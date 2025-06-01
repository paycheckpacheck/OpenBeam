"""
Testbench for Uniform Linear Array (ULA) beamforming
"""

import numpy as np
import matplotlib.pyplot as plt
from core.array_geometry import LinearArray
from core.signal_environment import SignalEnvironment
from core.simulator import BeamformingSimulator, BeamformingMethod


def test_ula_beamforming():
    # Array parameters
    num_elements = 16
    spacing = 0.5  # half-wavelength spacing
    frequency = 2.45  # 2.45 GHz

    # Create ULA
    array = LinearArray(num_elements=num_elements, spacing=spacing)

    # Create signal environment
    signal_env = SignalEnvironment(frequency=frequency)
    
    # Add desired signal sources
    signal_env.add_source(azimuth=30, power=10)  # Main source at 30 degrees
    signal_env.add_source(azimuth=-45, power=5)  # Secondary source at -45 degrees
    
    # Add interferer
    signal_env.add_source(azimuth=60, power=8, coherent=True, is_interferer=True)  # Interferer at 60 degrees
    
    # Set noise power
    signal_env.set_noise_power(power=0.1)

    # Create simulator
    simulator = BeamformingSimulator(array, signal_env)

    # Add all beamformers
    simulator.add_beamformer(BeamformingMethod.BARTLETT)
    #simulator.add_beamformer(BeamformingMethod.MUSIC, num_sources=2)  # We know there are 2 desired sources
    #simulator.add_beamformer(BeamformingMethod.MVDR, diagonal_loading=1e-6)

    # Run simulation
    results = simulator.run_simulation(
        num_snapshots=1000,
        scan_range=(-90, 90),
        scan_resolution=1.0,
        use_multiprocessing=True,
        num_monte_carlo=10
    )

    # Plot results
    plt.figure(figsize=(15, 10))

    # Plot spectrum comparison
    plt.subplot(2, 1, 1)
    for method, result in results.items():
        plt.plot(result['scan_angles'], result['spectrum'],
                label=f"{method.value.upper()}", linewidth=2)

    # Mark source locations
    for source in signal_env.sources:
        plt.axvline(x=np.rad2deg(source['azimuth']), color='k', linestyle='--', alpha=0.5)
        plt.text(np.rad2deg(source['azimuth']), -5, f"{np.rad2deg(source['azimuth']):.1f}°",
                rotation=90, va='top')

    plt.xlabel('Azimuth (degrees)')
    plt.ylabel('Normalized Power (dB)')
    plt.title('ULA Beamforming Spectrum Comparison')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim([-60, 5])

    # Plot array geometry
    plt.subplot(2, 1, 2)
    positions = array.positions
    plt.scatter(positions[:, 0], positions[:, 1], s=100, c='red', marker='o')
    
    # Plot source directions
    for i, source in enumerate(signal_env.sources):
        angle = np.rad2deg(source['azimuth'])
        plt.arrow(0, 0, 2 * np.cos(source['azimuth']), 2 * np.sin(source['azimuth']),
                 head_width=0.1, head_length=0.1, fc='blue', ec='blue')
        plt.text(2.2 * np.cos(source['azimuth']), 2.2 * np.sin(source['azimuth']),
                f'S{i + 1}: {angle:.1f}°', ha='center', va='center')

    plt.xlabel('X (wavelengths)')
    plt.ylabel('Y (wavelengths)')
    plt.title('ULA Geometry and Source Directions')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')

    plt.tight_layout()
    plt.show()

    # Print performance report
    print(simulator.generate_report())


if __name__ == "__main__":
    test_ula_beamforming() 