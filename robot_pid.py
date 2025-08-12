#coding:utf-8
import logging

logger = logging.getLogger("robot.pid")

class Incremental_PID:
    ''' PID controller'''
    def __init__(self, P=0.0, I=0.0, D=0.0):
        self.target_value = 0.0
        self.kp = P
        self.ki = I
        self.kd = D
        self.last_error = 0.0
        self.p_error = 0.0
        self.i_error = 0.0
        self.d_error = 0.0
        self.i_saturation = 10.0
        self.output = 0.0
        logger.info("PID controller initialized - P: %.3f, I: %.3f, D: %.3f", P, I, D)

    def pid_calculate(self, feedback_val):
        try:
            error = self.target_value - feedback_val
            self.p_error = self.kp * error
            self.i_error += error 
            self.d_error = self.kd * (error - self.last_error)
            
            # Apply integral saturation
            if (self.i_error < -self.i_saturation):
                self.i_error = -self.i_saturation
                logger.debug("Integral term saturated to lower limit: %.3f", -self.i_saturation)
            elif (self.i_error > self.i_saturation):
                self.i_error = self.i_saturation
                logger.debug("Integral term saturated to upper limit: %.3f", self.i_saturation)
            
            self.output = self.p_error + (self.ki * self.i_error) + self.d_error
            self.last_error = error
            
            logger.debug("PID calculation - target: %.3f, feedback: %.3f, error: %.3f, output: %.3f", 
                        self.target_value, feedback_val, error, self.output)
            logger.debug("PID terms - P: %.3f, I: %.3f, D: %.3f", self.p_error, self.ki * self.i_error, self.d_error)
            
            return self.output
        except Exception as e:
            logger.error("Error in PID calculation: %s", e)
            return 0.0

    def set_kp(self, proportional_gain):
        old_kp = self.kp
        self.kp = proportional_gain
        logger.debug("PID P gain changed: %.3f → %.3f", old_kp, proportional_gain)

    def set_ki(self, integral_gain):
        old_ki = self.ki
        self.ki = integral_gain
        logger.debug("PID I gain changed: %.3f → %.3f", old_ki, integral_gain)

    def set_kd(self, derivative_gain):
        old_kd = self.kd
        self.kd = derivative_gain
        logger.debug("PID D gain changed: %.3f → %.3f", old_kd, derivative_gain)

    def set_i_saturation(self, saturation_val):
        old_saturation = self.i_saturation
        self.i_saturation = saturation_val
        logger.debug("PID integral saturation changed: %.3f → %.3f", old_saturation, saturation_val)

    def set_target_value(self, target):
        old_target = self.target_value
        self.target_value = target
        logger.debug("PID target value changed: %.3f → %.3f", old_target, target)