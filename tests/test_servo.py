# test_servo.py
import time
import logging
from actuator_servo import Servo

logger = logging.getLogger("test.servo")

def test_servo_movement():
    """Test servo movement for all channels."""
    logger.info("Starting servo movement test")
    
    try:
        servo = Servo()
        logger.info("Servo controller initialized successfully")
        
        # Test each servo channel
        for i in range(32):
            angle = 90  # Center position
            logger.debug("Testing servo %2d | angle: %3d", i, angle)
            servo.set_servo_angle(i, angle)
            time.sleep(0.1)  # Small delay between servos
        
        logger.info("All servos moved to center position")
        time.sleep(2)  # Hold position for 2 seconds
        
        # Move to different positions
        for i in range(32):
            if i % 2 == 0:
                angle = 45  # Left position
            else:
                angle = 135  # Right position
            logger.debug("Testing servo %2d | angle: %3d", i, angle)
            servo.set_servo_angle(i, angle)
            time.sleep(0.1)
        
        logger.info("Servos moved to alternate positions")
        time.sleep(2)
        
        # Return to center
        for i in range(32):
            angle = 90
            logger.debug("Testing servo %2d | angle: %3d", i, angle)
            servo.set_servo_angle(i, angle)
            time.sleep(0.1)
        
        logger.info("All servos returned to center position")
        time.sleep(1)
        
        # Relax all servos
        servo.relax()
        logger.info("All servos relaxed")
        
        servo.close()
        logger.info("Servo test completed successfully")
        
    except Exception as e:
        logger.error("Error during servo test: %s", e)
        raise

if __name__ == "__main__":
    # Configure logging for test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s'
    )
    
    test_servo_movement()
