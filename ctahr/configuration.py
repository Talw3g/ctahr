## PIN CONFIGURATION ##
# Display
display_serial_device = "/dev/ttyAMA0"
display_serial_speed = 19200

# Sensors
thermohygro_sensor_exterior_pin = 17
thermohygro_sensor_interior_pin = 4
optsen_power_pin = 22
optsen_state_pin = 23
light_sensor_pin = 24

# Relays / Buzzer
fan_relay_pin = 13
heater_relay_pin = 25
dehum_relay_pin = 6
buzzer_pin = 26

# HMI switches
fan_lever_pin = 19
heater_lever_pin = 5
dehum_lever_pin = 12
reset_lever_pin = 7

# Servo
servo_power_pin = 27
servo_pwm_pin = 18

# System / Misc
watchdog_pin = 20
powerstate_pin = 23
led_run_pin = 16


## REGULATION FIXED VALUES ##
# Temperature thresholds
temp_low = 11
temp_high = 13
temp_freeze = 9
summer_temp = 13

# Hygrometry thresholds
winter_hygro_low = 75
winter_hygro_high = 80
summer_hygro_low = 85
summer_hygro_high = 90
