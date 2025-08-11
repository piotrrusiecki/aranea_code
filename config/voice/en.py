# en.py

command_map = {
    "go": "task_step_forward",
    "go back": "task_step_back",
    "go left": "task_step_left",
    "go right": "task_step_right",

    "march": "routine_march_forward",
    "march left": "routine_march_left",
    "march right": "routine_march_right",
    "march back": "routine_march_back",

    "run": "routine_run_forward",
    "run left": "routine_run_left",
    "run right": "routine_run_right",
    "run back": "routine_run_back",

    "turn left": "routine_turn_left",
    "turn right": "routine_turn_right",

    "tilt forward": "task_attitude_forward",
    "tilt back": "task_attitude_back",
    "tilt left": "task_attitude_left",
    "tilt right": "task_attitude_right",

    "shift left": "task_shift_left",
    "shift right": "task_shift_right",
    "shift back": "task_shift_back",
    "shift forward": "task_shift_forward",

    "look forward": "sys_reset_head",
    "look left": "task_look_left",
    "look right": "task_look_right",
    "look up": "task_look_up",
    "look down": "task_look_down",

    "relax": "task_servo_off",
    "wake up": "task_servo_on",

    "light red": "led_set_static:255:0:0",
    "light green": "led_set_static:0:255:0",
    "light blue": "led_set_static:0:0:255",
    "light off": "led_off",

    "avoid": "sys_start_sonic",
    "blind": "sys_stop_sonic",

    "stop": "sys_stop_motion",
    "patrol": "routine_patrol",

    "spider german": "language_DE",
    "spider english": "language_EN",
    "spider esperanto": "language_EO",
    "spider spanish": "language_ES",
    "spider french": "language_FR",
    "spider hindi": "language_HI",
    "spider polish": "language_PL",
    "spider portugese": "language_PT"
}