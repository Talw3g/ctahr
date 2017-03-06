
class DummyValues:

    def __init__(self):
        self.int_temp = 12.7
        self.int_temp_min = 9.1
        self.int_temp_max = 15.8
        self.ext_temp = 9.7
        self.ext_temp_min = -5.7
        self.ext_temp_max = 19.3
        self.int_hygro = 76.3
        self.int_hygro_min = 74.6
        self.int_hygro_max = 88.7
        self.ext_hygro = 93.5
        self.ext_hygro_min = 57.2
        self.ext_hygro_max = 98.7
        self.fan_status = False
        self.heater_status = False
        self.dehum_status = False
        self.fan_energy = 20.8
        self.heater_energy = 284.1
        self.dehum_energy = 98.4

    def increase(self):
        self.int_temp = round(self.int_temp + 0.1, 1)
        self.heater_status = not self.heater_status

    def reset(self):
        self.int_temp_min = self.int_temp
        self.int_temp_max = self.int_temp
        self.ext_temp_min = self.ext_temp
        self.ext_temp_max = self.ext_temp
