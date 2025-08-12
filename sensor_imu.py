#coding:utf-8
import math
import logging
from mpu6050 import mpu6050

logger = logging.getLogger("sensor.imu")

class Kalman_filter:
    def __init__(self, process_noise_covariance, measurement_noise_covariance):
        self.process_noise_covariance = process_noise_covariance  # Process noise covariance (Q)
        self.measurement_noise_covariance = measurement_noise_covariance  # Measurement noise covariance (R)
        self.estimated_error_covariance = 1  # Initial estimate error covariance (P_k_k1)
        self.kalman_gain = 0  # Kalman gain (Kg)
        self.posterior_error_covariance = 1  # Posterior estimate error covariance (P_k1_k1)
        self.posterior_estimate = 0  # Posterior estimate of state (x_k_k1)
        self.previous_adc_value = 0  # Previous ADC value
        self.current_measurement = 0  # Current measurement (Z_k)
        self.previous_kalman_output = 0  # Previous Kalman filter output

    def kalman(self, adc_value):
        self.current_measurement = adc_value
        # Handle large changes in ADC value
        if abs(self.previous_kalman_output - adc_value) >= 60:
            self.posterior_estimate = adc_value * 0.400 + self.previous_kalman_output * 0.600
        else:
            self.posterior_estimate = self.previous_kalman_output
        # Update estimate error covariance (P_k_k1 = P_k1_k1 + Q)
        self.estimated_error_covariance = self.posterior_error_covariance + self.process_noise_covariance
        # Calculate Kalman gain (Kg = P_k_k1 / (P_k_k1 + R))
        self.kalman_gain = self.estimated_error_covariance / (self.estimated_error_covariance + self.measurement_noise_covariance)
        # Calculate Kalman filter output (x_k_k1 = x_k1_k1 + Kg * (Z_k - x_k1_k1))
        kalman_output = self.posterior_estimate + self.kalman_gain * (self.current_measurement - self.previous_kalman_output)
        # Update posterior estimate error covariance (P_k1_k1 = (1 - Kg) * P_k_k1)
        self.posterior_error_covariance = (1 - self.kalman_gain) * self.estimated_error_covariance
        # Update previous Kalman filter output
        self.previous_kalman_output = kalman_output
        return kalman_output

class IMU:
    def __init__(self):
        self.proportional_gain = 100 
        self.integral_gain = 0.002 
        self.half_time_step = 0.001 

        self.quaternion_w = 1
        self.quaternion_x = 0
        self.quaternion_y = 0
        self.quaternion_z = 0

        self.integral_error_x = 0
        self.integral_error_y = 0
        self.integral_error_z = 0
        self.pitch_angle = 0
        self.roll_angle = 0
        self.yaw_angle = 0
    
        try:
            self.sensor = mpu6050(address=0x68, bus=1) 
            self.sensor.set_accel_range(mpu6050.ACCEL_RANGE_2G)   
            self.sensor.set_gyro_range(mpu6050.GYRO_RANGE_250DEG)  
            logger.info("MPU6050 IMU initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize MPU6050 IMU: %s", e)
            raise
    
        self.kalman_filter_AX = Kalman_filter(0.001, 0.1)
        self.kalman_filter_AY = Kalman_filter(0.001, 0.1)
        self.kalman_filter_AZ = Kalman_filter(0.001, 0.1)

        self.kalman_filter_GX = Kalman_filter(0.001, 0.1)
        self.kalman_filter_GY = Kalman_filter(0.001, 0.1)
        self.kalman_filter_GZ = Kalman_filter(0.001, 0.1)
    
        logger.info("Starting IMU calibration (100 samples)...")
        self.error_accel_data, self.error_gyro_data = self.calculate_average_sensor_data()
        logger.info("IMU calibration completed")
    
    def calculate_average_sensor_data(self):
        accel_x_sum = 0
        accel_y_sum = 0
        accel_z_sum = 0
        
        gyro_x_sum = 0
        gyro_y_sum = 0
        gyro_z_sum = 0
        
        for i in range(100):
            try:
                accel_data = self.sensor.get_accel_data()   
                gyro_data = self.sensor.get_gyro_data()      
                
                accel_x_sum += accel_data['x']
                accel_y_sum += accel_data['y']
                accel_z_sum += accel_data['z']
                
                gyro_x_sum += gyro_data['x']
                gyro_y_sum += gyro_data['y']
                gyro_z_sum += gyro_data['z']
                
                if i % 20 == 0:  # Log progress every 20 samples
                    logger.debug("IMU calibration progress: %d%%", i)
            except Exception as e:
                logger.error("Error during IMU calibration sample %d: %s", i, e)
                continue
            
        accel_x_avg = accel_x_sum / 100
        accel_y_avg = accel_y_sum / 100
        accel_z_avg = accel_z_sum / 100
        
        gyro_x_avg = gyro_x_sum / 100
        gyro_y_avg = gyro_y_sum / 100
        gyro_z_avg = gyro_z_sum / 100
        
        accel_data = {'x': accel_x_avg, 'y': accel_y_avg, 'z': accel_z_avg - 9.8}
        gyro_data = {'x': gyro_x_avg, 'y': gyro_y_avg, 'z': gyro_z_avg}
        
        logger.debug("IMU calibration averages - Accel: x=%.3f, y=%.3f, z=%.3f", 
                    accel_x_avg, accel_y_avg, accel_z_avg)
        logger.debug("IMU calibration averages - Gyro: x=%.3f, y=%.3f, z=%.3f", 
                    gyro_x_avg, gyro_y_avg, gyro_z_avg)
        
        return accel_data, gyro_data

    def get_sensor_data(self):
        try:
            accel_data = self.sensor.get_accel_data()   
            gyro_data = self.sensor.get_gyro_data()      
            
            # Apply Kalman filtering
            filtered_accel_x = self.kalman_filter_AX.kalman(accel_data['x'])
            filtered_accel_y = self.kalman_filter_AY.kalman(accel_data['y'])
            filtered_accel_z = self.kalman_filter_AZ.kalman(accel_data['z'])
            
            filtered_gyro_x = self.kalman_filter_GX.kalman(gyro_data['x'])
            filtered_gyro_y = self.kalman_filter_GY.kalman(gyro_data['y'])
            filtered_gyro_z = self.kalman_filter_GZ.kalman(gyro_data['z'])
            
            # Calculate angles
            self.roll_angle = math.atan2(filtered_accel_y, filtered_accel_z) * 180 / math.pi
            self.pitch_angle = math.atan2(-filtered_accel_x, math.hypot(filtered_accel_y, filtered_accel_z)) * 180 / math.pi
            
            # Integrate gyro for yaw (simplified)
            self.yaw_angle += filtered_gyro_z * self.half_time_step
            
            logger.debug("IMU data - Roll: %.2f°, Pitch: %.2f°, Yaw: %.2f°", 
                        self.roll_angle, self.pitch_angle, self.yaw_angle)
            
            return {
                'roll': self.roll_angle,
                'pitch': self.pitch_angle,
                'yaw': self.yaw_angle,
                'accel': {'x': filtered_accel_x, 'y': filtered_accel_y, 'z': filtered_accel_z},
                'gyro': {'x': filtered_gyro_x, 'y': filtered_gyro_y, 'z': filtered_gyro_z}
            }
        except Exception as e:
            logger.error("Failed to get IMU sensor data: %s", e)
            return None

    def get_angles(self):
        """Get current roll, pitch, and yaw angles."""
        try:
            data = self.get_sensor_data()
            if data:
                return data['roll'], data['pitch'], data['yaw']
            else:
                return 0.0, 0.0, 0.0
        except Exception as e:
            logger.error("Failed to get IMU angles: %s", e)
            return 0.0, 0.0, 0.0

    def update_imu_state(self):
        """Update IMU state and return (pitch, roll, yaw) angles.
        This method is required for compatibility with the original codebase."""
        try:
            accel_data = self.sensor.get_accel_data()    
            gyro_data = self.sensor.get_gyro_data() 
            
            accel_x = self.kalman_filter_AX.kalman(accel_data['x'] - self.error_accel_data['x'])
            accel_y = self.kalman_filter_AY.kalman(accel_data['y'] - self.error_accel_data['y'])
            accel_z = self.kalman_filter_AZ.kalman(accel_data['z'] - self.error_accel_data['z'])
            gyro_x = self.kalman_filter_GX.kalman(gyro_data['x'] - self.error_gyro_data['x'])
            gyro_y = self.kalman_filter_GY.kalman(gyro_data['y'] - self.error_gyro_data['y'])
            gyro_z = self.kalman_filter_GZ.kalman(gyro_data['z'] - self.error_gyro_data['z'])

            accel_norm = math.sqrt(accel_x * accel_x + accel_y * accel_y + accel_z * accel_z)
            
            accel_x /= accel_norm
            accel_y /= accel_norm
            accel_z /= accel_norm
            
            quat_vx = 2 * (self.quaternion_x * self.quaternion_z - self.quaternion_w * self.quaternion_y)
            quat_vy = 2 * (self.quaternion_w * self.quaternion_x + self.quaternion_y * self.quaternion_z)
            quat_vz = self.quaternion_w * self.quaternion_w - self.quaternion_x * self.quaternion_x - self.quaternion_y * self.quaternion_y + self.quaternion_z * self.quaternion_z
            
            error_x = (accel_y * quat_vz - accel_z * quat_vy)
            error_y = (accel_z * quat_vx - accel_x * quat_vz)
            error_z = (accel_x * quat_vy - accel_y * quat_vx)
            
            self.integral_error_x += error_x * self.integral_gain
            self.integral_error_y += error_y * self.integral_gain
            self.integral_error_z += error_z * self.integral_gain
            
            gyro_x += self.proportional_gain * error_x + self.integral_error_x
            gyro_y += self.proportional_gain * error_y + self.integral_error_y
            gyro_z += self.proportional_gain * error_z + self.integral_error_z
            
            self.quaternion_w += (-self.quaternion_x * gyro_x - self.quaternion_y * gyro_y - self.quaternion_z * gyro_z) * self.half_time_step
            self.quaternion_x += (self.quaternion_w * gyro_x + self.quaternion_y * gyro_z - self.quaternion_z * gyro_y) * self.half_time_step
            self.quaternion_y += (self.quaternion_w * gyro_y - self.quaternion_x * gyro_z + self.quaternion_z * gyro_x) * self.half_time_step
            self.quaternion_z += (self.quaternion_w * gyro_z + self.quaternion_x * gyro_y - self.quaternion_y * self.quaternion_x) * self.half_time_step
            
            norm = math.sqrt(self.quaternion_w * self.quaternion_w + self.quaternion_x * self.quaternion_x + self.quaternion_y * self.quaternion_y + self.quaternion_z * self.quaternion_z)
            self.quaternion_w /= norm
            self.quaternion_x /= norm
            self.quaternion_y /= norm
            self.quaternion_z /= norm
            
            current_pitch = math.asin(-2 * self.quaternion_x * self.quaternion_z + 2 * self.quaternion_w * self.quaternion_y) * 57.3
            current_roll = math.atan2(2 * self.quaternion_y * self.quaternion_z + 2 * self.quaternion_w * self.quaternion_x, -2 * self.quaternion_x * self.quaternion_x - 2 * self.quaternion_y * self.quaternion_y + 1) * 57.3
            current_yaw = math.atan2(2 * (self.quaternion_x * self.quaternion_y + self.quaternion_w * self.quaternion_z), self.quaternion_w * self.quaternion_w + self.quaternion_x * self.quaternion_x - self.quaternion_y * self.quaternion_y - self.quaternion_z * self.quaternion_z) * 57.3
            self.pitch_angle = current_pitch
            self.roll_angle = current_roll
            self.yaw_angle = current_yaw
            
            logger.debug("IMU update - Pitch: %.2f°, Roll: %.2f°, Yaw: %.2f°", 
                        self.pitch_angle, self.roll_angle, self.yaw_angle)
            
            return self.pitch_angle, self.roll_angle, self.yaw_angle
            
        except Exception as e:
            logger.error("Failed to update IMU state: %s", e)
            return 0.0, 0.0, 0.0

    def close(self):  # skipcq: PYL-R0201
        """Close the IMU sensor."""
        try:
            # MPU6050 doesn't have a close method, but we can log the cleanup
            logger.info("IMU sensor cleanup completed")
        except Exception as e:
            logger.error("Error during IMU cleanup: %s", e)
