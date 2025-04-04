📡 MSDR: Mixed Signal Defined Radio with MAX2831 and MAX5864
This project implements a Mixed Signal Defined Radio (MSDR) system using the MAX2831 RF up/downconverter and the MAX5864 dual-channel DAC/ADC, interfaced with a Raspberry Pi Pico (RP2040) microcontroller. The design supports both transmission and reception of IQ signals for SDR development, beamforming, and RF experimentation.

🧩 Components
Component	Description
MAX2831	RF Transceiver with integrated LO, mixer, AGC, and TR switch. Used for up/downconversion in 2.4 GHz band.
MAX5864	Dual 8-bit, 500 MSPS ADC/DAC for high-speed baseband I/Q signal processing.
RP2040 (Pico)	Controls SPI configuration and manages IQ data streams to/from the MAX5864.
20 MHz Crystal	Provides reference clock to MAX2831.
🔌 System Overview
![image](https://github.com/user-attachments/assets/2e832129-07a4-4afe-a01d-168cde68b0f8)

      Antenna / BPF
🛠️ Pin Mapping Summary
MAX5864 ↔ RP2040
MAX5864 Pin	Signal	RP2040 GPIO
D0-D7	DAC/ADC Data Bus	GPIO 0-7 (Pico)
CLK	Sampling Clock	External / RP2040 output
WRT/READ	Control for DAC/ADC	GPIO 8+
RESET	Active-low reset	GPIO (dedicated)
MAX2831 ↔ RP2040
MAX2831 Pin	Function	RP2040 GPIO
SPI_MOSI	Config Data	GPIO
SPI_CLK	SPI Clock	GPIO
SPI_CS	Chip Select	GPIO
ENABLE	Power/Enable Control	GPIO
TX/RX	Control Mode	GPIO
LOCK_DETECT	PLL Lock Status	GPIO input
⚙️ Features
Full-Duplex Capable (Time-Division): Use TR switch for controlled switching.

500 MSPS Dual-Channel Data: High-resolution IQ sampling.

Dynamic Reconfiguration: SPI interface to adjust MAX2831 parameters (LO frequency, gain, mode).

Phase Control for Beamforming: Use RP2040 or external controller to shift phase in IQ baseband.

🧪 Use Cases
🛰️ Satellite & Beamforming Experiments

📶 802.11 b/g SDR Prototyping

📻 Custom RF Modem Development

🧠 Educational Tool for DSP/RF

🧰 Setup Instructions
1. Power Supply
Connect regulated 3.3V and 1.8V rails.

Ensure sufficient current for MAX5864 and MAX2831.

2. SPI Configuration
Use RP2040 SPI peripheral to configure MAX2831 registers (consult MAX2831 datasheet).

Default LO is 2.412 GHz (use divider to change).

3. Baseband I/Q Interface
RP2040 handles 8-bit parallel I/Q data via PIO or DMA to/from MAX5864.

Sync DAC/ADC clock with MAX2831 or provide external reference.

4. Control Signals
Toggle TX/RX mode via GPIO.

Monitor PLL_LOCK signal to ensure LO lock status.

📂 File Structure (Optional for repo)
Copy
Edit
/
├── firmware/
│   └── pico_msdr_spi_config.c
├── hardware/
│   └── msdr_schematic.kicad_sch
├── README.md
📎 Notes
IQ Clocking: Ensure sample alignment and phase consistency with MAX5864.

Impedance Matching: Use 50-ohm traces, baluns, and BPFs at RF I/O.

Antialias Filtering: Add low-pass or bandpass filters after DAC and before ADC.

📘 References
MAX2831 Datasheet (Analog Devices)

MAX5864 Datasheet

RP2040 Datasheet (Raspberry Pi Foundation)

🙌 Acknowledgments
Designed as part of a research/development SDR system for embedded beamforming and RF experimentation. Created with ❤️ by [Your Name / Team].

Let me know if you'd like a KiCad .sch and .pcb repo structure added, or if you want me to generate firmware stubs for SPI control or I/Q buffering on the Pico.
