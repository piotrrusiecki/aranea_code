# eo.py

command_map = {
    "iru": "task_step_forward",
    "iru reen": "task_step_back",
    "iru maldekstren": "task_step_left",
    "iru dekstren": "task_step_right",

    "marŝu": "routine_march_forward",
    "marŝu maldekstren": "routine_march_left",
    "marŝu dekstren": "routine_march_right",
    "marŝu reen": "routine_march_back",

    "kuru": "routine_run_forward",
    "kuru maldekstren": "routine_run_left",
    "kuru dekstren": "routine_run_right",
    "kuru reen": "routine_run_back",

    "turnu maldekstren": "routine_turn_left",
    "turnu dekstren": "routine_turn_right",

    "klinu fronte": "task_attitude_forward",
    "klinu reen": "task_attitude_back",
    "klinu maldekstren": "task_attitude_left",
    "klinu dekstren": "task_attitude_right",

    "movu maldekstren": "task_shift_left",
    "movu dekstren": "task_shift_right",
    "movu reen": "task_shift_back",
    "movu fronte": "task_shift_forward",

    "rigardu fronte": "sys_reset_head",
    "rigardu maldekstren": "task_look_left",
    "rigardu dekstren": "task_look_right",
    "rigardu supren": "task_look_up",
    "rigardu malsupren": "task_look_down",

    "ripozu": "task_servo_off",
    "veku": "task_servo_on",

    "lumigu ruĝe": "task_light_red",
    "lumigu verde": "task_light_green",
    "lumigu blue": "task_light_blue",
    "malŝaltu lumo": "task_light_off",

    "evitu": "sys_start_sonic",
    "blinda": "sys_stop_sonic",

    "haltu": "sys_stop_motion",
    "patrolu": "routine_patrol",

    "araneo germane": "language_DE",
    "araneo angle": "language_EN",
    "araneo esperante": "language_EO",
    "araneo hindie": "language_HI",
    "araneo hispane": "language_ES",
    "araneo france": "language_FR",
    "araneo pole": "language_PL",
    "araneo portugale": "language_PT"
}