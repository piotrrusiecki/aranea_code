import time

def routine_patrol():
    from command_dispatcher_symbolic import execute_symbolic  # Delayed import

    def look_around():
        execute_symbolic("task_look_left")
        time.sleep(0.3)
        execute_symbolic("task_look_right")
        time.sleep(0.3)
        execute_symbolic("task_look_up")
        time.sleep(0.2)

    look_around()
    execute_symbolic("task_step_forward")
    time.sleep(0.6)

    look_around()
    execute_symbolic("task_step_forward")
    time.sleep(0.6)

    execute_symbolic("routine_turn_left")
    time.sleep(1.0)
    look_around()

    execute_symbolic("routine_turn_right")
    time.sleep(1.0)
    look_around()
