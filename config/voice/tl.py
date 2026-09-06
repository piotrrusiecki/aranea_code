# tl.py

command_map = {
    "lakad": "task_step_forward",
    "lakad paatras": "task_step_back",
    "lakad pakaliwa": "task_step_left",
    "lakad pakanan": "task_step_right",

    "martsa": "routine_march_forward",
    "martsa pakaliwa": "routine_march_left",
    "martsa pakanan": "routine_march_right",
    "martsa paatras": "routine_march_back",

    "takbo": "routine_run_forward",
    "takbo pakaliwa": "routine_run_left",
    "takbo pakanan": "routine_run_right",
    "takbo paatras": "routine_run_back",

    "liko pakaliwa": "routine_turn_left",
    "liko pakanan": "routine_turn_right",

    "hilig pasulong": "task_attitude_forward",
    "hilig paatras": "task_attitude_back",
    "hilig pakaliwa": "task_attitude_left",
    "hilig pakanan": "task_attitude_right",

    "usog pakaliwa": "task_shift_left",
    "usog pakanan": "task_shift_right",
    "usog paatras": "task_shift_back",
    "usog pasulong": "task_shift_forward",

    "tingin sa harap": "sys_reset_head",
    "tingin sa kaliwa": "task_look_left",
    "tingin sa kanan": "task_look_right",
    "tingin sa taas": "task_look_up",
    "tingin sa baba": "task_look_down",

    "relaks": "task_servo_off",
    "gising": "task_servo_on",

    "ilaw pula": "led_set_static:255:0:0",
    "ilaw berde": "led_set_static:0:255:0",
    "ilaw asul": "led_set_static:0:0:255",
    "ilaw patay": "led_off",
    "kislap": "led_blink",

    "iwas": "sys_start_sonic",
    "bulag": "sys_stop_sonic",

    "tigil": "sys_stop_motion",
    "patrolya": "routine_patrol",

    "gagamba aleman": "language_DE",
    "gagamba ingles": "language_EN",
    "gagamba esperanto": "language_EO",
    "gagamba espanyol": "language_ES",
    "gagamba pranses": "language_FR",
    "gagamba hindi": "language_HI",
    "gagamba polish": "language_PL",
    "gagamba portuges": "language_PT",
    "gagamba tagalog": "language_TL"
}
