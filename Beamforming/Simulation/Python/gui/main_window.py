"""
Main window for the beamforming GUI application
"""

import customtkinter as ctk
import numpy as np
from typing import Dict, List, Optional

from core.array_geometry import LinearArray, CircularArray, PlanarArray
from core.signal_environment import SignalEnvironment
from core.simulator import BeamformingSimulator, BeamformingMethod
from .widgets import SourceFrame, ArrayConfigFrame, SimulationConfigFrame, ResultsFrame


class BeamformingApp(ctk.CTk):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Beamforming Simulation Suite")
        self.geometry("1200x800")

        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create left and right frames
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Create widgets
        self.source_frame = SourceFrame(self.left_frame)
        self.source_frame.pack(fill="x", padx=5, pady=5)

        self.array_frame = ArrayConfigFrame(self.left_frame)
        self.array_frame.pack(fill="x", padx=5, pady=5)

        self.sim_frame = SimulationConfigFrame(self.left_frame)
        self.sim_frame.pack(fill="x", padx=5, pady=5)

        self.results_frame = ResultsFrame(self.right_frame)
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Add run button
        self.run_button = ctk.CTkButton(
            self.left_frame,
            text="Run Simulation",
            command=self.run_simulation,
            height=40
        )
        self.run_button.pack(pady=10)

    def create_array(self) -> Optional[LinearArray | CircularArray | PlanarArray]:
        """Create array based on configuration"""
        array_type = self.array_frame.array_type.get()

        try:
            if array_type == "Linear":
                num_elements = int(self.array_frame.num_elements.get())
                spacing = float(self.array_frame.spacing.get())
                return LinearArray(num_elements, spacing)

            elif array_type == "Circular":
                num_elements = int(self.array_frame.num_elements.get())
                radius = float(self.array_frame.radius.get())
                return CircularArray(num_elements, radius)

            elif array_type == "Planar":
                rows = int(self.array_frame.rows.get())
                cols = int(self.array_frame.cols.get())
                row_spacing = float(self.array_frame.row_spacing.get())
                col_spacing = float(self.array_frame.col_spacing.get())
                return PlanarArray(rows, cols, row_spacing, col_spacing)

        except ValueError:
            print("Invalid array parameters")
            return None

    def run_simulation(self):
        """Run the beamforming simulation"""
        # Create array
        array = self.create_array()
        if array is None:
            return

        # Create signal environment
        freq = float(self.sim_frame.frequency.get()) * 1e9  # Convert to Hz
        signal_env = SignalEnvironment(frequency=freq)

        # Add sources and interferers
        for source in self.source_frame.sources:
            signal_env.add_source(
                azimuth=source['azimuth'],
                power=source['power'],
                is_interferer=source['is_interferer']
            )

        # Create simulator
        simulator = BeamformingSimulator(array, signal_env)

        # Add beamformers
        simulator.add_beamformer(BeamformingMethod.BARTLETT)
        simulator.add_beamformer(BeamformingMethod.MUSIC, num_sources=len(signal_env.sources))
        simulator.add_beamformer(BeamformingMethod.MVDR, diagonal_loading=1e-4)

        # Run simulation
        results = simulator.run_simulation(
            num_snapshots=int(self.sim_frame.snapshots.get()),
            scan_range=(
                float(self.sim_frame.scan_min.get()),
                float(self.sim_frame.scan_max.get())
            ),
            scan_resolution=float(self.sim_frame.scan_res.get()),
            num_monte_carlo=int(self.sim_frame.monte_carlo.get())
        )

        # Update plots
        self.results_frame.update_plots(
            results,
            array.positions,
            signal_env.get_source_angles()
        )

        # Print report
        print(simulator.generate_report()) 