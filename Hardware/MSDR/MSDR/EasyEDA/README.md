

# 📡 MSDR: Mixed Signal Defined Radio System

## 📘 Introduction

## 🧊 MAX2831: Analog Front End

Shown below is the full internal block diagram behind our analog front end. We can break this up into 3 main sections, Recieve (RX), Transmit(TX), and Syncronization(PLL).
![image](https://github.com/user-attachments/assets/2cc59bc3-53ec-458b-a3bb-fc4ac5c47e8a)

### RX Chain
The single ended 50 ohm input to the system goes into a 1:2 balun to create a balanced 2.5GHz signal. This is internally AC coupled to the variable low noise amplifer at the start of the chain, these are typically implemented as variable darlington pairs.
![image](https://github.com/user-attachments/assets/decc8459-cb36-4795-90fe-23da08ab4ce1)

This RF's power is split and used to create IQ pairs using a direct downconversion archetechture as shown below. 
![image](https://github.com/user-attachments/assets/1634caee-be5d-4fbb-9d12-24010fbffc78)

Each mixer outputs the following signal which contains a low freq harmonic at (Wrf-Wlo) and a high freq harmonic at (Wrf+Wlo)
![image](https://github.com/user-attachments/assets/0884b154-8ce6-4702-a5c9-6b456362af58)

The principal reason why we are doing this is to to lower the frequency (downconvert) that 2.5Ghz signal into a baseband frequency we can sample and proccess at, whence 10 Mhz given 20Mhz sample rate. From the equation above, we can use a lowpass filter to attenuate the high harmonic, keeping the downconverted frequency which is further amplifed at baseband. Note the corner freq on the LPF and gain on baseband amp are configurable from registers using SPI. 

This whole process occurs twice as shown above, the chain on top represents the real component of the carrier (inphase component); the bottom chain represents the imaginary (quadrature) component, hence its local oscillator is phase shifted 90 to become sine. Pysdr does a great job at explaining the basics behind inphase quadrature signals and how they can be used for Amplitude and Phase modulation protocals like QAM and QPSK, (in addition to FM). 
Link: 
 https://pysdr.org/content/sampling.html

Also seen in this downconversion circuit is a periphail RSSI (Recieved Signal Strength Indicator) which outputs an analog recvied signal strength.

## TX Chain
In principal, the TX chain is the equivilant of the RX chain, but backwards. Both the RX and TX chains are interfaced to the same antenna (in practice) through the tr module, although this board has seperate coax sma connections for rx and tx.



## ⚡ MAX5864 High-Speed ADC/DAC
- IQ Interface Description
- Sampling Requirements and Nyquist Analysis
- Data Path Overview

## 🧮 Mathematical System Model
- I/Q Demodulation and Sampling
- I/Q Modulation for Transmission
- Frequency Domain Considerations

## 🔄 Full System Signal Flow
- Receive Path: RF signal is amplified then downconverted to a lower frequency and split into iq pairs for phase detection then sampled by the adc which creates an 8-bit word and writes to 8 GPIOs on the RP2040 which are configured to the PIO Hardware State Machines. The state machines can read that 8 bit parrallel load into its internal 8 bit RX FIFO, then pass that to the systems datapath, hence could be confiugred to operare async based off DMA.
- Transmit Path: Same but backwards ...

## 🎮 RP2040 Microcontroller Role
- SPI Configuration for MAX2831 and MAX5864
- Timing & Control for MAX5864 and maybe MAX2831, potential for operating on a reference frequency created by a filtered clock
- Data Acquisition & Streaming

## 📌 Pin Mapping and Wiring
- MAX2831 ↔  | RP2040
- ||   ||    |
- MAX5864 ↔  | RP2040
- Clocking, Control, and Data Lines

## 🧪 Setup and Usage Notes
- Power Requirements
- Clock/LO Configuration
- Filtering and Impedance Matching
- Grounding Considerations


