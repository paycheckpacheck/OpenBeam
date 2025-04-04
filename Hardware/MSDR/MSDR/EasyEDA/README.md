

# 📡 MSDR: Mixed Signal Defined Radio System

## 📘 Introduction

## 🧊 MAX2831: Analog Front End

Shown below is the full internal block diagram behind our analog front end. We can break this up into 3 main sections, Recieve (RX), Transmit(TX), and Syncronization(PLL).
![image](https://github.com/user-attachments/assets/2cc59bc3-53ec-458b-a3bb-fc4ac5c47e8a)

### RX Chain
The single ended 50 ohm input to the system goes into a 1:2 balun to create a balanced 2.5GHz signal. This is internally AC coupled to the variable low noise amplifer at the start of the chain, these are typically implemented as variable darlington pairs.
![image](https://github.com/user-attachments/assets/decc8459-cb36-4795-90fe-23da08ab4ce1)
Below is a sample of the datasheet with an overview of the Embedded LNA Control.
![image](https://github.com/user-attachments/assets/3bd9f271-535d-49b1-ba13-b24c3dddfe42)

This RF's power is split and used to create IQ pairs using a direct downconversion archetechture as shown below. 
![image](https://github.com/user-attachments/assets/1634caee-be5d-4fbb-9d12-24010fbffc78)

Each mixer outputs the following signal which contains a low freq harmonic at (Wrf-Wlo) and a high freq harmonic at (Wrf+Wlo)
![image](https://github.com/user-attachments/assets/0884b154-8ce6-4702-a5c9-6b456362af58)

The principal reason why we are doing this is to to lower the frequency (downconvert) that 2.5Ghz signal into a baseband frequency we can sample and proccess at, whence 10 Mhz given 20Mhz sample rate. From the equation above, we can use a lowpass filter to attenuate the high harmonic, keeping the downconverted frequency which is further amplifed at baseband. Note the corner freq on the LPF and gain on baseband amp are configurable from registers using SPI. 

This whole process occurs twice as shown above, the chain on top represents the real component of the carrier (inphase component); the bottom chain represents the imaginary (quadrature) component, hence its local oscillator is phase shifted 90 to become sine. Pysdr does a great job at explaining the basics behind inphase quadrature signals and how they can be used for Amplitude and Phase modulation protocals like QAM and QPSK, (in addition to FM). 
Link: 
 https://pysdr.org/content/sampling.html

Also seen in this downconversion circuit is a periphail RSSI (Recieved Signal Strength Indicator) which outputs an analog recvied signal strength.






## ⚡ MAX5864 High-Speed ADC/DAC
- IQ Interface Description
- Sampling Requirements and Nyquist Analysis
- Data Path Overview

## 🧮 Mathematical System Model
- I/Q Demodulation and Sampling
- I/Q Modulation for Transmission
- Frequency Domain Considerations

## 🔄 Full System Signal Flow
- Receive Path: RF to Digital
- Transmit Path: Digital to RF

## 🎮 RP2040 Microcontroller Role
- SPI Configuration for MAX2831
- Timing & Control for MAX5864
- Data Acquisition & Streaming

## 📌 Pin Mapping and Wiring
- MAX2831 ↔ RP2040
- MAX5864 ↔ RP2040
- Clocking, Control, and Data Lines

## 🧪 Setup and Usage Notes
- Power Requirements
- Clock/LO Configuration
- Filtering and Impedance Matching
- Grounding Considerations

## 🛠️ Future Improvements

## 📂 Project Structure

## 📚 References

## 🙌 Credits
