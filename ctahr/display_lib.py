
from serial import Serial
import math
from . import configuration

class DisplayLib:

    def __init__(self):
        # Configuring display
        self.serial = Serial(
            self.configuration.display_serial_device,
            self.configuration.display_serial_speed)
        # disables autoscroll:
        self.write(b'\xfe\x52')
        # reset display contrast:
        self.write(b'\xfe\x91\x64')
        self.clear()
        # Create waterdrop and thermometer symbols:
        self.waterdrop()
        self.thermo()


    def justify_R(self, row, col, msg, typ):
        """ Writes 'msg' justified to the right, starting at position [col,row],
        and append the right typ: degC, % or KWh"""
        msg = bytes(str(msg), encoding='ascii')
        if typ == 'T':
            msg += b'\xb2C'
        elif typ == 'H':
            msg += b'\x25'
        elif typ == 'E':
            msg += b'KWh'
        else:
            pass

        start_clr = col - 6
        width = 7 - len(msg)
        prefix = self.clr_zone(row,start_clr,width)
        start = col - (len(msg)-1)
        prefix += self.goto(row,start)
        instr = prefix + msg

        self.write(instr)


    def center(self, row, msg):
        """ Writes 'msg' centered on [row] """
        msg = bytes(str(msg), encoding='ascii')
        start = max(11 - math.ceil(len(msg)/2),1)
        instr = self.goto(row, start)
        instr += msg

        self.write(instr)



    def waterdrop(self):
        """ Stores the waterdrop symbol in slot 0"""
        instr = b'\xfe\x4e\x00'
        instr += b'\x04\x04\x0a\x0a\x11\x11\x11\x0e'
        self.write(instr)


    def thermo(self):
        """ Stores the thermometer symbol in slot 1"""
        instr = b'\xfe\x4e\x01'
        instr += b'\x04\x0a\x0a\x0e\x0e\x1f\x1f\x0e'
        self.write(instr)


    def goto(self,row,col):
        instr = b'\xfe\x47'
        instr += bytes([col,row])
        return instr


    def home(self):
        self.write(b'\xfe\x48')


    def clr_zone(self,row,col,width):
        """ Returns the instruction str to clear the zone starting
        at [col,row] and 'width' slot-wide"""
        instr = self.goto(row,col)
        instr += b'\x20' * width
        return instr


    def backlight(self,state):
        if state:
            self.write(b'\xfe\x42')
        else:
            self.write(b'\xfe\x46')


    def clear(self):
        """ Clear display """
        self.write(b'\xfe\x58')


    def write(self,msg):
        if type(msg) == str:
            instr = bytes(msg, encoding = 'ascii')
        elif type(msg) == bytes:
            instr = msg
        else:
            print('Error: invalid type.',
                'Available types: bytes or str, got',type(msg))
            return

#        with open('/tmp/serial_write.log', 'ab') as f: #           f.write(instr)
#           f.write(instr)

        #print(instr)
        self.serial.write(instr)
