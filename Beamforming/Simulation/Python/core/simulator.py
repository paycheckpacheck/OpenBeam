"""
Beamforming simulation orchestrator
"""

import numpy as np
import time
from typing import Dict, Tuple, Optional
from multiprocessing import Pool, cpu_count
from enum import Enum

from core.array_geometry import ArrayGeometry
from core.signal_environment import SignalEnvironment
from core.beamformers import BartlettBeamformer, MUSICBeamformer, MVDRBeamformer
from utils.metrics import compute_metrics


class BeamformingMethod(Enum):
    """Enumeration of beamforming methods"""
    BARTLETT = "bartlett"
    MUSIC = "music"
    MVDR = "mvdr"


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
            metrics = compute_metrics(
                spectrum_db, scan_angles,
                self.signal_env.get_source_angles(),
                computation_time
            )

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

    def generate_report(self) -> str:
        """Generate a performance comparison report"""
        report = "BEAMFORMING ALGORITHM COMPARISON REPORT\n"
        report += "=" * 50 + "\n\n"

        report += f"Array Configuration: {type(self.array).__name__}\n"
        report += f"Number of Elements: {self.array.num_elements}\n"
        report += f"Number of Sources: {len(self.signal_env.sources)}\n"
        report += f"Number of Interferers: {len(self.signal_env.interferers)}\n"
        report += f"Frequency: {self.signal_env.frequency / 1e9:.2f} GHz\n\n"

        for method, result in self.results.items():
            metrics = result['metrics']
            report += f"{method.value.upper()} BEAMFORMER:\n"
            report += f"  Resolution (3dB BW): {metrics.resolution:.2f}°\n"
            report += f"  Peak-to-Sidelobe Ratio: {metrics.peak_to_sidelobe_ratio:.2f} dB\n"
            report += f"  Detection Accuracy: {metrics.detection_accuracy:.2f}\n"
            report += f"  False Alarm Rate: {metrics.false_alarm_rate:.4f}\n\n"

        # Recommendations
        best_resolution = min(self.results.items(),
                            key=lambda x: x[1]['metrics'].resolution)
        best_pslr = max(self.results.items(),
                       key=lambda x: x[1]['metrics'].peak_to_sidelobe_ratio)

        report += "RECOMMENDATIONS:\n"
        report += f"  Best Resolution: {best_resolution[0].value.upper()}\n"
        report += f"  Best PSLR: {best_pslr[0].value.upper()}\n"

        return report 