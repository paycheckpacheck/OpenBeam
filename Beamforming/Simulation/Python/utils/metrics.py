"""
Performance metrics for beamforming evaluation
"""

from dataclasses import dataclass
import numpy as np
from typing import List, Dict


@dataclass
class PerformanceMetrics:
    """Data class to store performance metrics"""
    resolution: float
    peak_to_sidelobe_ratio: float
    detection_accuracy: float
    false_alarm_rate: float


def compute_metrics(spectrum_db: np.ndarray, scan_angles: np.ndarray,
                   source_angles: List[float], computation_time: float) -> PerformanceMetrics:
    """Compute performance metrics for beamforming results"""
    # Find peaks
    peaks = []
    for source_angle in source_angles:
        closest_idx = np.argmin(np.abs(scan_angles - source_angle))
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

    # Detection accuracy
    detected_peaks = []
    for i in range(1, len(spectrum_db) - 1):
        if (spectrum_db[i] > spectrum_db[i - 1] and
                spectrum_db[i] > spectrum_db[i + 1] and
                spectrum_db[i] > main_peak_val - 10):  # Within 10dB of main peak
            detected_peaks.append(i)

    detection_accuracy = min(len(detected_peaks) / len(source_angles), 1.0)
    false_alarm_rate = max(0, len(detected_peaks) - len(source_angles)) / len(scan_angles)

    return PerformanceMetrics(
        resolution=resolution,
        peak_to_sidelobe_ratio=pslr,
        detection_accuracy=detection_accuracy,
        false_alarm_rate=false_alarm_rate
    ) 