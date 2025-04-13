
MAX5864 eval board V1

------------- INPUTS/OUTPUTS-----------------:
Receiver:
RXIP - Real part positive differential 
RXIN - Real part inverted differential (can ground with physical switch) 
RXQP - Imaginary part positive differential 
RXQN - Imaginary part inverted differential (can ground with physical switch) 

Transmitter: 
TXIP - Real part positive differential
TXIN - Real part inverted differential
TXQP - Imaginary part positive differential
TXQN - Imaginary part inverted differential


-------------Pin connections-----------------:   
{ADC} -> {RP2040}

DA0 -> GPIO20
DA1 -> GPIO19
DA2 -> GPIO17
DA3 -> GPIO16
DA4 -> GPIO15
DA5 -> GPIO14
DA6 -> GPIO12
DA7 -> GPIO11


DD0 -> GPIO10
DD1 -> GPIO9
DD2 -> GPIO7
DD3 -> GPIO6
DD4 -> GPIO5
DD5 -> GPIO4
DD6 -> GPIO2

DIN -> GPIO21
SCLK -> GPIO22
CS -> GPIO24
CLK -> 34
 
