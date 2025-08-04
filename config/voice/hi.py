# hi.py

command_map = {
    "aage badho": "task_step_forward",
    "peeche jao": "task_step_back",
    "baaye mud": "task_step_left",
    "daaye mud": "task_step_right",

    "march karo": "routine_march_forward",
    "baaye march karo": "routine_march_left",
    "daaye march karo": "routine_march_right",
    "peeche march karo": "routine_march_back",

    "daudo": "routine_run_forward",
    "baaye daudo": "routine_run_left",
    "daaye daudo": "routine_run_right",
    "peeche daudo": "routine_run_back",

    "baaye ghoomo": "routine_turn_left",
    "daaye ghoomo": "routine_turn_right",

    "jhuk jao aage": "task_attitude_forward",
    "jhuko peeche": "task_attitude_back",
    "jhuko baaye": "task_attitude_left",
    "jhuko daaye": "task_attitude_right",

    "sarak baaye": "task_shift_left",
    "sarak daaye": "task_shift_right",
    "sarako peeche": "task_shift_back",
    "sarako aage": "task_shift_forward",

    "seedha dekho": "sys_reset_head",
    "baaye dekho": "task_look_left",
    "daaye dekho": "task_look_right",
    "upar dekho": "task_look_up",
    "neeche dekho": "task_look_down",

    "aaraam karo": "task_servo_off",
    "jago": "task_servo_on",

    "laal roshni": "task_light_red",
    "hara roshni": "task_light_green",
    "neela roshni": "task_light_blue",
    "band roshni": "task_light_off",

    "bachao": "sys_start_sonic",
    "andha": "sys_stop_sonic",

    "ruk jao": "sys_stop_motion",
    "nigrani karo": "routine_patrol",

    "makhi hindi": "language_HI",
    "makhi angrezi": "language_EN",
    "makhi esperanto": "language_EO",
    "makhi german": "language_DE",
    "makhi spanish": "language_ES",
    "makhi french": "language_FR",
    "makhi polish": "language_PL",
    "makhi portuguese": "language_PT"
}
