# test_servo.py
import time
import logging
import threading
from actuator_servo import Servo

logger = logging.getLogger("test.servo")

# Global state for servo test loop
_servo_test_running = False
_servo_test_thread = None
_servo_test_lock = threading.Lock()

def start_servo_test():
    """Start a continuous servo test loop in a background thread."""
    global _servo_test_running, _servo_test_thread
    
    with _servo_test_lock:
        if _servo_test_running:
            logger.warning("Servo test is already running")
            return
        
        _servo_test_running = True
        _servo_test_thread = threading.Thread(target=_servo_test_loop, daemon=True)
        _servo_test_thread.start()
        logger.info("Servo test loop started")

def stop_servo_test():
    """Stop the continuous servo test loop."""
    global _servo_test_running
    
    with _servo_test_lock:
        if not _servo_test_running:
            logger.warning("Servo test is not running")
            return
        
        _servo_test_running = False
        logger.info("Servo test loop stopped")

def _servo_test_loop():
    """Background thread function for continuous servo testing."""
    global _servo_test_running
    logger.info("Servo test loop thread started")
    
    try:
        servo = Servo()
        logger.info("Servo controller initialized for test loop")
        
        while _servo_test_running:
            # Test each servo channel in sequence
            for i in range(32):
                if not _servo_test_running:
                    break
                    
                # Move to center position
                servo.set_servo_angle(i, 90)
                time.sleep(0.1)
                
                if not _servo_test_running:
                    break
                    
                # Move to left position
                servo.set_servo_angle(i, 45)
                time.sleep(0.1)
                
                if not _servo_test_running:
                    break
                    
                # Move to right position
                servo.set_servo_angle(i, 135)
                time.sleep(0.1)
                
                if not _servo_test_running:
                    break
                    
                # Return to center
                servo.set_servo_angle(i, 90)
                time.sleep(0.1)
            
            # Small pause between cycles
            if _servo_test_running:
                time.sleep(1)
        
        # Clean up when loop ends
        servo.relax()
        servo.close()
        logger.info("Servo test loop thread ended")
        
    except Exception as e:
        logger.error("Error in servo test loop: %s", e)
        _servo_test_running = False

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
