
from serial import Serial
from . import configuration

class DisplayLib

    def __init__(self):
        # Configuring display
        self.serial = Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)
        # disables autoscroll:
        self.write(bytes.fromhex('fe52'))
        # reset display contrast:
        self.write(bytes.fromhex('fe9164'))
        self.clear()
        # Create waterdrop and thermometer symbols:
        self.waterdrop()
        self.thermo()

    def backwards(self, row, col, msg, typ):
        """ Returns an instruction str to write 'msg' backwards, starting
        at position [col,row], and append the right typ: degC, % or KWh"""
        if typ == 'T':
            start = col - 6
            width = 5 - len(str(msg))
            instr = self.clr_zone(row,start,width)
            instr += self.goto(row,col)
        else:
            instr = goto(row,col)
        msg = list(str(msg))
        if typ == 'T':
            msg.append('\xb2')
            msg.append('C')
        elif typ == 'H':
            msg.append('\x25')
        elif typ == 'E':
            msg.append('K')
            msg.append('W')
            msg.append('h')
        msg.reverse()
        for i in msg:
            instr += i
            instr += '\xfe\x4c'
            instr += '\xfe\x4c'
        return instr

    def waterdrop(self):
        """ Returns the instruction str to store the waterdrop symbol in
        slot x00"""
        instr = '\xfe\x4e\x00'
        instr += '\x04\x04\x0A\x0A\x11\x11\x11\x0E'
        self.write(instr)

    def thermo(self):
        """ Returns the instruction str to store the thermometer symbol in
        slot x01"""
        instr = '\xfe\x4e\x01'
        instr += '\04\x0A\x0A\x0E\x0E\x1F\x1F\x0E'
        self.write(instr)

    def goto(self,row,col):
        instr = '\xfe\x47'
        instr += chr(col)
        instr += chr(row)
        self.write(instr)

    def clr_zone(self,row,col,width):
        """ Returns the instruction str to clear the zone starting
        at [col,row] and 'width' slot-wide"""
        instr = goto(row,col)
        for i in range(0,width):
            instr += ' '
        self.write(instr)

    def clear(self):
        """ Clear display """
        self.write(bytes.fromhex('fe58'))

    def write(self,msg):
        self.serial.write(msg)
