ctahr_absolute_path = '/opt/ctahr/'

## PIN CONFIGURATION ##
# Display
display_serial_device = "/dev/ttyAMA0"
display_serial_speed = 115200

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
servo_dutycycle_close = 6
servo_dutycycle_open = 9


# System / Misc
watchdog_pin = 20
powerstate_pin = 23
led_run_pin = 16

stats_log_file = ctahr_absolute_path + 'ctahr/stats.json'

## REGULATION FIXED VALUES ##
# Temperature thresholds
temp_target = 12
delta_targ_H = 1
delta_targ_L = 0.2
delta_ext_H = 2
delta_ext_L = 1
delta_freeze_H = 3
delta_freeze_L = 1

# Daily airing
daily_period = 86400
daily_airing_time = 3600

# Hygrometry thresholds
hygro_target_winter = 75
hygro_target_summer= 85
delta_hygro = 5

## POWER VALUES ##
fan_power = 100
heater_power = 1500
dehum_power = 600
