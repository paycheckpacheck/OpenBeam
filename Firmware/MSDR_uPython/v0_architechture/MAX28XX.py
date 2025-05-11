

from machine import Pin
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


        # config
        self.names = names
        self.registers = registers
        self.values = values

        # list of register objects
        self.reg_list = [Register(name, reg, val) for name, reg, val in zip(self.names, self.registers, self.values)]

    def write2reg():
        for i in range(num):
            self.reg_list.write2reg()




class MAX28XX:
    def __init__(self, spi, spi_cs):
        
        
        self.spi = spi
        self.cs = Pin(spi_cs, Pin.OUT)
        self.cs.value(1) # Active low, hence start high to indicate no message
    pass

class MAX2821(MAX28XX):
    pass

class MAX2831(MAX28XX):
    pass