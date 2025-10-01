"""
Coding with Raspberry Pi for the IS4320 is very simple. It does not require 
any INACKS-specific library, just the standard Python smbus2 library for I2C:
i2c_msg.write(), i2c_msg.read() and related.

This Raspberry Pi project uses the IS4320 I2C Modbus RTU Master chip. 
The example demonstrates how to use the Pi to communicate with the IS4320 
over I2C. In this example, the Raspberry Pi instructs the IS4320 to read 
Holding Register 0 using Function Code 3 from a Modbus Slave, and prints 
the result to the console.

To test the example, you will need a Modbus Slave. You can use the pyModSlave 
software, which is a Modbus TCP/RTU Slave simulator. Configure the Slave with 
these values: Slave Address 1, 19200 baud, Even parity, and 1 Stop bit.

Execute this example with sudo to get access to the I2C interface:
sudo python ISXMPL4320ex4-IS4320 I2C Modbus RTU Master Python example on Raspberry Pi.py

More info at:
- Kappa4320Ard Evaluation Board: https://www.inacks.com/kappa4320rasp
- IS4320 Datasheet: https://www.inacks.com/is4320
- pyModSlave: https://www.sourceforge.net/projects/pymodslave
- Inacks website: https://www.inacks.com

You can download this Python project at: https://github.com/inacks/ISXMPL4320ex5
"""

from smbus2 import SMBus, i2c_msg
import time

I2C_BUS = 1  # 
DEVICE_ADDRESS = 0x14  # 7-bit I2C address of the IS4320

# IS4320 register map
CFG_MBBDR    = 0
CFG_MBPAR    = 1
CFG_MBSTP    = 2
CFG_CHIP_ID  = 4
CFG_CHIP_REV = 5
REQ_EXECUTE  = 6
REQ_SLAVE    = 7
REQ_FC       = 8
REQ_STARTING = 9
REQ_QTY      = 10
RES_STATUS   = 138
RES_DATA1    = 139

def write_IS4320_register(start_register, data_word):
    """
    Write a 16-bit register to the IS4320 memory map.
    
    :param start_register: The 16-bit register address to start writing to.
    :param data_bytes: A list of bytes to write.
    """
    high_addr = (start_register >> 8) & 0xFF
    low_addr = start_register & 0xFF
    data_word_high = (data_word>> 8) & 0xFF
    data_word_low = data_word & 0xFF
    with SMBus(I2C_BUS) as bus:
        msg = i2c_msg.write(DEVICE_ADDRESS, [high_addr, low_addr, data_word_high, data_word_low])
        bus.i2c_rdwr(msg)

def read_IS4320_register(start_register):
    """
    Read a 16-bit value from the IS4320 memory map.
    
    :param start_register: 16-bit register address to read from
    :return: 16-bit integer value read (big-endian)
    """
    high_addr = (start_register >> 8) & 0xFF  # High byte of register address
    low_addr = start_register & 0xFF          # Low byte of register address
    try:
	with SMBus(I2C_BUS) as bus:
	    # Write register address first to set internal pointer
            write_msg = i2c_msg.write(DEVICE_ADDRESS, [high_addr, low_addr])
            # Prepare to read 2 bytes from the device
            read_msg = i2c_msg.read(DEVICE_ADDRESS, 2)
            bus.i2c_rdwr(write_msg, read_msg)
    
            data = list(read_msg)  # Read bytes as list of ints
            # Combine high and low bytes into 16-bit integer (big-endian)
            value = (data[0] << 8) | data[1]
            return value
    except IOError as e:
        return None  # return None on failure


chipID = None
chipRev = None

# Detect the chip
chipID = None
chipRev = None

# Detect the chip
while True:
    chipID = read_IS4320_register(CFG_CHIP_ID)
    chipRev = read_IS4320_register(CFG_CHIP_REV)

    if chipID == 20:
        print("IS4320 Chip detected on I2C!")
        print("Chip ID:", chipID)
        print("Chip Rev:", chipRev)
        break

    print("ERROR: IS4320 Chip NOT detected on I2C!")
    time.sleep(1)

# First, configure the Modbus communication parameters
# to match the slave characteristics.
# This only needs to be done once before communicating
# with a Modbus device that has a different configuration.

# Set baud rate to 19200:
baudRate = 113
write_IS4320_register(CFG_MBBDR, baudRate)

# Set parity to Even:
parityBit = 122
write_IS4320_register(CFG_MBPAR, parityBit)

# Set stop bits to 1:
stopBits = 131
write_IS4320_register(CFG_MBSTP, stopBits)

while True:
    """Example: Read Holding Register 0 and print its value."""

    # Set the Modbus Slave ID:
    modbusSlaveId = 1
    write_IS4320_register(REQ_SLAVE, modbusSlaveId)

    # Set the Function Code. For reading Holding Registers, use FC = 3:
    functionCode = 3
    write_IS4320_register(REQ_FC, functionCode)

    # Set the Starting Register address. Here we want to read Holding Register 0:
    startingRegister = 0
    write_IS4320_register(REQ_STARTING, startingRegister)

    # Set the number of Holding Registers to read (minimum is 1):
    quantity = 1
    write_IS4320_register(REQ_QTY, quantity)

    # Send the request to the Modbus Slave:
    write_IS4320_register(REQ_EXECUTE, 1)

    # Read back the result/status of the operation:
    status = None
    while (status == None):
        status = read_IS4320_register(RES_STATUS)

    if status == 2:
        # OK! The request was sent and a response was received
        holdingRegisterData = read_IS4320_register(RES_DATA1)
        print("Holding Register 0 content =", holdingRegisterData)

    elif status == 3:
        # Timeout: no response from the Modbus Slave
        print("Timeout, the Modbus Slave did not answer.")
        print("Did you start the pyModSlave? Did you set its configuration to: "
              "Slave Address 1, 19200 baud, Even parity, and 1 Stop bit?")

    elif status == 4:
        print("Broadcast message sent.")

    elif status == 5:
        print("You configured wrongly the REQ_SLAVE register.")

    elif status == 6:
        print("You configured wrongly the REQ_FC register.")

    elif status == 7:
        print("You configured wrongly the REQ_QTY register.")

    elif status == 8:
        print("There was a Frame Error.")

    elif status == 201:
        print("Modbus Exception Code 1: Illegal Function.")

    elif status == 202:
        print("Modbus Exception Code 2: Illegal Data Address.")
        print("If using pyModSlave, make sure the 'Start Addr' parameter is set to 0.")

    elif status == 203:
        print("Modbus Exception Code 3: Illegal Data Value.")

    elif status == 204:
        print("Modbus Exception Code 4: Server Device Failure.")

    else:
        print("Unknown Error")

    # Add a delay to give the Modbus Slave time to respond and avoid stressing it:
    time.sleep(1)
