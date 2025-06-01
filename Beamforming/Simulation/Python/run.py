"""
Entry point for the Beamforming Simulation Suite
"""

import customtkinter as ctk
from gui.main_window import BeamformingApp


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