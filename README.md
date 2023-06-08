# Suito
## Leds
07_LED LIGHTS
Suito transmits speed, cadence and power data via the
ANT+ and Bluetooth Smart protocols.
There are 3 LED lights on the motherboard, displaying power
supply status, motherboard status and the protocol being
used.
The LED lights come in 3 colors with the following meanings:
Red = status of hometrainer power supply
- Off = Suito is not receiving power or has the entered sleep
mode
- On = Suito is powered up.
Blue = Suito is connected via the Bluetooth Smart
protocol.
-Slow blinking = Suito is awaiting connection.
-On = Suito is transmitting data via the Bluetooth Smart
protocol.
- Fast blink = searching for a power meter (see "08_Power
Meter Link" chapter)
Green = Suito is connected via the ANT+ protocol.
-Slow blinki = Suito is awaiting connection.
-On = Suito is transmitting data via the ANT+ protocol.
- Fast blink = searching for a power meter (see "08_Power
Meter Link" chapter)
## bluetooth protocols
### Fitness Machine
This protocol sends training data to compatible software /
app / device and adjusts resistance on the hometrainer.

### Speed & Cadence
"Speed&Cadence Service" protocol*: this protocol transmits
hometrainer speed and cadence data, but does not allow
interaction between software / app / device and the
hometrainer.

### Power Service
"Power Service" protocol: this protocol transmits the cyclist’s
power output data, but will it also not allow interaction
between software / app / device and the hometrainer

\x08\x00\x00\x00\x00T\x00\x00\x00\x00\x00\x00
