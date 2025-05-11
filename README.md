# Beamforming Research & Implementation Project

## Current Status
**IN PROGRESS**

## Project Overview

This project aims to make **beamforming research and implementation more accessible** by developing both simulation and hardware solutions. The team will work on **FDTD-based simulations** and **hardware development of a beamformer**, starting with phased array elements. Each phased array element will consist of a custom **Software Defined Radio (SDR)** shown below. 


![image](https://github.com/user-attachments/assets/7e5acf7b-bf31-4c8f-90a7-d1229b554992)

Here is how it works. The above pcb is a prototype sheild to the Raspberry PI PICO board. The Pico board connects via serial to the main command system and recives the individual antenna element gain and phase shift defined by beamforming simulation team in addition to the actual transmit data. This data then gets parsed and put into the uC's Direct Memory Address (DMA). Upon some clock cycle the DMA then loads this value into the PICO's Programmable Input Output (PIO) TX FIFO which gets outputed to 8 pins on the pico which are connected to the MAX586X Digital to Analog Converter (DAC). The DAC then creates a baseband Intermediate Frequency (IF) which gets connected to the input of the MAX2822. The MAX2822 will then upconvert this IF to 2.5GHz, this goes into a Balun which makes the differential RF single ended to interface with the RF amplfier which then transmits. 
On the RX chain, we have the opposite process happen. The RF block applies a gain to the received signal, is converted to a differntial pair and inputted into the MAX2822 which downconverts the signal back down to IF. This IF is then connected to the ADC in the MAX586X and digitized. The PIOs then read this 8-bit word outputted form the ADC and load them into the RX FIFO. The DMA then gets this 8-bit word from the RX-FIFO.




## Design Decisions

- Engineers should document design choices, including **trade-offs** and **justifications**.
- The **simulation team** will provide feedback to optimize antenna element placement.
- PCB layouts must be reviewed by both **RF and embedded engineers** before fabrication.

## Steps for Documenting Your Design Process

1. ALWAYS CREATE A NEW BRANCH FOR DEVELOPMENT
2. Keep a **running log** of design iterations.
3. Provide **diagrams and schematics** where applicable.
4. Submit updates to the repository with **detailed commit messages**.
5. Write **clear documentation** for any custom software or hardware decisions.


## Useful Links

- **Documentation for MAX2822**: https://rocelec.widen.net/view/pdf/ybgjsvttkr/MAXMS12737-1.pdf?t.download=true&u=5oefqw
- **Documentation for MAX5864**: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX5864.pdf
- **Raspberry Pi Pico SDK and HW manual**: https://www.raspberrypi.com/documentation/pico-sdk/
- **Additional Raspberry Pi Pico Documentation for Pico 2 RP2350**:  https://www.raspberrypi.com/documentation/microcontrollers/silicon html#rp2350
- **Raaspbeery Pi Pico 2 Pinout Diagram**: https://datasheets.raspberrypi.com/pico/Pico-2-Pinout.pdf
**RP2350 Datasheet**: https://www.raspberrypi.com/documentation/microcontrollers/silicon.html#rp2350
**RP2350 HW Design Guide**: https://datasheets.raspberrypi./rp2350/hardware-design-with-rp2350.pdf
- **FDTD Simulation Resources**: https://fdtd.readthedocs.io/en/latest/


