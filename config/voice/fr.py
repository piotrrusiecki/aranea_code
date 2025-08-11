# fr.py

command_map = {
    "avance": "task_step_forward",
    "recule": "task_step_back",
    "pas à gauche": "task_step_left",
    "pas à droite": "task_step_right",

    "marche": "routine_march_forward",
    "marche à gauche": "routine_march_left",
    "marche à droite": "routine_march_right",
    "marche arrière": "routine_march_back",

    "cours": "routine_run_forward",
    "cours à gauche": "routine_run_left",
    "cours à droite": "routine_run_right",
    "cours en arrière": "routine_run_back",

    "tourne à gauche": "routine_turn_left",
    "tourne à droite": "routine_turn_right",

    "penche en avant": "task_attitude_forward",
    "penche en arrière": "task_attitude_back",
    "penche à gauche": "task_attitude_left",
    "penche à droite": "task_attitude_right",

    "décale à gauche": "task_shift_left",
    "décale à droite": "task_shift_right",
    "décale en arrière": "task_shift_back",
    "décale en avant": "task_shift_forward",

    "regarde devant": "sys_reset_head",
    "regarde à gauche": "task_look_left",
    "regarde à droite": "task_look_right",
    "regarde en haut": "task_look_up",
    "regarde en bas": "task_look_down",

    "relaxe": "task_servo_off",
    "réveille-toi": "task_servo_on",

    "lumière rouge": "led_set_static:255:0:0",
    "lumière verte": "led_set_static:0:255:0",
    "lumière bleue": "led_set_static:0:0:255",
    "éteins la lumière": "led_off",
    "clignote": "led_blink",

    "évite": "sys_start_sonic",
    "aveugle": "sys_stop_sonic",

    "arrête": "sys_stop_motion",
    "patrouille": "routine_patrol",

    "araignée français": "language_FR",
    "araignée anglais": "language_EN",
    "araignée espéranto": "language_EO",
    "araignée allemand": "language_DE",
    "araignée hindi": "language_HI",
    "araignée espagnol": "language_ES",
    "araignée polonais": "language_PL",
    "araignée portugais": "language_PT"
}
