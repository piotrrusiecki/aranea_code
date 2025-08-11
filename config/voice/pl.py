# pl.py

command_map = {
    "krok": "task_step_forward",
    "krok w tył": "task_step_back",
    "krok w lewo": "task_step_left",
    "krok w prawo": "task_step_right",

    "maszeruj": "routine_march_forward",
    "maszeruj w lewo": "routine_march_left",
    "maszeruj w prawo": "routine_march_right",
    "maszeruj w tył": "routine_march_back",

    "biegnij": "routine_run_forward",
    "biegnij w lewo": "routine_run_left",
    "biegnij w prawo": "routine_run_right",
    "biegnij w tył": "routine_run_back",

    "skręć w lewo": "routine_turn_left",
    "skręć w prawo": "routine_turn_right",

    "pochyl się do przodu": "task_attitude_forward",
    "pochyl się do tyłu": "task_attitude_back",
    "pochyl się w lewo": "task_attitude_left",
    "pochyl się w prawo": "task_attitude_right",

    "przesuń w lewo": "task_shift_left",
    "przesuń w prawo": "task_shift_right",
    "przesuń w tył": "task_shift_back",
    "przesuń do przodu": "task_shift_forward",

    "patrz przed siebie": "sys_reset_head",
    "patrz w lewo": "task_look_left",
    "patrz w prawo": "task_look_right",
    "patrz w górę": "task_look_up",
    "patrz w dół": "task_look_down",

    "relaks": "task_servo_off",
    "obudź się": "task_servo_on",

    "światło czerwone": "led_set_static:255:0:0",
    "światło zielone": "led_set_static:0:255:0",
    "światło niebieskie": "led_set_static:0:0:255",
    "zgaś światło": "led_off",
    "migaj": "led_blink",

    "unikaj": "sys_start_sonic",
    "ślepy": "sys_stop_sonic",

    "stop": "sys_stop_motion",
    "patroluj": "routine_patrol",

    "pająk po polsku": "language_PL",
    "pająk po angielsku": "language_EN",
    "pająk w esperanto": "language_EO",
    "pająk po niemiecku": "language_DE",
    "pająk po hindusku": "language_HI",
    "pająk po hiszpańsku": "language_ES",
    "pająk po francusku": "language_FR",
    "pająk po portugalsku": "language_PT"
}
