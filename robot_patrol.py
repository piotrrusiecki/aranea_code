import time
import logging

logger = logging.getLogger("robot.patrol")

def routine_patrol():
    from command_dispatcher_symbolic import execute_symbolic  # Delayed import

    def look_around():
        logger.debug("Starting look around sequence")
        execute_symbolic("task_look_left")
        time.sleep(0.3)
        execute_symbolic("task_look_right")
        time.sleep(0.3)
        execute_symbolic("task_look_up")
        time.sleep(0.2)
        logger.debug("Look around sequence completed")

    logger.info("Starting patrol routine")
    
    try:
        look_around()
        execute_symbolic("task_step_forward")
        time.sleep(0.6)
        logger.debug("First patrol step completed")

        look_around()
        execute_symbolic("task_step_forward")
        time.sleep(0.6)
        logger.debug("Second patrol step completed")

        execute_symbolic("routine_turn_left")
        time.sleep(1.0)
        look_around()
        logger.debug("Left turn and look completed")

        execute_symbolic("routine_turn_right")
        time.sleep(1.0)
        look_around()
        logger.debug("Right turn and look completed")
        
        logger.info("Patrol routine completed successfully")
    except Exception as e:
        logger.error("Error during patrol routine: %s", e)
        raise
