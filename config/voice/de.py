# de.py

command_map = {
    "schritt": "task_step_forward",
    "schritt zurück": "task_step_back",
    "schritt links": "task_step_left",
    "schritt rechts": "task_step_right",

    "marschieren": "routine_march_forward",
    "marschieren links": "routine_march_left",
    "marschieren rechts": "routine_march_right",
    "marschieren zurück": "routine_march_back",

    "lauf": "routine_run_forward",
    "lauf links": "routine_run_left",
    "lauf rechts": "routine_run_right",
    "lauf zurück": "routine_run_back",

    "dreh links": "routine_turn_left",
    "dreh rechts": "routine_turn_right",

    "neige vor": "task_attitude_forward",
    "neige zurück": "task_attitude_back",
    "neige links": "task_attitude_left",
    "neige rechts": "task_attitude_right",

    "verschiebe links": "task_shift_left",
    "verschiebe rechts": "task_shift_right",
    "verschiebe zurück": "task_shift_back",
    "verschiebe vor": "task_shift_forward",

    "schau geradeaus": "sys_reset_head",
    "schau links": "task_look_left",
    "schau rechts": "task_look_right",
    "schau hoch": "task_look_up",
    "schau runter": "task_look_down",

    "relax": "task_servo_off",
    "aufwachen": "task_servo_on",

    "licht rot": "led_set_static:255:0:0",
    "licht grün": "led_set_static:0:255:0",
    "licht blau": "led_set_static:0:0:255",
    "licht aus": "led_off",
    "blinken": "led_blink",

    "vermeiden": "sys_start_sonic",
    "blind": "sys_stop_sonic",

    "stopp": "sys_stop_motion",
    "patrouilliere": "routine_patrol",

    "spinne deutsch": "language_DE",
    "spinne englisch": "language_EN",
    "spinne esperanto": "language_EO",
    "spinne spanisch": "language_ES",
    "spinne französisch": "language_FR",
    "spinne hindi": "language_HI",
    "spinne polnisch": "language_PL",
    "spinne portugiesisch": "language_PT"
}
