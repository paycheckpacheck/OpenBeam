"""
Beamforming algorithm implementations
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional
from core.array_geometry import ArrayGeometry
from core.signal_environment import SignalEnvironment


class BeamformerBase(ABC):
    """Abstract base class for beamforming algorithms"""

    def __init__(self, array: ArrayGeometry, signal_env: SignalEnvironment):
        self.array = array
        self.signal_env = signal_env
        self.covariance_matrix = None
        self.eigenvalues = None
        self.eigenvectors = None

    def estimate_covariance(self, data: np.ndarray) -> np.ndarray:
        """Estimate spatial covariance matrix"""
        # Use sample covariance matrix
        self.covariance_matrix = np.cov(data) + np.eye(np.size(self.array))
        return self.covariance_matrix

    def eigendecomposition(self):
        """Perform eigendecomposition of covariance matrix"""
        if self.covariance_matrix is None:
            raise ValueError("Covariance matrix not estimated")

        self.eigenvalues, self.eigenvectors = np.linalg.eigh(self.covariance_matrix)
        # Sort in descending order
        idx = np.argsort(self.eigenvalues)[::-1]
        self.eigenvalues = self.eigenvalues[idx]
        self.eigenvectors = self.eigenvectors[:, idx]

    def normalize_steering_vector(self, steering_vec: np.ndarray) -> np.ndarray:
        """Normalize steering vector to unit norm"""
        return steering_vec / np.sqrt(np.sum(np.abs(steering_vec)**2))

    @abstractmethod
    def beamform(self, scan_angles: np.ndarray) -> np.ndarray:
        """Perform beamforming over scan angles"""
        pass

    def compute_spectrum(self, data: np.ndarray, scan_angles: np.ndarray) -> np.ndarray:
        """Compute beamforming spectrum"""
        self.estimate_covariance(data)
        return self.beamform(scan_angles)


class BartlettBeamformer(BeamformerBase):
    """Bartlett (conventional) beamformer"""

    def beamform(self, scan_angles: np.ndarray) -> np.ndarray:
        """Bartlett beamforming"""
        spectrum = np.zeros(len(scan_angles))

        for i, angle in enumerate(scan_angles):
            steering_vec = self.signal_env.generate_steering_vector(self.array, angle)
            
            # Bartlett spectrum
            spectrum[i] = np.real(
                steering_vec.conj().T @ self.covariance_matrix @ steering_vec
            )

        # Normalize spectrum
        spectrum = spectrum / np.max(spectrum)
        return spectrum


class MUSICBeamformer(BeamformerBase):
    """MUSIC (Multiple Signal Classification) beamformer"""

    def __init__(self, array: ArrayGeometry, signal_env: SignalEnvironment, num_sources: int):
        super().__init__(array, signal_env)
        self.num_sources = num_sources

    def beamform(self, scan_angles: np.ndarray) -> np.ndarray:
        """MUSIC beamforming"""
        self.eigendecomposition()

        # Noise subspace
        noise_subspace = self.eigenvectors[:, self.num_sources:]

        spectrum = np.zeros(len(scan_angles))

        for i, angle in enumerate(scan_angles):
            steering_vec = self.signal_env.generate_steering_vector(self.array, angle)
            
            # MUSIC spectrum
            denominator = steering_vec.conj().T @ noise_subspace @ noise_subspace.conj().T @ steering_vec
            spectrum[i] = 1.0 / np.real(denominator)

        # Normalize spectrum
        spectrum = spectrum / np.max(spectrum)
        return spectrum


class MVDRBeamformer(BeamformerBase):
    """MVDR (Minimum Variance Distortionless Response) beamformer"""

    def __init__(self, array: ArrayGeometry, signal_env: SignalEnvironment,
                 diagonal_loading: float = 1e-6):
        super().__init__(array, signal_env)
        self.diagonal_loading = diagonal_loading

    def beamform(self, scan_angles: np.ndarray) -> np.ndarray:
        """MVDR beamforming"""
        # Add diagonal loading for numerical stability
        R = self.covariance_matrix + self.diagonal_loading * np.eye(self.array.num_elements)
        R_inv = np.linalg.inv(R)

        spectrum = np.zeros(len(scan_angles))

        for i, angle in enumerate(scan_angles):
            steering_vec = self.signal_env.generate_steering_vector(self.array, angle)
            
            # MVDR spectrum
            denominator = steering_vec.conj().T @ R_inv @ steering_vec
            spectrum[i] = 1.0 / np.real(denominator)

        # Normalize spectrum
        spectrum = spectrum / np.max(spectrum)
        return spectrum 