"""
Beamforming Simulation Suite
A comprehensive OOP framework for comparing Bartlett, MUSIC, and MVDR beamforming algorithms
"""

import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional, Union
from multiprocessing import Pool, cpu_count
import time
from dataclasses import dataclass
from enum import Enum
import customtkinter as ctk
from gui.main_window import BeamformingApp


class BeamformingMethod(Enum):
    """Enumeration of beamforming methods"""
    BARTLETT = "bartlett"
    MUSIC = "music"
    MVDR = "mvdr"


@dataclass
class PerformanceMetrics:
    """Data class to store performance metrics"""
    resolution: float
    peak_to_sidelobe_ratio: float
    computation_time: float
    detection_accuracy: float
    false_alarm_rate: float


class ArrayGeometry(ABC):
    """Abstract base class for array geometries"""

    def __init__(self, num_elements: int):
        self.num_elements = num_elements
        self._positions = None

    @abstractmethod
    def get_positions(self) -> np.ndarray:
        """Return array element positions as (N, 3) array"""
        pass

    @property
    def positions(self) -> np.ndarray:
        if self._positions is None:
            self._positions = self.get_positions()
        return self._positions


class LinearArray(ArrayGeometry):
    """Linear array geometry"""

    def __init__(self, num_elements: int, spacing: float = 0.5):
        super().__init__(num_elements)
        self.spacing = spacing  # in wavelengths

    def get_positions(self) -> np.ndarray:
        """Generate linear array positions"""
        positions = np.zeros((self.num_elements, 3))
        positions[:, 0] = np.arange(self.num_elements) * self.spacing
        positions[:, 0] -= np.mean(positions[:, 0])  # Center the array
        return positions


class CircularArray(ArrayGeometry):
    """Circular array geometry"""

    def __init__(self, num_elements: int, radius: float = 1.0):
        super().__init__(num_elements)
        self.radius = radius  # in wavelengths

    def get_positions(self) -> np.ndarray:
        """Generate circular array positions"""
        angles = np.linspace(0, 2* np.pi, self.num_elements, endpoint=False)
        positions = np.zeros((self.num_elements, 3))
        positions[:, 0] = self.radius * np.cos(angles)
        positions[:, 1] = self.radius * np.sin(angles)
        return positions


class PlanarArray(ArrayGeometry):
    """Planar array geometry"""

    def __init__(self, rows: int, cols: int, row_spacing: float = 0.5, col_spacing: float = 0.5):
        super().__init__(rows * cols)
        self.rows = rows
        self.cols = cols
        self.row_spacing = row_spacing
        self.col_spacing = col_spacing

    def get_positions(self) -> np.ndarray:
        """Generate planar array positions"""
        positions = np.zeros((self.num_elements, 3))
        idx = 0
        for i in range(self.rows):
            for j in range(self.cols):
                positions[idx, 0] = j * self.col_spacing
                positions[idx, 1] = i * self.row_spacing
                idx += 1

        # Center the array
        positions[:, 0] -= np.mean(positions[:, 0])
        positions[:, 1] -= np.mean(positions[:, 1])
        return positions


class SignalEnvironment:
    """Class to manage signal sources and noise environment"""

    def __init__(self, frequency: float, c: float = 3e8):
        self.frequency = frequency
        self.c = c
        self.wavelength = c / frequency
        self.sources = []
        self.noise_power = 1.0

    def add_source(self, azimuth: float, elevation: float = 0.0, power: float = 1.0,
                   coherent: bool = False):
        """Add a signal source"""
        self.sources.append({
            'azimuth': np.deg2rad(azimuth),
            'elevation': np.deg2rad(elevation),
            'power': power,
            'coherent': coherent
        })

    def set_noise_power(self, power: float):
        """Set noise power level"""
        self.noise_power = power

    def generate_steering_vector(self, array: ArrayGeometry, azimuth: float,
                                 elevation: float = 0.0) -> np.ndarray:
        """Generate steering vector for given direction"""
        k = 2 * np.pi / self.wavelength

        # Direction cosines
        dx = np.sin(elevation) * np.cos(azimuth)
        dy = np.sin(elevation) * np.sin(azimuth)
        dz = np.cos(elevation)
        direction = np.array([dx, dy, dz])

        # Phase shifts
        phases = k * np.dot(array.positions, direction)
        return np.exp(1j * phases)

    def generate_data(self, array: ArrayGeometry, num_snapshots: int) -> np.ndarray:
        """Generate array data with sources and noise"""
        data = np.zeros((array.num_elements, num_snapshots), dtype=complex)

        # Add signal sources
        for source in self.sources:
            steering_vec = self.generate_steering_vector(
                array, source['azimuth'], source['elevation']
            )

            if source['coherent']:
                # Coherent signal
                signal = np.sqrt(source['power']) * np.ones(num_snapshots)
            else:
                # Random signal
                signal = np.sqrt(source['power']) * (
                        np.random.randn(num_snapshots) + 1j * np.random.randn(num_snapshots)
                ) / np.sqrt(2)

            data += np.outer(steering_vec, signal)

        # Add noise
        noise = np.sqrt(self.noise_power / 2) * (
                np.random.randn(array.num_elements, num_snapshots) +
                1j * np.random.randn(array.num_elements, num_snapshots)
        )
        data += noise

        return data


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
        self.covariance_matrix = np.cov(data)
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
            spectrum[i] = np.real(
                steering_vec.conj().T @ self.covariance_matrix @ steering_vec
            )

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
            denominator = steering_vec.conj().T @ noise_subspace @ noise_subspace.conj().T @ steering_vec
            spectrum[i] = 1.0 / np.real(denominator)

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
        R_inv = np.linalg.inv(
            self.covariance_matrix + self.diagonal_loading * np.eye(self.array.num_elements)
        )

        spectrum = np.zeros(len(scan_angles))

        for i, angle in enumerate(scan_angles):
            steering_vec = self.signal_env.generate_steering_vector(self.array, angle)
            denominator = steering_vec.conj().T @ R_inv @ steering_vec
            spectrum[i] = 1.0 / np.real(denominator)

        return spectrum


def compute_spectrum_parallel(args):
    """Helper function for parallel spectrum computation"""
    beamformer, data, angle_chunk = args
    return beamformer.compute_spectrum(data, angle_chunk)


class BeamformingSimulator:
    """Main simulation class that orchestrates beamforming comparisons"""

    def __init__(self, array: ArrayGeometry, signal_env: SignalEnvironment):
        self.array = array
        self.signal_env = signal_env
        self.beamformers = {}
        self.results = {}

    def add_beamformer(self, method: BeamformingMethod, **kwargs):
        """Add a beamformer to the simulation"""
        if method == BeamformingMethod.BARTLETT:
            self.beamformers[method] = BartlettBeamformer(self.array, self.signal_env)
        elif method == BeamformingMethod.MUSIC:
            num_sources = kwargs.get('num_sources', len(self.signal_env.sources))
            self.beamformers[method] = MUSICBeamformer(self.array, self.signal_env, num_sources)
        elif method == BeamformingMethod.MVDR:
            diagonal_loading = kwargs.get('diagonal_loading', 1e-6)
            self.beamformers[method] = MVDRBeamformer(self.array, self.signal_env, diagonal_loading)

    def run_simulation(self, num_snapshots: int = 1000, scan_range: Tuple[float, float] = (-90, 90),
                       scan_resolution: float = 1.0, use_multiprocessing: bool = True,
                       num_monte_carlo: int = 100) -> Dict:
        """Run beamforming simulation"""
        scan_angles = np.arange(scan_range[0], scan_range[1], scan_resolution)
        scan_angles_rad = np.deg2rad(scan_angles)

        results = {}

        for method, beamformer in self.beamformers.items():
            print(f"Running {method.value} simulation...")

            start_time = time.time()

            if use_multiprocessing and num_monte_carlo > 1:
                spectra = self._run_parallel_monte_carlo(
                    beamformer, num_snapshots, scan_angles_rad, num_monte_carlo
                )
            else:
                spectra = self._run_sequential_monte_carlo(
                    beamformer, num_snapshots, scan_angles_rad, num_monte_carlo
                )

            computation_time = time.time() - start_time

            # Average over Monte Carlo runs
            avg_spectrum = np.mean(spectra, axis=0)

            # Convert to dB
            spectrum_db = 10 * np.log10(avg_spectrum / np.max(avg_spectrum))

            # Compute performance metrics
            metrics = self._compute_metrics(spectrum_db, scan_angles, computation_time)

            results[method] = {
                'spectrum': spectrum_db,
                'scan_angles': scan_angles,
                'metrics': metrics,
                'raw_spectra': spectra
            }

        self.results = results
        return results

    def _run_parallel_monte_carlo(self, beamformer, num_snapshots, scan_angles, num_runs):
        """Run Monte Carlo simulation with multiprocessing"""
        with Pool(processes=min(cpu_count(), num_runs)) as pool:
            args_list = []
            for _ in range(num_runs):
                data = self.signal_env.generate_data(self.array, num_snapshots)
                args_list.append((beamformer, data, scan_angles))

            spectra = pool.map(compute_spectrum_parallel, args_list)

        return np.array(spectra)

    def _run_sequential_monte_carlo(self, beamformer, num_snapshots, scan_angles, num_runs):
        """Run Monte Carlo simulation sequentially"""
        spectra = []
        for _ in range(num_runs):
            data = self.signal_env.generate_data(self.array, num_snapshots)
            spectrum = beamformer.compute_spectrum(data, scan_angles)
            spectra.append(spectrum)

        return np.array(spectra)

    def _compute_metrics(self, spectrum_db, scan_angles, computation_time):
        """Compute performance metrics"""
        # Find peaks
        peaks = []
        for source in self.signal_env.sources:
            source_angle_deg = np.rad2deg(source['azimuth'])
            closest_idx = np.argmin(np.abs(scan_angles - source_angle_deg))
            peaks.append(closest_idx)

        # Resolution (3dB beamwidth)
        main_peak_idx = peaks[0] if peaks else np.argmax(spectrum_db)
        main_peak_val = spectrum_db[main_peak_idx]

        # Find 3dB points
        left_3db = right_3db = main_peak_idx
        for i in range(main_peak_idx, 0, -1):
            if spectrum_db[i] < main_peak_val - 3:
                left_3db = i
                break
        for i in range(main_peak_idx, len(spectrum_db)):
            if spectrum_db[i] < main_peak_val - 3:
                right_3db = i
                break

        resolution = scan_angles[right_3db] - scan_angles[left_3db]

        # Peak-to-sidelobe ratio
        sidelobe_mask = np.ones(len(spectrum_db), dtype=bool)
        for peak_idx in peaks:
            sidelobe_mask[max(0, peak_idx - 5):min(len(spectrum_db), peak_idx + 6)] = False

        if np.any(sidelobe_mask):
            max_sidelobe = np.max(spectrum_db[sidelobe_mask])
            pslr = main_peak_val - max_sidelobe
        else:
            pslr = np.inf

        # Detection accuracy (simplified)
        detected_peaks = []
        for i in range(1, len(spectrum_db) - 1):
            if (spectrum_db[i] > spectrum_db[i - 1] and
                    spectrum_db[i] > spectrum_db[i + 1] and
                    spectrum_db[i] > main_peak_val - 10):  # Within 10dB of main peak
                detected_peaks.append(i)

        detection_accuracy = min(len(detected_peaks) / len(self.signal_env.sources), 1.0)
        false_alarm_rate = max(0, len(detected_peaks) - len(self.signal_env.sources)) / len(scan_angles)

        return PerformanceMetrics(
            resolution=resolution,
            peak_to_sidelobe_ratio=pslr,
            computation_time=computation_time,
            detection_accuracy=detection_accuracy,
            false_alarm_rate=false_alarm_rate
        )

    def plot_results(self, save_path: Optional[str] = None):
        """Plot comparison results"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Spectrum comparison
        for method, result in self.results.items():
            ax1.plot(result['scan_angles'], result['spectrum'],
                     label=f"{method.value.upper()}", linewidth=2)

        ax1.set_xlabel('Azimuth (degrees)')
        ax1.set_ylabel('Normalized Power (dB)')
        ax1.set_title('Beamforming Spectrum Comparison')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_ylim([-60, 5])

        # Performance metrics bar chart
        methods = list(self.results.keys())
        metrics_names = ['Resolution', 'PSLR', 'Detection Acc.', 'Comp. Time']

        resolution_vals = [self.results[m]['metrics'].resolution for m in methods]
        pslr_vals = [self.results[m]['metrics'].peak_to_sidelobe_ratio for m in methods]
        detection_vals = [self.results[m]['metrics'].detection_accuracy for m in methods]
        time_vals = [self.results[m]['metrics'].computation_time for m in methods]

        x = np.arange(len(methods))
        width = 0.2

        ax2.bar(x - 1.5 * width, resolution_vals, width, label='Resolution (deg)', alpha=0.8)
        ax2.bar(x - 0.5 * width, np.array(pslr_vals) / 10, width, label='PSLR/10 (dB)', alpha=0.8)
        ax2.bar(x + 0.5 * width, detection_vals, width, label='Detection Acc.', alpha=0.8)
        ax2.bar(x + 1.5 * width, np.array(time_vals) * 10, width, label='Time*10 (s)', alpha=0.8)

        ax2.set_xlabel('Beamforming Method')
        ax2.set_ylabel('Normalized Metrics')
        ax2.set_title('Performance Metrics Comparison')
        ax2.set_xticks(x)
        ax2.set_xticklabels([m.value.upper() for m in methods])
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Array geometry
        positions = self.array.positions
        ax3.scatter(positions[:, 0], positions[:, 1], s=100, c='red', marker='o')
        ax3.set_xlabel('X (wavelengths)')
        ax3.set_ylabel('Y (wavelengths)')
        ax3.set_title('Array Geometry')
        ax3.grid(True, alpha=0.3)
        ax3.axis('equal')

        # Source positions
        for i, source in enumerate(self.signal_env.sources):
            angle = np.rad2deg(source['azimuth'])
            ax3.arrow(0, 0, 2 * np.cos(source['azimuth']), 2 * np.sin(source['azimuth']),
                      head_width=0.1, head_length=0.1, fc='blue', ec='blue')
            ax3.text(2.2 * np.cos(source['azimuth']), 2.2 * np.sin(source['azimuth']),
                     f'S{i + 1}: {angle:.1f}°', ha='center', va='center')

        # Computation time comparison
        methods_str = [m.value.upper() for m in methods]
        ax4.bar(methods_str, time_vals, alpha=0.8, color=['blue', 'red', 'green'][:len(methods)])
        ax4.set_xlabel('Beamforming Method')
        ax4.set_ylabel('Computation Time (s)')
        ax4.set_title('Computational Efficiency')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        plt.show()

    def generate_report(self) -> str:
        """Generate a performance comparison report"""
        report = "BEAMFORMING ALGORITHM COMPARISON REPORT\n"
        report += "=" * 50 + "\n\n"

        report += f"Array Configuration: {type(self.array).__name__}\n"
        report += f"Number of Elements: {self.array.num_elements}\n"
        report += f"Number of Sources: {len(self.signal_env.sources)}\n"
        report += f"Frequency: {self.signal_env.frequency / 1e9:.2f} GHz\n\n"

        for method, result in self.results.items():
            metrics = result['metrics']
            report += f"{method.value.upper()} BEAMFORMER:\n"
            report += f"  Resolution (3dB BW): {metrics.resolution:.2f}°\n"
            report += f"  Peak-to-Sidelobe Ratio: {metrics.peak_to_sidelobe_ratio:.2f} dB\n"
            report += f"  Detection Accuracy: {metrics.detection_accuracy:.2f}\n"
            report += f"  False Alarm Rate: {metrics.false_alarm_rate:.4f}\n"
            report += f"  Computation Time: {metrics.computation_time:.4f} s\n\n"

        # Recommendations
        best_resolution = min(self.results.items(),
                              key=lambda x: x[1]['metrics'].resolution)
        best_pslr = max(self.results.items(),
                        key=lambda x: x[1]['metrics'].peak_to_sidelobe_ratio)
        fastest = min(self.results.items(),
                      key=lambda x: x[1]['metrics'].computation_time)

        report += "RECOMMENDATIONS:\n"
        report += f"  Best Resolution: {best_resolution[0].value.upper()}\n"
        report += f"  Best PSLR: {best_pslr[0].value.upper()}\n"
        report += f"  Fastest: {fastest[0].value.upper()}\n"

        return report


def main():
    """Main entry point for the application"""
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create and run the application
    app = BeamformingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
