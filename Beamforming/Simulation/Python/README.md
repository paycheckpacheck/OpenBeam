# Beamforming Simulation Suite

A comprehensive GUI application for comparing Bartlett, MUSIC, and MVDR beamforming algorithms in the presence of interferers.

## Features

- Interactive GUI for configuring array geometry, signal sources, and simulation parameters
- Support for linear, circular, and planar array geometries
- Implementation of three beamforming algorithms:
  - Bartlett (Conventional)
  - MUSIC (Multiple Signal Classification)
  - MVDR (Minimum Variance Distortionless Response)
- Real-time visualization of beamforming results
- Performance metrics calculation and reporting
- Support for multiple signal sources and interferers


2. Configure the simulation:
   - Select array type and parameters
   - Add signal sources and interferers
   - Set simulation parameters (frequency, snapshots, etc.)

3. Click "Run Simulation" to start the simulation

4. View results:
   - Beamforming spectrum plot
   - Array geometry visualization
   - Performance metrics in the console

## Example Configuration

1. Array Configuration:
   - Type: Linear
   - Elements: 16
   - Spacing: 0.5λ

2. Signal Sources:
   - Source 1: 30° azimuth, power = 10
   - Source 2: -45° azimuth, power = 5
   - Interferer: 60° azimuth, power = 8

3. Simulation Parameters:
   - Frequency: 2.45 GHz
   - Snapshots: 100
   - Monte Carlo runs: 10
   - Scan range: -90° to 90°
   - Resolution: 1°

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
