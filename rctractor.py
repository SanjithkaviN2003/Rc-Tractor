import pigpio
import time

pi = pigpio.pi()

pwm_pin_direction = 3
pwm_pin_speed = 2

pi.set_mode(pwm_pin_direction, pigpio.INPUT)
pi.set_mode(pwm_pin_speed, pigpio.INPUT)

STBY = 23
AIN1 = 24
AIN2 = 25
PWMA = 18  # Motor A PWM for forward/backward
BIN1 = 17
BIN2 = 27
PWMB = 22  # Motor B PWM for left/right

pi.set_mode(STBY, pigpio.OUTPUT)
pi.set_mode(AIN1, pigpio.OUTPUT)
pi.set_mode(AIN2, pigpio.OUTPUT)
pi.set_mode(PWMA, pigpio.OUTPUT)
pi.set_mode(BIN1, pigpio.OUTPUT)
pi.set_mode(BIN2, pigpio.OUTPUT)
pi.set_mode(PWMB, pigpio.OUTPUT)

# Mapping function to scale PWM values
def map_value(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Callback functions to capture PWM pulse widths
speed_pulse_width = 0
direction_pulse_width = 0
start_time = None

def speed_callback(gpio, level, tick):
    global speed_pulse_width,start_time

    if level == pigpio.HIGH:
        start_time = tick

    elif level == pigpio.LOW and start_time is not None:
        pulse_width = tick - start_time
        
        pwm_value = int((pulse_width - 1000) * 255 / (2000 - 1000))
        
        speed_pulse_width = max(0, min(255, pwm_value))
        
        print(f"Pulse width: {pulse_width} microseconds, Mapped PWM Value speed: {speed_pulse_width}")

def direction_callback(gpio, level, tick):
    global direction_pulse_width,start_time

    if level == pigpio.HIGH:
        start_time = tick

    elif level == pigpio.LOW and start_time is not None:
        pulse_width = tick - start_time
        
        pwm_value = int((pulse_width - 1000) * 255 / (2000 - 1000))
        
        direction_pulse_width = max(0, min(255, pwm_value))
        
        print(f"Pulse width: {pulse_width} microseconds, Mapped PWM Value dir: {direction_pulse_width}")


# Attach callbacks
pi.callback(pwm_pin_speed, pigpio.EITHER_EDGE, speed_callback)
pi.callback(pwm_pin_direction, pigpio.EITHER_EDGE, direction_callback)


def control_motors():
    # Map speed PWM values from 130–255 to 1–255
    if (speed_pulse_width >= 130 and speed_pulse_width <= 255):
        speed_forward = map_value(speed_pulse_width, 130, 235, 1, 255)

            # Forward control
        if speed_pulse_width > 130:
            pi.write(STBY, 1)
            pi.write(AIN1, 0)
            pi.write(AIN2, 1)
            pi.write(BIN1, 1)
            pi.write(BIN2, 0)
            pi.set_PWM_dutycycle(PWMA, speed_forward)
            pi.set_PWM_dutycycle(PWMB, speed_forward)
             

        if direction_pulse_width <= 120 and direction_pulse_width >= 0:
            speed_left = map_value(direction_pulse_width,120,0,150,255)
            
            #left cotrol
            if direction_pulse_width < 120:
                pi.write(STBY, 1)
                pi.write(AIN1, 0)
                pi.write(AIN2, 1)
                pi.write(BIN1, 1)
                pi.write(BIN2, 0)
                pi.set_PWM_dutycycle(PWMA,speed_left)
                pi.set_PWM_dutycycle(PWMB,speed_forward)

        if  direction_pulse_width >= 130 and direction_pulse_width <= 255:
            speed_right = map_value(direction_pulse_width,130,235,150,255)

            #right control
            if direction_pulse_width > 130:
                pi.write(STBY, 1)
                pi.write(AIN1, 0)
                pi.write(AIN2, 1)
                pi.write(BIN1, 1)
                pi.write(BIN2, 0)
                pi.set_PWM_dutycycle(PWMA,speed_forward)
                pi.set_PWM_dutycycle(PWMB,speed_right)
        
    elif (speed_pulse_width <= 120 and speed_pulse_width >= 1): 
        speed_reverse = map_value(speed_pulse_width,120,20,1,255)
           
        #Reverse
        if speed_pulse_width < 120:
            pi.write(STBY, 1)
            pi.write(AIN1, 1)
            pi.write(AIN2, 0)
            pi.write(BIN1, 0)
            pi.write(BIN2, 1)
            pi.set_PWM_dutycycle(PWMA, speed_reverse)
            pi.set_PWM_dutycycle(PWMB, speed_reverse)


        if direction_pulse_width <= 120 and direction_pulse_width >= 0:
            speed_left = map_value(direction_pulse_width,120,0,150,255)
            
            #left cotrol
            if direction_pulse_width < 120:
                pi.write(STBY, 1)
                pi.write(AIN1, 1)
                pi.write(AIN2, 0)
                pi.write(BIN1, 0)
                pi.write(BIN2, 1)
                pi.set_PWM_dutycycle(PWMA,speed_left)
                pi.set_PWM_dutycycle(PWMB,speed_reverse)

        if  direction_pulse_width >= 130 and direction_pulse_width <= 255:
            speed_right = map_value(direction_pulse_width,130,235,150,255)

            #right control
            if direction_pulse_width > 130:
                pi.write(STBY, 1)
                pi.write(AIN1, 1)
                pi.write(AIN2, 0)
                pi.write(BIN1, 0)
                pi.write(BIN2, 1)
                pi.set_PWM_dutycycle(PWMA,speed_reverse)
                pi.set_PWM_dutycycle(PWMB,speed_right)



    else:
        pi.write(STBY, 0)

#    # Map direction PWM values as needed
#    if direction_pulse_width >= 130 and direction_pulse_width <= 255:
#        speed_left = map_value(direction_pulse_width, 130, 135, 1, 255)
#
#        # Left
#        if direction_pulse_width > 130:
#            pi.write(BIN1, 1)
#            pi.write(BIN2, 0)
#            pi.set_PWM_dutycycle(PWMB, speed_left)
#        elif direction_pulse_width < 1500:
#            pi.write(BIN1, 0)
#            pi.write(BIN2, 1)
#            pi.set_PWM_dutycycle(PWMB, mapped_direction)

# Main loop
try:
    pi.write(STBY, 1)
    while True:
        control_motors()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting program.")

finally:
    pi.write(STBY, 0)
    pi.set_PWM_dutycycle(PWMA, 0)
    pi.set_PWM_dutycycle(PWMB, 0)
    pi.stop()
