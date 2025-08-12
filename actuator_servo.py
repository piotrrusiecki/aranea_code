# coding:utf-8
from hardware_pca9685 import PCA9685
import time
import logging
from config import robot_config

logger = logging.getLogger("actuator.servo")

def map_value(value, from_low, from_high, to_low, to_high):
    """Map a value from one range to another."""
    try:
        result = (to_high - to_low) * (value - from_low) / (from_high - from_low) + to_low
        logger.debug("map_value: %.3f [%.3f,%.3f] -> %.3f [%.3f,%.3f]", 
                    value, from_low, from_high, result, to_low, to_high)
        return result
    except ZeroDivisionError:
        logger.warning("map_value: division by zero, returning to_low value %.3f", to_low)
        return to_low
    except Exception as e:
        logger.error("Error in map_value: %s", e)
        return to_low

class Servo:
    def __init__(self):
        try:
            logger.info("Initializing servo controller with PCA9685 boards")
            self.pwm_40 = PCA9685(0x40, debug=True)
            self.pwm_41 = PCA9685(0x41, debug=True)
            # Set the cycle frequency of PWM to 50 Hz
            self.pwm_40.set_pwm_freq(50)
            time.sleep(0.01)
            self.pwm_41.set_pwm_freq(50)
            time.sleep(0.01)
            logger.info("Servo controller initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize servo controller: %s", e)
            raise

    def set_servo_angle(self, channel, angle):
        """
        Convert the input angle to the value of PCA9685 and set the servo angle.
        
        :param channel: Servo channel (0-31)
        :param angle: Angle in degrees (0-180)
        """
        try:
            if not (0 <= channel <= 31):
                logger.error("Invalid servo channel: %d (must be 0-31)", channel)
                return
            
            if not (0 <= angle <= 180):
                logger.warning("Servo angle out of range: %d (clamping to 0-180)", angle)
                angle = max(0, min(180, angle))
            
            if channel < 16:
                duty_cycle = map_value(angle, 0, 180, 500, 2500)
                duty_cycle = map_value(duty_cycle, 0, 20000, 0, 4095)
                if robot_config.DEBUG_LEGS:
                    logger.debug("Setting servo %d (pwm_41) to angle %d°, duty_cycle %d", 
                                channel, angle, int(duty_cycle))
                self.pwm_41.set_pwm(channel, 0, int(duty_cycle))
            elif 16 <= channel < 32:
                channel -= 16
                duty_cycle = map_value(angle, 0, 180, 500, 2500)
                duty_cycle = map_value(duty_cycle, 0, 20000, 0, 4095)
                if robot_config.DEBUG_LEGS:
                    logger.debug("Setting servo %d (pwm_40) to angle %d°, duty_cycle %d", 
                                channel + 16, angle, int(duty_cycle))
                self.pwm_40.set_pwm(channel, 0, int(duty_cycle))
        except Exception as e:
            logger.error("Failed to set servo %d to angle %d°: %s", channel, angle, e)

    def relax(self):
        """Relax all servos by setting their PWM values to 4096."""
        try:
            logger.info("Relaxing all servos")
            # Relax all channels on both PCA9685 boards
            for channel in range(32):
                if channel < 16:
                    self.pwm_41.set_pwm(channel, 4096, 4096)
                else:
                    self.pwm_40.set_pwm(channel - 16, 4096, 4096)
            logger.info("All servos relaxed")
        except Exception as e:
            logger.error("Failed to relax servos: %s", e)

    def close(self):
        """Close the servo controller."""
        try:
            logger.info("Closing servo controller")
            self.pwm_40.close()
            self.pwm_41.close()
            logger.info("Servo controller closed")
        except Exception as e:
            logger.error("Error closing servo controller: %s", e)


# Main program logic follows:
if __name__ == '__main__':
    logger.info("Starting servo test program")
    logger.info("Now servos will rotate to certain angles")
    logger.info("Please keep the program running when installing the servos")
    logger.info("After that, you can press ctrl-C to end the program")
    
    try:
        servo = Servo()
        while True:
            try:
                for servo_channel in range(32):
                    if servo_channel in [10, 13, 31]:
                        servo.set_servo_angle(servo_channel, 10)
                    elif servo_channel in [18, 21, 27]:
                        servo.set_servo_angle(servo_channel, 170)
                    else:
                        servo.set_servo_angle(servo_channel, 90)
                time.sleep(3)
            except KeyboardInterrupt:
                logger.info("Servo test program ended by user")
                logger.info("End of program")
                servo.relax()
                servo.close()
                break
    except Exception as e:
        logger.error("Error in servo test program: %s", e)