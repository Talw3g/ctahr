
from serial import Serial
from . import configuration

class DisplayLib:

    def __init__(self):
        # Configuring display
        self.serial = Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)
        # disables autoscroll:
        self.write([chr(254),chr(82)])
        # reset display contrast:
        self.write([chr(254),chr(145),chr(100)])
        self.clear()
        # Create waterdrop and thermometer symbols:
        self.waterdrop()
        self.thermo()


    def backwards(self, row, col, msg, typ):
        """ Returns an instruction str to write 'msg' backwards, starting
        at position [col,row], and append the right typ: degC, % or KWh"""
        instr = []
        if typ == 'T':
            start = col - 6
            width = 5 - len(str(msg))
            instr += self.clr_zone(row,start,width)
            instr += self.goto(row,col)
        else:
            instr += self.goto(row,col)

        msg = list(str(msg))
        if typ == 'T':
            msg.append(chr(178))
            msg.append('C')
        elif typ == 'H':
            msg.append(chr(37))
        elif typ == 'E':
            msg.append('K')
            msg.append('W')
            msg.append('h')

        for i in reversed(msg):
            instr.append(i)
            instr.extend([chr(254),chr(76)] * 2)

        self.write(instr)


    def waterdrop(self):
        """ Stores the waterdrop symbol in slot 0"""
        instr = [chr(254),chr(78),chr(0)]
        instr.extend([chr(4)] * 2)
        instr.extend([chr(10)] * 2)
        instr.extend([chr(17)] * 3)
        instr.append(chr(14))
        self.write(instr)


    def thermo(self):
        """ Stores the thermometer symbol in slot 1"""
        instr = [chr(254),chr(78),chr(1)]
        instr.append(chr(4))
        instr.extend([chr(10)] * 2)
        instr.extend([chr(14)] * 2)
        instr.extend([chr(31)] * 2)
        instr.append(chr(14))
        self.write(instr)


    def goto(self,row,col):
        instr = [chr(254),chr(71)]
        instr.append(chr(col))
        instr.append(chr(row))
        return instr


    def home(self):
        self.write([chr(254),chr(72)])


    def clr_zone(self,row,col,width):
        """ Returns the instruction str to clear the zone starting
        at [col,row] and 'width' slot-wide"""
        instr = self.goto(row,col)
        instr.extend([chr(32)] * width)
        return instr


    def backlight(self,state):
        if state:
            self.write([chr(254),chr(66)])
        else:
            self.write([chr(254),chr(70)])


    def clear(self):
        """ Clear display """
        self.write([chr(254),chr(88)])


    def write(self,msg):
        instr = []
        if type(msg) == str:
            instr = list(msg)
        elif type(msg) == list:
            instr = msg
        elif type(msg) == float or type(msg) == int:
            instr = list(str(msg))
        else:
            print('Error: invalid type.',
                'Available types: [list, str, float, int], got',type(msg))
            return

        for char in instr:
            hexa = '{:02x}'.format(ord(char))
            bits = bytes.fromhex(hexa)
#            print(hexa,bits)
            self.serial.write(bits)
