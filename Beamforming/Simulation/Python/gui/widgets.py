"""
Custom widgets for the beamforming GUI
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from typing import Callable, List, Dict, Optional


class SourceFrame(ctk.CTkFrame):
    """Frame for managing signal sources"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.sources = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        # Title
        self.title = ctk.CTkLabel(self, text="Signal Sources", font=("Arial", 16, "bold"))
        self.title.pack(pady=10)

        # Source list
        self.source_list = ctk.CTkTextbox(self, height=150)
        self.source_list.pack(padx=10, pady=5, fill="x")

        # Add source frame
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(padx=10, pady=5, fill="x")

        # Azimuth
        ctk.CTkLabel(add_frame, text="Azimuth (°):").pack(side="left", padx=5)
        self.azimuth_entry = ctk.CTkEntry(add_frame, width=60)
        self.azimuth_entry.pack(side="left", padx=5)

        # Power
        ctk.CTkLabel(add_frame, text="Power:").pack(side="left", padx=5)
        self.power_entry = ctk.CTkEntry(add_frame, width=60)
        self.power_entry.pack(side="left", padx=5)

        # Add button
        self.add_btn = ctk.CTkButton(add_frame, text="Add Source", command=self.add_source)
        self.add_btn.pack(side="left", padx=5)

        # Interferer checkbox
        self.is_interferer = ctk.CTkCheckBox(add_frame, text="Is Interferer")
        self.is_interferer.pack(side="left", padx=5)

    def add_source(self):
        """Add a new source"""
        try:
            azimuth = float(self.azimuth_entry.get())
            power = float(self.power_entry.get())
            is_interferer = self.is_interferer.get()

            source = {
                'azimuth': azimuth,
                'power': power,
                'is_interferer': is_interferer
            }
            self.sources.append(source)
            self.update_source_list()

            # Clear entries
            self.azimuth_entry.delete(0, "end")
            self.power_entry.delete(0, "end")
            self.is_interferer.deselect()

        except ValueError:
            print("Invalid input values")

    def update_source_list(self):
        """Update the source list display"""
        self.source_list.delete("1.0", "end")
        for i, source in enumerate(self.sources):
            source_type = "Interferer" if source['is_interferer'] else "Source"
            self.source_list.insert("end", 
                f"{source_type} {i+1}: Azimuth={source['azimuth']}°, Power={source['power']}\n")


class ArrayConfigFrame(ctk.CTkFrame):
    """Frame for array configuration"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        # Title
        self.title = ctk.CTkLabel(self, text="Array Configuration", font=("Arial", 16, "bold"))
        self.title.pack(pady=10)

        # Array type
        type_frame = ctk.CTkFrame(self)
        type_frame.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(type_frame, text="Array Type:").pack(side="left", padx=5)
        self.array_type = ctk.CTkOptionMenu(type_frame, 
                                          values=["Linear", "Circular", "Planar"])
        self.array_type.pack(side="left", padx=5)

        # Parameters frame
        self.params_frame = ctk.CTkFrame(self)
        self.params_frame.pack(padx=10, pady=5, fill="x")

        # Update parameters when array type changes
        self.array_type.configure(command=self.update_params)

        # Initial parameters
        self.update_params()

    def update_params(self, *args):
        """Update parameter inputs based on array type"""
        # Clear existing widgets
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        array_type = self.array_type.get()

        if array_type == "Linear":
            ctk.CTkLabel(self.params_frame, text="Number of Elements:").pack(side="left", padx=5)
            self.num_elements = ctk.CTkEntry(self.params_frame, width=60)
            self.num_elements.pack(side="left", padx=5)
            self.num_elements.insert(0, "16")

            ctk.CTkLabel(self.params_frame, text="Spacing (λ):").pack(side="left", padx=5)
            self.spacing = ctk.CTkEntry(self.params_frame, width=60)
            self.spacing.pack(side="left", padx=5)
            self.spacing.insert(0, "0.5")

        elif array_type == "Circular":
            ctk.CTkLabel(self.params_frame, text="Number of Elements:").pack(side="left", padx=5)
            self.num_elements = ctk.CTkEntry(self.params_frame, width=60)
            self.num_elements.pack(side="left", padx=5)
            self.num_elements.insert(0, "12")

            ctk.CTkLabel(self.params_frame, text="Radius (λ):").pack(side="left", padx=5)
            self.radius = ctk.CTkEntry(self.params_frame, width=60)
            self.radius.pack(side="left", padx=5)
            self.radius.insert(0, "1.0")

        elif array_type == "Planar":
            ctk.CTkLabel(self.params_frame, text="Rows:").pack(side="left", padx=5)
            self.rows = ctk.CTkEntry(self.params_frame, width=60)
            self.rows.pack(side="left", padx=5)
            self.rows.insert(0, "4")

            ctk.CTkLabel(self.params_frame, text="Columns:").pack(side="left", padx=5)
            self.cols = ctk.CTkEntry(self.params_frame, width=60)
            self.cols.pack(side="left", padx=5)
            self.cols.insert(0, "4")

            ctk.CTkLabel(self.params_frame, text="Row Spacing (λ):").pack(side="left", padx=5)
            self.row_spacing = ctk.CTkEntry(self.params_frame, width=60)
            self.row_spacing.pack(side="left", padx=5)
            self.row_spacing.insert(0, "0.5")

            ctk.CTkLabel(self.params_frame, text="Col Spacing (λ):").pack(side="left", padx=5)
            self.col_spacing = ctk.CTkEntry(self.params_frame, width=60)
            self.col_spacing.pack(side="left", padx=5)
            self.col_spacing.insert(0, "0.5")


class SimulationConfigFrame(ctk.CTkFrame):
    """Frame for simulation configuration"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        # Title
        self.title = ctk.CTkLabel(self, text="Simulation Parameters", font=("Arial", 16, "bold"))
        self.title.pack(pady=10)

        # Parameters frame
        params_frame = ctk.CTkFrame(self)
        params_frame.pack(padx=10, pady=5, fill="x")

        # Frequency
        ctk.CTkLabel(params_frame, text="Frequency (GHz):").pack(side="left", padx=5)
        self.frequency = ctk.CTkEntry(params_frame, width=60)
        self.frequency.pack(side="left", padx=5)
        self.frequency.insert(0, "2.45")

        # Snapshots
        ctk.CTkLabel(params_frame, text="Snapshots:").pack(side="left", padx=5)
        self.snapshots = ctk.CTkEntry(params_frame, width=60)
        self.snapshots.pack(side="left", padx=5)
        self.snapshots.insert(0, "100")

        # Monte Carlo runs
        ctk.CTkLabel(params_frame, text="Monte Carlo:").pack(side="left", padx=5)
        self.monte_carlo = ctk.CTkEntry(params_frame, width=60)
        self.monte_carlo.pack(side="left", padx=5)
        self.monte_carlo.insert(0, "10")

        # Scan range
        range_frame = ctk.CTkFrame(self)
        range_frame.pack(padx=10, pady=5, fill="x")

        ctk.CTkLabel(range_frame, text="Scan Range:").pack(side="left", padx=5)
        self.scan_min = ctk.CTkEntry(range_frame, width=60)
        self.scan_min.pack(side="left", padx=5)
        self.scan_min.insert(0, "-90")

        ctk.CTkLabel(range_frame, text="to").pack(side="left", padx=5)
        self.scan_max = ctk.CTkEntry(range_frame, width=60)
        self.scan_max.pack(side="left", padx=5)
        self.scan_max.insert(0, "90")

        ctk.CTkLabel(range_frame, text="Resolution:").pack(side="left", padx=5)
        self.scan_res = ctk.CTkEntry(range_frame, width=60)
        self.scan_res.pack(side="left", padx=5)
        self.scan_res.insert(0, "1.0")


class ResultsFrame(ctk.CTkFrame):
    """Frame for displaying simulation results"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        # Title
        self.title = ctk.CTkLabel(self, text="Simulation Results", font=("Arial", 16, "bold"))
        self.title.pack(pady=10)

        # Create figure for plots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # Initialize plots
        self.ax1.set_title("Beamforming Spectrum")
        self.ax1.set_xlabel("Azimuth (degrees)")
        self.ax1.set_ylabel("Normalized Power (dB)")
        self.ax1.grid(True)

        self.ax2.set_title("Array Geometry")
        self.ax2.set_xlabel("X (wavelengths)")
        self.ax2.set_ylabel("Y (wavelengths)")
        self.ax2.grid(True)
        self.ax2.axis('equal')

    def update_plots(self, results: Dict, array_positions: np.ndarray, source_angles: List[float]):
        """Update the plots with new results"""
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()

        # Plot spectrum
        for method, result in results.items():
            self.ax1.plot(result['scan_angles'], result['spectrum'],
                         label=method.value.upper(), linewidth=2)

        self.ax1.set_title("Beamforming Spectrum")
        self.ax1.set_xlabel("Azimuth (degrees)")
        self.ax1.set_ylabel("Normalized Power (dB)")
        self.ax1.grid(True)
        self.ax1.legend()
        self.ax1.set_ylim([-60, 5])

        # Plot array geometry
        self.ax2.scatter(array_positions[:, 0], array_positions[:, 1],
                        s=100, c='red', marker='o')
        
        # Plot source directions
        for angle in source_angles:
            angle_rad = np.deg2rad(angle)
            self.ax2.arrow(0, 0, 2 * np.cos(angle_rad), 2 * np.sin(angle_rad),
                          head_width=0.1, head_length=0.1, fc='blue', ec='blue')
            self.ax2.text(2.2 * np.cos(angle_rad), 2.2 * np.sin(angle_rad),
                         f'{angle:.1f}°', ha='center', va='center')

        self.ax2.set_title("Array Geometry")
        self.ax2.set_xlabel("X (wavelengths)")
        self.ax2.set_ylabel("Y (wavelengths)")
        self.ax2.grid(True)
        self.ax2.axis('equal')

        # Update canvas
        self.canvas.draw() 