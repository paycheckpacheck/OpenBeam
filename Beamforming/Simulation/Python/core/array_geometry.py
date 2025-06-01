"""
Array geometry implementations for beamforming simulation
"""

import numpy as np
from abc import ABC, abstractmethod


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
        angles = np.linspace(0, 2 * np.pi, self.num_elements, endpoint=False)
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