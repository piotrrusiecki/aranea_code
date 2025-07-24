# voice_config.py

command_map = {
    "iru": "CMD_MOVE#1#0#35#8#0",
    "iru reen": "CMD_MOVE#1#0#-35#8#0",
    "iru maldekstren": "CMD_MOVE#1#-35#0#8#0",
    "iru dekstren": "CMD_MOVE#1#35#0#8#0",

    "turnu maldekstren": [
        "CMD_MOVE#1#5#5#8#-10", "CMD_MOVE#1#-5#0#8#-10",
        "CMD_MOVE#1#5#-5#8#-10", "CMD_MOVE#1#-5#-5#8#-10"
    ],
    "turnu dekstren": [
        "CMD_MOVE#1#5#5#8#10", "CMD_MOVE#1#-5#0#8#10",
        "CMD_MOVE#1#5#-5#8#10", "CMD_MOVE#1#-5#-5#8#10"
    ],
    "turnu iomete maldekstren": "CMD_MOVE#1#5#-5#8#-10",
    "turnu iomete dekstren": "CMD_MOVE#1#5#-5#8#10",

    "klinu fronte": "CMD_ATTITUDE#0#15#-2",
    "klinu reen": "CMD_ATTITUDE#0#-15#-2",
    "klinu maldekstren": "CMD_ATTITUDE#-15#0#-2",
    "klinu dekstren": "CMD_ATTITUDE#15#0#-2",

    "rigardu fronte": ["CMD_HEAD#0#90", "CMD_HEAD#1#90"],
    "rigardu maldekstren": "CMD_HEAD#1#135",
    "rigardu dekstren": "CMD_HEAD#1#45",
    "rigardu supren": "CMD_HEAD#0#180",
    "rigardu malsupren": "CMD_HEAD#0#50",

    "ripozu": "CMD_SERVOPOWER#0",
    "veku": "CMD_SERVOPOWER#1",

    "movu maldekstren": "CMD_POSITION#-40#0#0",
    "movu dekstren": "CMD_POSITION#40#0#0",
    "movu reen": "CMD_POSITION#0#-40#0",
    "movu fronte": "CMD_POSITION#0#40#0",

    "lumigu ruĝe": "CMD_LED#255#0#0",
    "lumigu verde": "CMD_LED#0#255#0",
    "lumigu blue": "CMD_LED#0#0#255",
    "malŝaltu lumo": "CMD_LED#0#0#0",

    "evitu": "START_SONIC_MODE",
    "blinda": "STOP_SONIC_MODE",

    "marŝu": "START_MARCH",
    "marŝu maldekstren": "START_MARCH_LEFT",
    "marŝu dekstren": "START_MARCH_RIGHT",
    "marŝu reen": "START_MARCH_BACK",

    "kuru": "START_RUN",
    "kuru maldekstren": "START_RUN_LEFT",
    "kuru dekstren": "START_RUN_RIGHT",
    "kuru reen": "START_RUN_BACK",

    "haltu": "STOP_MOTION_LOOP"
}

model_path = "/home/piotr/Aranea_code/robot_voice_model"
samplerate = 44100
blocksize = 4000