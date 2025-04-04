from machine import Pin, SPI
import time





class Register:
    def __init__(self, name, addr, value) -> None:
        

        self.name = name
        self.address = addr
        self.value = value

    def write2reg(self):
        pass
    def get_value(self):
        pass
    def get_addr(self):
        pass
    


class Config:
    def __init__(self, names, registers, values) -> None:


        # init spi ... blah blah
        self.spi = SPI()


        # config
        self.names = names
        self.registers = registers
        self.values = values

        # list of register objects
        self.reg_list = [Register(name, reg, val) for name, reg, val in zip(self.names, self.registers, self.values)]

    def write2reg():
        for i in range(num):
            self.reg_list.write2reg()







REG_TX_A = Register("REG_TX_A", "look at datasheet", "datasheet")



class MAX2821:
    """Driver for MAX2821 RF Transceiver"""
    
    # Register addresses
    REG_TX_A = 0x00 # tx gain
    REG_TX_B = 0x01 # tx bias
    REG_LPF = 0x02
    REG_SHUTDOWN = 0x03
    REG_RX_A = 0x04
    REG_RX_B = 0x05
    REG_SYN_A = 0x06
    REG_SYN_B = 0x07
    REG_SYN_C = 0x08
    REG_SYN_D = 0x09
    REG_SYN_E = 0x0A
    REG_TEST = 0x0B

    def __init__(self, spi_bus=0, spi_cs=5, spi_sck=2, spi_mosi=3, spi_miso=4):
        """Initialize MAX2821 driver
        
        Args:

            spi_bus: SPI bus number
            spi_cs: Chip select pin number
            spi_sck: SPI clock pin number  
            spi_mosi: SPI MOSI pin number
            spi_miso: SPI MISO pin number

        """

        self.num_of_packets = 9
        # Setup SPI interface::    <8 bits Q><8 bits I data> ... 
        self.spi = SPI(spi_bus,
                      baudrate=1_000_000,
                      polarity=0,
                      phase=0,
                      bits=16*self.num_of_packets,
                      sck=Pin(spi_sck),    # clock rate that data is shifted into RX fifo
                      mosi=Pin(spi_mosi))  # master out slave in
        
        self.cs = Pin(spi_cs, Pin.OUT)      # chip select (active-low) 
        # incilize CS to be high ( init to deactivated state )
        self.cs.value(1) # Active low       before data is sent, CS# gets pulled low
        
        # Initialize registers with default values
        self._tx_a = 0x0000
        self._tx_b = 0x0000
        self._lpf = 0x0000  
        self._shutdown = 0x0000
        self._rx_a = 0x0000
        self._rx_b = 0x0000
        self._syn_a = 0x0000
        self._syn_b = 0x0000
        self._syn_c = 0x0000
        self._syn_d = 0x0000
        self._syn_e = 0x0000
        self._test = 0x0000

    def _write_reg(self, addr, data):
        """Write 16-bit value to register"""
        # pull cs# low to activate writing
        self.cs.value(0)
        # Combine address and data into 16-bit word
        word = (addr << 12) | (data & 0x0FFF) 
        # write
        self.spi.write(bytes([word >> 8, word & 0xFF]))
        # pull high, done sending dats

        self.cs.value(1)


class TxConfig:
    """TX Configuration Options"""
    
    class TxGain:
        """TX Gain Settings"""
        GAIN_0DB = 0x0
        GAIN_2DB = 0x1  
        GAIN_4DB = 0x2
        GAIN_6DB = 0x3

    class TxBias:
        """TX Bias Current Settings"""
        BIAS_1_5MA = 0x0
        BIAS_2_0MA = 0x1
        BIAS_2_5MA = 0x2
        BIAS_3_0MA = 0x3

    # other stuff too

class RxConfig:
    """RX Configuration Options"""
    
    class RxGain:
        """RX Gain Settings"""
        GAIN_0DB = 0x0
        GAIN_15DB = 0x1
        GAIN_30DB = 0x2
        GAIN_45DB = 0x3

    class LnaGain:
        """LNA Gain Settings"""
        GAIN_LOW = 0x0
        GAIN_MED = 0x1
        GAIN_HIGH = 0x2
        GAIN_MAX = 0x3

class LpfConfig:
    """Low-Pass Filter Configuration"""
    
    class Bandwidth:
        """Filter Bandwidth Settings"""
        BW_7MHZ = 0x0
        BW_11MHZ = 0x1
        BW_14MHZ = 0x2
        BW_18MHZ = 0x3

class SynthConfig:
    """Synthesizer Configuration"""
    
    class ChargePump:
        """Charge Pump Settings"""
        CURRENT_LOW = 0x0
        CURRENT_MED = 0x1
        CURRENT_HIGH = 0x2
        CURRENT_MAX = 0x3

    def set_frequency(self, freq_mhz):
        """Set synthesizer frequency in MHz"""
        # Calculate N divider and fractional values based on freq
        n_div = int(freq_mhz / 20) # Assuming 20MHz reference
        frac = int((freq_mhz % 20) * 1000)
        
        # Update synthesizer registers
        self._write_reg(self.REG_SYN_A, n_div)
        self._write_reg(self.REG_SYN_B, frac & 0xFFF)
        self._write_reg(self.REG_SYN_C, (frac >> 12) & 0xFFF)

    def set_tx_gain(self, gain):
        """Set TX gain level"""
        self._tx_a = (self._tx_a & ~0x3) | gain
        self._write_reg(self.REG_TX_A, self._tx_a)

    def set_rx_gain(self, gain):
        """Set RX gain level"""
        self._rx_a = (self._rx_a & ~0x3) | gain
        self._write_reg(self.REG_RX_A, self._rx_a)

    def set_lpf_bandwidth(self, bw):
        """Set low-pass filter bandwidth"""
        self._lpf = (self._lpf & ~0x3) | bw
        self._write_reg(self.REG_LPF, self._lpf)

    def enable(self):
        """Enable the device"""
        self._shutdown &= ~0x1
        self._write_reg(self.REG_SHUTDOWN, self._shutdown)

    def disable(self):
        """Disable the device"""
        self._shutdown |= 0x1
        self._write_reg(self.REG_SHUTDOWN, self._shutdown)


class MAX2831:
    # does this have same reg config as max2821
    def __init__(self) -> None:
        self.spi = SPI()
    
    def write_configs(reg_list):
        self.spi.write(addr, value)
        pass
    