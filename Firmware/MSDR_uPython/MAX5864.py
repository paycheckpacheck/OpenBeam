#MAX5864 I/Q DAC/ADC Driver


from machine import Pin, SPI
from rp2 import PIO, StateMachine, asm_pio
from array import array
import time




# TDD mode: date_write_poins = data_read_pins 
# on pcb, tie botht h rx buses and the tx busus together
# change pin from inpit to output (on the fly)

class MAX5864:
    """
    Driver for MAX5864 ADC/DAC with DDR I/Q interface
    Supports both PIO-based high-speed transfers and regular GPIO
    """
    
    # Control register addresses
    REG_CONTROL = 0x00
    REG_STATUS = 0x01
    
    def __init__(self,  
                 clk_pin=2,  # 20MHz Clock that hooks up to the MAX5864 Sample Clock
                 data_write_pins=[3,4,5,6,7,8,9,10],  # 8-bit write data bus
                 data_read_pins=[11,12,13,14,15,16,17,18],  # 8-bit read data bus
                 spi_sck=19, 
                 spi_mosi=20,
                 spi_cs=21,
                 use_pio=True):
        

        # ================================ SETUP PINS FOR 20MHz CLOCK ================================
        self.clk = Pin(clk_pin, Pin.OUT)
        

        # ================================ SETUP PINS FOR 8-BIT DATA BUS ================================
        # Setup 8-bit write data bus
        self.data_write = [Pin(pin, Pin.OUT) for pin in data_write_pins]
        
        # Setup 8-bit read data bus
        self.data_read = [Pin(pin, Pin.IN) for pin in data_read_pins]
        
        # ================================ SETUP 3-WIRE SPI INTERFACE FOR CONTROL ================================
        # Setup 3-wire SPI interface for control (half-duplex)
        self.spi = SPI(0, baudrate=1000000, 
                      sck=Pin(spi_sck),
                      mosi=Pin(spi_mosi),
                      miso=None)  # No MISO for 3-wire SPI
        self.cs = Pin(spi_cs, Pin.OUT)
        self.cs.value(1)# Active low, start with CS high
        
        self.use_pio = use_pio
        if use_pio:
            self._setup_pio()
    
    # ================================ PIO PROGRAMS FOR DDR I/Q TRANSMISSION AND RECEPTION ================================
    @asm_pio(out_init=PIO.OUT_LOW, # Initialize output pins to low
             set_init=PIO.OUT_LOW, # Initialize set pins to low
             sideset_init=PIO.OUT_LOW, # Initialize sideset pins to low
             out_shiftdir=PIO.SHIFT_LEFT, # Shift left for DDR
             autopull=True, # Auto pull data from FIFO
             pull_thresh=16) # Pull threshold for FIFO
    def _pio_ddr_tx_program():
        """PIO program for DDR I/Q transmission"""
        # Step 1: I Data Transmission
        out(pins, 8).side(0)    # - Outputs 8 bits of I data
                                # - Sets clock LOW (side(0))
                                # - MAX5864 samples I data on rising edge

        # Step 2: Clock High
        nop().side(1)           # - No data output (nop)
                                # - Sets clock HIGH (side(1))
                                # - Prepares for Q data transmission

        # Step 3: Q Data Transmission
        out(pins, 8).side(1)    # - Outputs 8 bits of Q data
                                # - Sets clock HIGH (side(1))
                                # - MAX5864 samples Q data on falling edge

        # Step 4: Clock Low
        nop().side(0)           # - No data output (nop)
                                # - Sets clock LOW (side(0))
                                # - Prepares for next I data transmission

    @asm_pio(in_shiftdir=PIO.SHIFT_LEFT,
             autopush=True,
             push_thresh=16)
    def _pio_ddr_rx_program():
        """PIO program for DDR I/Q reception"""
        # Sample I data on rising edge
        wait(1, pin, 0)              # Wait for clock rising edge
        in_(pins, 8)                 # Input 8 bits I data
        # Sample Q data on falling edge
        wait(0, pin, 0)              # Wait for clock falling edge
        in_(pins, 8)                 # Input 8 bits Q data
    # constructor dor PIO state machines
    def _setup_pio(self):
        """Initialize PIO state machines"""
        # TX State Machine
        self.sm_tx = StateMachine(0, self._pio_ddr_tx_program,
                                freq=40_000_000,  # 20MHz DDR = 40MHz Clock
                                out_base=self.data_write[0],  # First pin of write bus
                                sideset_base=self.clk)
        
        # RX State Machine                        
        self.sm_rx = StateMachine(1, self._pio_ddr_rx_program,
                                freq=40_000_000,  # 20MHz DDR
                                in_base=self.data_read[0],  # First pin of read bus
                                jmp_pin=self.clk)
                                
        self.sm_tx.active(1)
        self.sm_rx.active(1)

    def write_control(self, reg, value):
        """Write to MAX5864 control registers via 3-wire SPI"""
        self.cs.value(0)
        self.spi.write(bytes([reg << 1 | 0, value]))
        self.cs.value(1)
        
    def read_control(self, reg):
        """Read from MAX5864 control registers via 3-wire SPI"""
        self.cs.value(0)
        result = bytearray(2)
        self.spi.write_readinto(bytes([reg << 1 | 1, 0]), result)
        self.cs.value(1)
        return result[1]

    def set_mode(self, adc_enable=True, dac_enable=True):
        """Configure ADC/DAC operation mode"""
        ctrl = 0
        if adc_enable:
            ctrl |= 0x01
        if dac_enable:
            ctrl |= 0x02
        self.write_control(self.REG_CONTROL, ctrl)

    def send_iq(self, i_data, q_data):
        """Send I/Q data pair"""
        if self.use_pio:
            # Combine I/Q into 16-bit word for PIO
            self.sm_tx.put((i_data << 8) | q_data)
        else:
            # Bit-bang implementation
            self.clk.value(0)
            # Write I data to all 8 pins
            for i in range(8):
                self.data_write[i].value((i_data >> i) & 1)
            self.clk.value(1)
            # Write Q data to all 8 pins
            for i in range(8):
                self.data_write[i].value((q_data >> i) & 1)
            self.clk.value(0)
            
    def receive_iq(self):
        """Receive I/Q data pair"""
        if self.use_pio:
            # Read combined 16-bit I/Q from PIO
            word = self.sm_rx.get()
            return (word >> 8) & 0xFF, word & 0xFF
        else:
            # Bit-bang implementation
            while self.clk.value() == 0:
                pass
            # Read I data from all 8 pins
            i_data = 0
            for i in range(8):
                i_data |= (self.data_read[i].value() << i)
            
            while self.clk.value() == 1:
                pass
            # Read Q data from all 8 pins
            q_data = 0
            for i in range(8):
                q_data |= (self.data_read[i].value() << i)
            return i_data, q_data

    def send_iq_buffer(self, buffer, use_dma=True):
        raise NotImplementedError("DMA not implemented")
        """Send buffer of I/Q data using DMA"""
        if not self.use_pio:
            raise ValueError("DMA only supported with PIO")
            
        # Configure DMA channel
        from machine import mem32
        # ... DMA configuration code would go here
        # This requires lower level RP2040 SDK access
        # which isn't fully exposed in MicroPython
        pass
