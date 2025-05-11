from machine import Pin, SPI
import time
import machine
from MAX5864 import MAX586X
from MAX28XX import MAX2831
import _thread

# Based on the V1 of SDR Hardware
MAX2831_CS_PIN = 0
MAX5864_CS_PIN = 1
SPI_CLK_PIN = 2
SPI_DIN_PIN = 3
BBC_CLK_PIN = 26


class MSDR:
    def __init__(self):



        # Inicialize the SPI
        self.spi = SPI(0, baudrate=10000,
                      sck=Pin(SPI_CLK_PIN),
                      mosi=Pin(SPI_DIN_PIN),
                      miso=None)# that way we can read back

        # Inicialize the Updownconverter
        #self.updown_converter = MAX2831(spi = self.spi, spi_cs = MAX2831_CS_PIN )

        # Inicialize the ADC and DAC IC
        self.bb_converter = MAX586X(spi_hw=self.spi, spi_cs = MAX5864_CS_PIN,
                                    clk_pin = BBC_CLK_PIN)
        
        
        
        
pae = MSDR()

while True:
    pae.bbc_converter.send_iq(0,int(hex("FF")))


        
        