import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D


class AdaptiveBeamformer:
    def __init__(self, frequency, array_shape='linear', num_elements=8, custom_positions=None):
        """

        Parameters:
        - frequency: Operating frequency in Hz
        - array_shape: 'linear', 'circular', 'rectangular', 'l_shape', or 'custom'
        - num_elements: Number of array elements (ignored for custom)
        - custom_positions: Nx3 array of [x,y,z] positions for custom arrays
        """
        self.frequency = frequency
        self.c = 3e8  # Speed of light
        self.wavelength = self.c / frequency
        self.d = self.wavelength / 2  # Element spacing
        self.array_shape = array_shape
        self.num_elements = num_elements
        self.k = 2 * np.pi / self.wavelength  # Wave number

        # Generate array geometry
        self.element_positions = self._generate_array_geometry(custom_positions)
        self.Nr = len(self.element_positions)

        print(f"Frequency: {frequency / 1e6:.1f} MHz")
        print(f"Wavelength: {self.wavelength:.3f} m")
        print(f"Element spacing: {self.d:.3f} m")
        print(f"Array shape: {array_shape}")
        print(f"Number of elements: {self.Nr}")

    def _generate_array_geometry(self, custom_positions):
        """Generate array element positions based on specified geometry"""


        # Make a uniform linekar array
        if self.array_shape == 'linear':
            positions = np.array([[i * self.d, 0, 0] for i in range(self.num_elements)])


        # uniform ciruclar arrat
        elif self.array_shape == 'circular':
            radius = self.num_elements * self.d / (2 * np.pi)
            angles = np.linspace(0, 2 * np.pi, self.num_elements, endpoint=False)
            positions = np.array([[radius * np.cos(a), radius * np.sin(a), 0] for a in angles])

        # unfirom rectangular arry
        elif self.array_shape == 'rectangular':
            rows = int(np.sqrt(self.num_elements))
            cols = int(np.ceil(self.num_elements / rows))
            positions = []
            for i in range(rows):
                for j in range(cols):
                    if len(positions) < self.num_elements:
                        positions.append([j * self.d, i * self.d, 0])
            positions = np.array(positions)
        # kinda shitt
        elif self.array_shape == 'l_shape':
            # L-shaped array
            positions = []
            # Horizontal arm
            for i in range(self.num_elements // 2):
                positions.append([i * self.d, 0, 0])
            # Vertical arm
            for i in range(1, self.num_elements - self.num_elements // 2 + 1):
                positions.append([0, i * self.d, 0])
            positions = np.array(positions)

        # user gives custom array
        elif self.array_shape == 'custom' and custom_positions is not None:
            positions = np.array(custom_positions)
            if positions.shape[1] == 2:  # Add z=0 if only x,y provided
                positions = np.column_stack([positions, np.zeros(positions.shape[0])])

        else:
            raise ValueError("Invalid array shape or missing custom positions")

        return positions

    def plot_array_geometry(self):
        """Visualize the array geometry in 3D"""
        fig = plt.figure(figsize=(12, 5))

        # 3D plot
        ax1 = fig.add_subplot(121, projection='3d')
        x_pos = self.element_positions[:, 0]
        y_pos = self.element_positions[:, 1]
        z_pos = self.element_positions[:, 2]

        ax1.scatter(x_pos, y_pos, z_pos, c='red', s=100, marker='o', edgecolors='black', linewidth=2)

        # Add element numbers
        for i, (x, y, z) in enumerate(self.element_positions):
            ax1.text(x, y, z, f'  {i}', fontsize=10)

        ax1.set_xlabel('X (m)')
        ax1.set_ylabel('Y (m)')
        ax1.set_zlabel('Z (m)')
        ax1.set_title(f'{self.array_shape.title()} Array - 3D View')

        # 2D top view
        ax2 = fig.add_subplot(122)
        ax2.scatter(x_pos, y_pos, c='red', s=100, marker='o', edgecolors='black', linewidth=2)

        for i, (x, y, z) in enumerate(self.element_positions):
            ax2.annotate(f'{i}', (x, y), xytext=(5, 5), textcoords='offset points',
                         fontsize=10, fontweight='bold')

        ax2.set_xlabel('X Position (m)')
        ax2.set_ylabel('Y Position (m)')
        ax2.set_title(
            f'{self.array_shape.title()} Array - Top View\n{self.Nr} Elements, f={self.frequency / 1e6:.1f} MHz')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal')

        plt.tight_layout()
        plt.show()

    def steering_vector_3d(self, theta_deg, phi_deg):
        """
        Calculate steering vector for 3D array
        theta_deg: azimuth angle in degrees (0 = +x axis, 90 = +y axis)
        phi_deg: elevation angle in degrees (90 = horizontal, 0 = zenith)
        """
        theta_rad = np.deg2rad(theta_deg)
        phi_rad = np.deg2rad(phi_deg)

        # Direction unit vector (pointing towards source)
        ux = np.sin(phi_rad) * np.cos(theta_rad)
        uy = np.sin(phi_rad) * np.sin(theta_rad)
        uz = np.cos(phi_rad)

        # Calculate phase at each element relative to origin
        phases = self.k * (self.element_positions[:, 0] * ux +
                           self.element_positions[:, 1] * uy +
                           self.element_positions[:, 2] * uz)

        # Steering vector (conjugate for receive beamforming)
        steering_vector = np.exp(-1j * phases).reshape(-1, 1)

        return steering_vector

    def array_factor(self, weights, theta_range, phi_range):
        """
        Calculate array factor over angular range
        """
        AF = np.zeros((len(phi_range), len(theta_range)), dtype=complex)

        for i, phi in enumerate(phi_range):
            for j, theta in enumerate(theta_range):
                s = self.steering_vector_3d(theta, phi)
                AF[i, j] = np.abs(weights.conj().T @ s) ** 2

        return AF

    def generate_signals(self, soi_angles, interferer_angles, soi_powers=None,
                         interferer_powers=None, noise_power=0.1, n_samples=1000):
        """
        Generate received signals with SOI, interferers, and noise
        soi_angles: List of [theta, phi] pairs for SOI
        interferer_angles: List of [theta, phi] pairs for interferers
        """
        self.n_samples = n_samples
        t = np.arange(n_samples) / (10 * self.frequency)  # Time vector

        # Initialize received signal matrix
        X = np.zeros((self.Nr, n_samples), dtype=complex)

        # Set default powers
        if soi_powers is None:
            soi_powers = [1.0] * len(soi_angles)
        if interferer_powers is None:
            interferer_powers = [1.0] * len(interferer_angles)

        # Generate SOI signals
        self.soi_angles = soi_angles
        # for all SOI, make signal, add to signal matrix
        for i, (angles, power) in enumerate(zip(soi_angles, soi_powers)):
            theta, phi = angles
            s = self.steering_vector_3d(theta, phi)
            freq_offset = (i + 1) * 0.01e6  # Different frequencies for each signal
            tone = np.sqrt(power) * np.exp(2j * np.pi * freq_offset * t)
            X += s @ tone.reshape(1, -1)

        # Generate interferer signals
        self.interferer_angles = interferer_angles
        # for all interferer, make signal, add to signal mat
        for i, (angles, power) in enumerate(zip(interferer_angles, interferer_powers)):
            theta, phi = angles
            s = self.steering_vector_3d(theta, phi)
            freq_offset = (i + 10) * 0.015e6  # Different frequencies
            tone = np.sqrt(power) * np.exp(2j * np.pi * freq_offset * t)
            X += s @ tone.reshape(1, -1)

        # Add noise to signal mat. Noise mdoeled as complex
        noise = np.sqrt(noise_power / 2) * (np.random.randn(self.Nr, n_samples) +
                                            1j * np.random.randn(self.Nr, n_samples))
        X += noise

        self.X = X

        print(f"\nSignal Generation:")
        print(f"SOI angles (θ,φ): {soi_angles} degrees")
        print(f"Interferer angles (θ,φ): {interferer_angles} degrees")
        print(f"Samples: {n_samples}")

        return X

    def conventional_beamformer(self, theta_deg, phi_deg):
        """Calculate conventional beamformer weights"""
        return self.steering_vector_3d(theta_deg, phi_deg)

    def mvdr_beamformer(self, theta_deg, phi_deg):
        """Calculate MVDR weights for given angle"""

        # comptue steerign vectro
        s = self.steering_vector_3d(theta_deg, phi_deg)
        # Compute signal covariance amtrix
        sig_covR = (self.X @ self.X.conj().T) / self.X.shape[1]

        # Add small diagonal loading for numerical stability
        # Hence computing Noise covariance matrix
        noise_covR = 1e-6 * np.eye(self.Nr)

        # compute the spacial covariance matric
        R = sig_covR+noise_covR

        # attempt to compute inverse spacial covariance matrdix
        try:
            Rinv = np.linalg.inv(R)
        except:
            Rinv = np.linalg.pinv(R)

        # calcualte complex hermirtian weithg that minimizes the variance and creates
        # a distiotionless resposne
        denominator = s.conj().T @ Rinv @ s
        w = (Rinv @ s) / denominator

        return w

    def lcmv_beamformer(self, soi_angles, null_angles=None):
        """
        LCMV beamformer with multiple SOI and optional nulls
        """
        # Create constraint matrix C
        steering_vectors = []
        desired_response = []

        # Add SOI constraints
        for theta, phi in soi_angles:
            # append steering vecotr
            steering_vectors.append(self.steering_vector_3d(theta, phi))
            # append constraint
            desired_response.append(1.0)

        # Add null constraints if specified
        if null_angles is not None:
            for theta, phi in null_angles:
                # append interferer steering vec
                steering_vectors.append(self.steering_vector_3d(theta, phi))
                # apply null constrainy
                desired_response.append(0.0)


        C = np.concatenate(steering_vectors, axis=1)
        f = np.array(desired_response).reshape(-1, 1)

        # Calculate covariance matrix
        signal_covR = (self.X @ self.X.conj().T) / self.X.shape[1]
        noise_covR = 1e-6 * np.eye(self.Nr)  # Diagonal loading


        spacial_covR=signal_covR+noise_covR


        try:
            Rinv = np.linalg.inv(spacial_covR)
        except:
            Rinv = np.linalg.pinv(spacial_covR)

        # LCMV equation
        try:
            w = Rinv @ C @ np.linalg.inv(C.conj().T @ Rinv @ C) @ f
        except:
            w = Rinv @ C @ np.linalg.pinv(C.conj().T @ Rinv @ C) @ f

        return w

    def plot_azimuth_pattern(self, weights, phi_fixed=90, title="Azimuth Pattern"):
        """Plot beam pattern vs azimuth at fixed elevation"""
        theta_range = np.linspace(-180, 180, 361)
        phi_range = [phi_fixed]

        AF = self.array_factor(weights, theta_range, phi_range)
        AF_dB = 10 * np.log10(np.abs(AF.flatten()) / np.max(np.abs(AF)))

        # Polar plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Polar
        ax1 = plt.subplot(121, projection='polar')
        theta_rad = np.deg2rad(theta_range)
        ax1.plot(theta_rad, AF_dB)
        ax1.set_theta_zero_location('N')
        ax1.set_theta_direction(-1)
        ax1.set_ylim([-40, 0])
        ax1.set_title(f'{title}\nElevation = {phi_fixed}°')

        # Add SOI and interferer markers
        if hasattr(self, 'soi_angles'):
            for theta, phi in self.soi_angles:
                if abs(phi - phi_fixed) < 5:  # Show if close to current elevation
                    ax1.plot([np.deg2rad(theta)], [-5], 'go', markersize=10, label='SOI')
        if hasattr(self, 'interferer_angles'):
            for theta, phi in self.interferer_angles:
                if abs(phi - phi_fixed) < 5:
                    ax1.plot([np.deg2rad(theta)], [-5], 'ro', markersize=10, label='Interferer')

        # Cartesian
        ax2.plot(theta_range, AF_dB)
        ax2.set_xlabel('Azimuth (degrees)')
        ax2.set_ylabel('Gain (dB)')
        ax2.set_title(f'{title} - Cartesian View')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([-40, 5])
        ax2.set_xlim([-180, 180])

        # Add markers
        if hasattr(self, 'soi_angles'):
            for theta, phi in self.soi_angles:
                if abs(phi - phi_fixed) < 5:
                    ax2.axvline(x=theta, color='green', linestyle='--', alpha=0.7, label='SOI')
        if hasattr(self, 'interferer_angles'):
            for theta, phi in self.interferer_angles:
                if abs(phi - phi_fixed) < 5:
                    ax2.axvline(x=theta, color='red', linestyle='--', alpha=0.7, label='Interferer')

        plt.tight_layout()
        plt.show()

        return theta_range, AF_dB

    def plot_elevation_pattern(self, weights, theta_fixed=0, title="Elevation Pattern"):
        """Plot beam pattern vs elevation at fixed azimuth"""
        theta_range = [theta_fixed]
        phi_range = np.linspace(0, 180, 181)

        AF = self.array_factor(weights, theta_range, phi_range)
        AF_dB = 10 * np.log10(np.abs(AF.flatten()) / np.max(np.abs(AF)))

        # Polar plot (elevation)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Polar - convert elevation to show horizon at edge
        ax1 = plt.subplot(121, projection='polar')
        phi_polar = np.deg2rad(90 - phi_range)  # Convert to polar coords (0 = zenith)
        ax1.plot(phi_polar, AF_dB)
        ax1.set_theta_zero_location('N')
        ax1.set_theta_direction(-1)
        ax1.set_ylim([-40, 0])
        ax1.set_title(f'{title}\nAzimuth = {theta_fixed}°')

        # Cartesian
        ax2.plot(phi_range, AF_dB)
        ax2.set_xlabel('Elevation (degrees)')
        ax2.set_ylabel('Gain (dB)')
        ax2.set_title(f'{title} - Cartesian View')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([-40, 5])
        ax2.set_xlim([0, 180])

        # Add markers
        if hasattr(self, 'soi_angles'):
            for theta, phi in self.soi_angles:
                if abs(theta - theta_fixed) < 5:
                    ax2.axvline(x=phi, color='green', linestyle='--', alpha=0.7, label='SOI')
        if hasattr(self, 'interferer_angles'):
            for theta, phi in self.interferer_angles:
                if abs(theta - theta_fixed) < 5:
                    ax2.axvline(x=phi, color='red', linestyle='--', alpha=0.7, label='Interferer')

        plt.tight_layout()
        plt.show()

        return phi_range, AF_dB

    def plot_3d_pattern(self, weights, title="3D Beam Pattern"):
        """Plot full 3D beam pattern"""
        # Create angular grids
        theta_range = np.linspace(-180, 180, 73)  # Azimuth
        phi_range = np.linspace(0, 180, 37)  # Elevation

        # Calculate array factor
        AF = self.array_factor(weights, theta_range, phi_range)
        AF_dB = 10 * np.log10(np.abs(AF) / np.max(np.abs(AF)))

        # Convert to spherical coordinates for 3D plotting
        THETA, PHI = np.meshgrid(np.deg2rad(theta_range), np.deg2rad(phi_range))

        # Convert to Cartesian for 3D surface
        R = 10 ** (AF_dB / 20)  # Convert dB to linear for radius
        R = np.maximum(R, 0.01)  # Avoid negative values

        X = R * np.sin(PHI) * np.cos(THETA)
        Y = R * np.sin(PHI) * np.sin(THETA)
        Z = R * np.cos(PHI)

        # Create 3D plot
        fig = plt.figure(figsize=(15, 5))

        # 3D surface plot
        ax1 = fig.add_subplot(131, projection='3d')
        surf = ax1.plot_surface(X, Y, Z, cmap='jet', alpha=0.8,
                                facecolors=plt.cm.jet((AF_dB + 40) / 40))
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title(f'{title}\n3D Surface')

        # 2D contour plot (top view)
        ax2 = fig.add_subplot(132)
        theta_2d = np.linspace(-180, 180, 73)
        phi_2d = np.linspace(0, 180, 37)
        THETA_2D, PHI_2D = np.meshgrid(theta_2d, phi_2d)

        contour = ax2.contourf(THETA_2D, PHI_2D, AF_dB, levels=20, cmap='jet')
        ax2.set_xlabel('Azimuth (degrees)')
        ax2.set_ylabel('Elevation (degrees)')
        ax2.set_title('2D Contour Plot')
        plt.colorbar(contour, ax=ax2, label='Gain (dB)')

        # Add source locations
        if hasattr(self, 'soi_angles'):
            for theta, phi in self.soi_angles:
                ax2.plot(theta, phi, 'go', markersize=10, label='SOI')
        if hasattr(self, 'interferer_angles'):
            for theta, phi in self.interferer_angles:
                ax2.plot(theta, phi, 'ro', markersize=10, label='Interferer')

        # Azimuth cut at elevation = 90°
        ax3 = fig.add_subplot(133)
        phi_cut = 90
        phi_idx = np.argmin(np.abs(phi_range - phi_cut))
        azimuth_cut = AF_dB[phi_idx, :]

        ax3.plot(theta_range, azimuth_cut)
        ax3.set_xlabel('Azimuth (degrees)')
        ax3.set_ylabel('Gain (dB)')
        ax3.set_title(f'Azimuth Cut (φ = {phi_cut}°)')
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim([-40, 5])

        plt.tight_layout()
        plt.show()

        return THETA, PHI, AF_dB

    def plot_spectral_density(self, beamformer_weights=None):
        """Plot power spectral density of beamformed signal"""
        if beamformer_weights is not None:
            # Apply beamforming weights
            X_bf = beamformer_weights.conj().T @ self.X
            signal_data = X_bf.flatten()
            title_suffix = " (Beamformed)"
        else:
            # Use signal from first element
            signal_data = self.X[0, :]
            title_suffix = " (Single Element)"

        # Calculate PSD
        fs = 10 * self.frequency  # Sampling frequency
        f, psd = signal.welch(signal_data, fs=fs, nperseg=min(512, len(signal_data) // 4))

        # Plot
        plt.figure(figsize=(12, 6))
        plt.semilogy(f / 1e6, psd)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Power Spectral Density (V²/Hz)')
        plt.title(f'Power Spectral Density{title_suffix}')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

        return f, psd

    def compare_beamformers(self, soi_theta=0, soi_phi=90):
        """Compare different beamforming techniques"""
        # Calculate weights for each beamformer
        w_conv = self.conventional_beamformer(soi_theta, soi_phi)
        w_mvdr = self.mvdr_beamformer(soi_theta, soi_phi)
        w_lcmv = self.lcmv_beamformer([(soi_theta, soi_phi)], self.interferer_angles)

        print(f"\nComparing beamformers pointed at θ={soi_theta}°, φ={soi_phi}°")

        # Plot azimuth patterns
        print("Plotting azimuth patterns...")
        self.plot_azimuth_pattern(w_conv, soi_phi, "Conventional Beamformer")
        self.plot_azimuth_pattern(w_mvdr, soi_phi, "MVDR Beamformer")
        self.plot_azimuth_pattern(w_lcmv, soi_phi, "LCMV Beamformer")

        # Plot elevation patterns
        print("Plotting elevation patterns...")
        self.plot_elevation_pattern(w_conv, soi_theta, "Conventional Beamformer")
        self.plot_elevation_pattern(w_mvdr, soi_theta, "MVDR Beamformer")
        self.plot_elevation_pattern(w_lcmv, soi_theta, "LCMV Beamformer")

        # Plot 3D patterns
        print("Plotting 3D patterns...")
        self.plot_3d_pattern(w_conv, "Conventional Beamformer")
        self.plot_3d_pattern(w_mvdr, "MVDR Beamformer")
        self.plot_3d_pattern(w_lcmv, "LCMV Beamformer")



def test_ULA():
    # Example 1: Linear array with detailed analysis
    print("=" * 70)
    print("EXAMPLE 1: LINEAR ARRAY - DETAILED BEAMFORMING ANALYSIS")
    print("=" * 70)

    bf_linear = AdaptiveBeamformer(
        frequency=2.4e9,  # 2.4 GHz WiFi frequency
        array_shape='linear',
        num_elements=8
    )

    bf_linear.plot_array_geometry()

    # Generate signals: SOI at (30°, 90°), interferers at various locations
    bf_linear.generate_signals(
        soi_angles=[(30, 90)],  # One SOI at 30° azimuth, 90° elevation
        interferer_angles=[(-45, 90), (0, 90), (60, 80)],  # Three interferers
        soi_powers=[1.0],
        interferer_powers=[1.5, 2.0, 1.2],  # Strong interferers
        noise_power=0.05,
        n_samples=2000
    )

    # Compare all beamforming techniques
    bf_linear.compare_beamformers(soi_theta=30, soi_phi=90)


def test_CircularArray():

    # Example 2: Circular array
    print("\n" + "=" * 70)
    print("EXAMPLE 2: CIRCULAR ARRAY - 360° COVERAGE")
    print("=" * 70)

    bf_circular = AdaptiveBeamformer(
        frequency=1e9,  # 1 GHz
        array_shape='circular',
        num_elements=12
    )

    bf_circular.plot_array_geometry()

    # Generate signals from multiple directions
    bf_circular.generate_signals(
        soi_angles=[(45, 90)],
        interferer_angles=[(-60, 90), (0, 90), (120, 90), (180, 85)],
        soi_powers=[1.0],
        interferer_powers=[1.8, 1.5, 1.3, 1.1],
        noise_power=0.03,
        n_samples=2000
    )

    bf_circular.compare_beamformers(soi_theta=45, soi_phi=90)


def test_URA():
    # Example 3: Rectangular array with 3D capability
    print("\n" + "=" * 70)
    print("EXAMPLE 3: RECTANGULAR ARRAY - 3D BEAMFORMING")
    print("=" * 70)

    bf_rect = AdaptiveBeamformer(
        frequency=5e9,  # 5 GHz
        array_shape='rectangular',
        num_elements=16  # 4x4 array
    )

    bf_rect.plot_array_geometry()

    # 3D scenario with elevation diversity
    bf_rect.generate_signals(
        soi_angles=[(30, 60)],  # SOI at 30° azimuth, 60° elevation
        interferer_angles=[(0, 90), (-45, 80), (60, 70), (90, 45)],
        soi_powers=[1.0],
        interferer_powers=[1.2, 1.8, 1.4, 1.0],
        noise_power=0.04,
        n_samples=2000
    )

    bf_rect.compare_beamformers(soi_theta=30, soi_phi=60)

    # Spectral analysis
    print("\nPerforming spectral analysis...")
    w_mvdr = bf_rect.mvdr_beamformer(30, 60)
    bf_rect.plot_spectral_density()
    bf_rect.plot_spectral_density(w_mvdr)

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

# Example usage and demonstrations
if __name__ == "__main__":
    test_URA()




