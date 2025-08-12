from gpiozero import DistanceSensor, PWMSoftwareFallback, DistanceSensorNoEcho
import warnings
import time
import threading
import logging

logger = logging.getLogger("sensor.ultrasonic")

class Ultrasonic:
    def __init__(self, trigger_pin: int = 27, echo_pin: int = 22, max_distance: float = 3.0):
        self.thread = None
        self.stop_event = threading.Event()
        # Initialize the Ultrasonic class and set up the distance sensor.
        warnings.filterwarnings("ignore", category = DistanceSensorNoEcho)
        warnings.filterwarnings("ignore", category = PWMSoftwareFallback)  # Ignore PWM software fallback warnings
        self.trigger_pin = trigger_pin  # Set the trigger pin number
        self.echo_pin = echo_pin        # Set the echo pin number
        self.max_distance = max_distance  # Set the maximum distance
        
        try:
            self.sensor = DistanceSensor(echo=self.echo_pin, trigger=self.trigger_pin, max_distance=self.max_distance)  # Initialize the distance sensor
            logger.info("Ultrasonic sensor initialized - trigger: %d, echo: %d, max_distance: %.1fm", 
                       trigger_pin, echo_pin, max_distance)
        except Exception as e:
            logger.error("Failed to initialize ultrasonic sensor: %s", e)
            raise

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None
        self.stop_event.clear()
        logger.debug("Ultrasonic sensor thread stopped")
    
    @property
    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    def start_distance_loop(self, interval=0.5):
        logger.info("Starting ultrasonic distance monitoring loop (interval: %.1fs)", interval)
        self.stop()

        def loop():
            logger.debug("Ultrasonic monitoring loop started")
            while not self.stop_event.is_set():
                try:
                    measured_distance = self.get_distance()
                    if measured_distance is not None:
                        logger.debug("Distance: %.1fcm", measured_distance)
                    time.sleep(interval)
                except Exception as e:
                    logger.error("Error in ultrasonic monitoring loop: %s", e)
                    time.sleep(interval)
            logger.debug("Ultrasonic monitoring loop stopped")

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.close()

    def get_distance(self) -> float:
        """
        Get the distance measurement from the ultrasonic sensor.

        Returns:
        float: The distance measurement in centimeters, rounded to one decimal place.
        """
        try:
            sensor_distance = self.sensor.distance * 100  # Get the distance in centimeters
            result = round(float(sensor_distance), 1)  # Return the distance rounded to one decimal place
            logger.debug("Raw distance: %.3fm, converted: %.1fcm", sensor_distance, result)
            return result
        except RuntimeWarning as e:
            logger.warning("Runtime warning in distance measurement: %s", e)
            return None
        except Exception as e:
            logger.error("Failed to get distance measurement: %s", e)
            return None

    def close(self):
        # Close the distance sensor.
        try:
            self.sensor.close()  # Close the sensor to release resources
            logger.info("Ultrasonic sensor closed")
        except Exception as e:
            logger.error("Error closing ultrasonic sensor: %s", e)

if __name__ == '__main__':
    # Initialize the Ultrasonic instance with default pin numbers and max distance
    logger.info("Ultrasonic sensor test started")
    with Ultrasonic() as ultrasonic:
        try:
            while True:
                current_distance = ultrasonic.get_distance()  # Get the distance measurement in centimeters
                if current_distance is not None:
                    logger.info("Ultrasonic distance: %.1fcm", current_distance)  # Print the distance measurement
                time.sleep(0.5)  # Wait for 0.5 seconds
        except KeyboardInterrupt:  # Handle keyboard interrupt (Ctrl+C)
            logger.info("Ultrasonic sensor test ended by user")  # Print an end message