# IS4320 I2C Modbus RTU Master Python example on Raspberry Pi (ISXMPL4320ex4)

Coding with Raspberry Pi for the IS4320 is very simple. It does not require 
any INACKS-specific library, just the standard Python smbus2 library for I2C:
`i2c_msg.write()`, `i2c_msg.read()` and related.

This Raspberry Pi project uses the IS4320 I2C Modbus RTU Master chip. 
The example demonstrates how to use the Pi to communicate with the IS4320 
over I2C. In this example, the Raspberry Pi instructs the IS4320 to read 
Holding Register 0 using Function Code 3 from a Modbus Slave, and prints 
the result to the console.

To test the example, you will need a Modbus Slave. You can use the **pyModSlave** 
software, which is a Modbus TCP/RTU Slave simulator. Configure the Slave with 
these values: Slave Address `1`, `19200` baud, **Even** parity, and `1` Stop bit.

More info at:
- [Kappa4320Ard Evaluation Board](https://www.inacks.com/kappa4320ard)
- [IS4320 Datasheet](https://www.inacks.com/is4320)
- [pyModSlave](https://www.sourceforge.net/projects/pymodslave)
- [INACKS Website](https://www.inacks.com)

You can download this Python project at:  
[https://github.com/inacks/ISXMPL4320ex5](https://github.com/inacks/ISXMPL4320ex5)

