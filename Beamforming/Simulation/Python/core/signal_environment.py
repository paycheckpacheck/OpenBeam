"""
Signal environment implementation for beamforming simulation
"""

import numpy as np
from typing import List, Dict, Optional
from core.array_geometry import ArrayGeometry


class SignalEnvironment:
    """Class to manage signal sources and noise environment"""

    def __init__(self, frequency: float, c: float = 3e8):
        self.frequency = frequency * 1e9  # Convert to Hz
        self.c = c
        self.wavelength = c / self.frequency
        self.sources = []
        self.interferers = []  # Separate list for interferers
        self.noise_power = 1.0

    def add_source(self, azimuth: float, elevation: float = 0.0, power: float = 1.0,
                  coherent: bool = False, is_interferer: bool = False):
        """Add a signal source or interferer"""
        source = {
            'azimuth': np.deg2rad(azimuth),
            'elevation': np.deg2rad(elevation),
            'power': power,
            'coherent': coherent
        }
        
        if is_interferer:
            self.interferers.append(source)
        else:
            self.sources.append(source)

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
        steering_vec = np.exp(1j * phases)
        
        # Normalize steering vector
        return steering_vec / np.sqrt(np.sum(np.abs(steering_vec)**2))

    def generate_data(self, array: ArrayGeometry, num_snapshots: int) -> np.ndarray:
        """Generate array data with sources, interferers, and noise"""
        data = np.zeros((array.num_elements, num_snapshots), dtype=complex)

        # Add desired signal sources
        for source in self.sources:
            steering_vec = self.generate_steering_vector(
                array, source['azimuth'], source['elevation']
            )

            if source['coherent']:
                # Coherent signal (constant phase)
                signal = np.sqrt(source['power']) * np.ones(num_snapshots)
            else:
                # Random signal (random phase)
                signal = np.sqrt(source['power']) * (
                    np.random.randn(num_snapshots) + 1j * np.random.randn(num_snapshots)
                ) / np.sqrt(2)

            data += np.outer(steering_vec, signal)

        # Add interferers
        for interferer in self.interferers:
            steering_vec = self.generate_steering_vector(
                array, interferer['azimuth'], interferer['elevation']
            )

            if interferer['coherent']:
                # Coherent interferer
                signal = np.sqrt(interferer['power']) * np.ones(num_snapshots)
            else:
                # Random interferer
                signal = np.sqrt(interferer['power']) * (
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

    def get_source_angles(self) -> List[float]:
        """Get list of source angles in degrees"""
        return [np.rad2deg(source['azimuth']) for source in self.sources]

    def get_interferer_angles(self) -> List[float]:
        """Get list of interferer angles in degrees"""
        return [np.rad2deg(interferer['azimuth']) for interferer in self.interferers] 