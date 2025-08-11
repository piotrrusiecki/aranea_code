# pt.py

command_map = {
    "passo": "task_step_forward",
    "passo atrás": "task_step_back",
    "passo esquerda": "task_step_left",
    "passo direita": "task_step_right",

    "marcha": "routine_march_forward",
    "marcha esquerda": "routine_march_left",
    "marcha direita": "routine_march_right",
    "marcha atrás": "routine_march_back",

    "corre": "routine_run_forward",
    "corre esquerda": "routine_run_left",
    "corre direita": "routine_run_right",
    "corre atrás": "routine_run_back",

    "vira esquerda": "routine_turn_left",
    "vira direita": "routine_turn_right",

    "inclina frente": "task_attitude_forward",
    "inclina atrás": "task_attitude_back",
    "inclina esquerda": "task_attitude_left",
    "inclina direita": "task_attitude_right",

    "desliza esquerda": "task_shift_left",
    "desliza direita": "task_shift_right",
    "desliza atrás": "task_shift_back",
    "desliza frente": "task_shift_forward",

    "olha frente": "sys_reset_head",
    "olha esquerda": "task_look_left",
    "olha direita": "task_look_right",
    "olha cima": "task_look_up",
    "olha baixo": "task_look_down",

    "relaxe": "task_servo_off",
    "acorde": "task_servo_on",

    "luz vermelha": "led_set_static:255:0:0",
    "luz verde": "led_set_static:0:255:0",
    "luz azul": "led_set_static:0:0:255",
    "luz apaga": "led_off",
    "pisca": "led_blink",

    "evite": "sys_start_sonic",
    "cego": "sys_stop_sonic",

    "para": "sys_stop_motion",
    "patrulha": "routine_patrol",

    "aranha alemão": "language_DE",
    "aranha inglês": "language_EN",
    "aranha esperanto": "language_EO",
    "aranha espanhol": "language_ES",
    "aranha francês": "language_FR",
    "aranha hindi": "language_HI",
    "aranha polonês": "language_PL",
    "aranha português": "language_PT"
}
