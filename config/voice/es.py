# es.py

command_map = {
    "paso": "task_step_forward",
    "paso atrás": "task_step_back",
    "paso izquierda": "task_step_left",
    "paso derecha": "task_step_right",

    "marcha": "routine_march_forward",
    "marcha izquierda": "routine_march_left",
    "marcha derecha": "routine_march_right",
    "marcha atrás": "routine_march_back",

    "corre": "routine_run_forward",
    "corre izquierda": "routine_run_left",
    "corre derecha": "routine_run_right",
    "corre atrás": "routine_run_back",

    "gira izquierda": "routine_turn_left",
    "gira derecha": "routine_turn_right",

    "inclina adelante": "task_attitude_forward",
    "inclina atrás": "task_attitude_back",
    "inclina izquierda": "task_attitude_left",
    "inclina derecha": "task_attitude_right",

    "desliza izquierda": "task_shift_left",
    "desliza derecha": "task_shift_right",
    "desliza atrás": "task_shift_back",
    "desliza adelante": "task_shift_forward",

    "mira adelante": "sys_reset_head",
    "mira izquierda": "task_look_left",
    "mira derecha": "task_look_right",
    "mira arriba": "task_look_up",
    "mira abajo": "task_look_down",

    "relájate": "task_servo_off",
    "despierta": "task_servo_on",

    "luz roja": "task_light_red",
    "luz verde": "task_light_green",
    "luz azul": "task_light_blue",
    "luz apaga": "task_light_off",

    "evita": "sys_start_sonic",
    "ciego": "sys_stop_sonic",

    "para": "sys_stop_motion",
    "patrulla": "routine_patrol",

    "araña alemán": "language_DE",
    "araña inglés": "language_EN",
    "araña esperanto": "language_EO",
    "araña español": "language_ES",
    "araña francés": "language_FR",
    "araña hindi": "language_HI",
    "araña polaco": "language_PL",
    "araña portugués": "language_PT"
}
