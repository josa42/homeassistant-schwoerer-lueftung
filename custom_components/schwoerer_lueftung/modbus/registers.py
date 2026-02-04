from __future__ import annotations

# Register addresses
# Betriebsart (Operation Mode)
REG_OPERATION_MODE = 100
# Manuelle Luftstufe (Manual Fan Speed)
REG_FAN_SPEED = 101
# Aktuelle Luftstufe (Current Fan Level)
REG_CURRENT_FAN_LEVEL = 102
# Manuelle Lineare Luftleistung (Manual Linear Fan Power)
REG_LINEAR_FAN_POWER = 103
# Luftstufen Überschreibung (Fan Level Override)
REG_FAN_OVERRIDE = 104
# Zeitprogramm Basis Luftstufe (Time Program Base Fan Level)
REG_TIME_PROGRAM_BASE_LEVEL = 110
# Stoßlüftung (Shock Ventilation)
REG_SHOCK_VENTILATION = 111
# Restlaufzeit Stoßlüftung (Shock Ventilation Remaining Time)
REG_SHOCK_VENTILATION_REMAINING = 112
# Status Wärmepumpe (Heat Pump Status)
REG_HEAT_PUMP_STATUS = 114
# NHR Zustand (NHR State)
REG_REHEATER_STATE = 116
# Status Gebläse Zuluft (Supply Air Fan Status)
REG_SUPPLY_AIR_FAN_STATUS = 117
# Status Gebläse Abluft (Exhaust Air Fan Status)
REG_EXHAUST_AIR_FAN_STATUS = 118
# EWT Zustand (Ground Heat Exchanger State)
REG_GROUND_HEAT_EXCHANGER_STATE = 121
# Bypass Zustand (Bypass State)
REG_BYPASS_STATE = 123
# Aussenklappe Zustand (Outdoor Damper State)
REG_OUTDOOR_DAMPER_STATE = 131
# Vorheizregister Zustand (Preheater State)
REG_PREHEATER_STATE = 133
# Luftstufe Zeitprogramm (Time Program Fan Level)
REG_TIME_PROGRAM_FAN_LEVEL = 140
# Luftstufe Sensoren (Sensor Fan Level)
REG_SENSOR_FAN_LEVEL = 141
# Luftleistung aktuell Zuluft (Current Supply Air Flow)
REG_CURRENT_SUPPLY_AIR_FLOW = 142
# Luftleistung aktuell Abluft (Current Exhaust Air Flow)
REG_CURRENT_EXHAUST_AIR_FLOW = 143
# Aktuelle Drehzahl Zuluft (Current Supply Air RPM)
REG_CURRENT_SUPPLY_AIR_RPM = 144
# Aktuelle Drehzahl Abluft (Current Exhaust Air RPM)
REG_CURRENT_EXHAUST_AIR_RPM = 145

# Temperature registers (all values /10 for actual °C)
# T1 nach EWT (T1 after EWT)
REG_TEMP_T1_AFTER_GROUND_HEAT_EXCHANGER = 200
# T2 nach VHR (T2 after VHR)
REG_TEMP_T2_AFTER_PREHEATING_COIL = 201
# T3 vor NE (T3 before NE)
REG_TEMP_T3_BEFORE_REHEATER = 202
# T4 nach NE (T4 after NE)
REG_TEMP_T4_AFTER_REHEATER = 203
# T5 Abluft (T5 exhaust air)
REG_TEMP_T5_EXHAUST_AIR = 204
# T6 im WT (T6 in WT)
REG_TEMP_T6_IN_HEAT_EXCHANGER = 205
# T7 Verdampfer (T7 evaporator)
REG_TEMP_T7_EVAPORATOR = 206
# T8 Kondensator (T8 condenser)
REG_TEMP_T8_CONDENSER = 207
# T10 Aussen (T10 outdoor)
REG_TEMP_T10_OUTDOOR = 209

# Heiz-Kühlfunktion (Heating/Cooling Function)
REG_HEATING_COOLING_FUNCTION = 230
# Wärmepumpe Heizen (Heat Pump Heating)
REG_HEAT_PUMP_HEATING_ENABLED = 231
# Wärmepumpe Kühlen (Heat Pump Cooling)
REG_HEAT_PUMP_COOLING_ENABLED = 232
# Zusatzheizung Haus (Auxiliary House Heating)
REG_AUXILIARY_HEATING_ENABLED = 234

# Fehlermeldung (Error Message)
REG_ERROR_MESSAGE = 240

# Alarm registers
# Meldung Druckwächter Aktiv (Pressure Switch Active)
REG_ALARM_PRESSURE_SWITCH = 242
# EVU Sperre Aktiv (Utility Lock Active)
REG_ALARM_UTILITY_LOCK = 243
# Tür offen (Door Open)
REG_ALARM_DOOR_OPEN = 244
# Gerätefilter verschmutzt (Device Filter Dirty)
REG_ALARM_DEVICE_FILTER_DIRTY = 245
# Vorgelagerter Filter verschmutzt (Upstream Filter Dirty)
REG_ALARM_UPSTREAM_FILTER_DIRTY = 246
# Niedertarif abgeschaltet (Off-Peak Tariff Disabled)
REG_ALARM_OFF_PEAK_DISABLED = 247
# Versorgungsspannung abgeschaltet (Supply Voltage Disabled)
REG_ALARM_SUPPLY_VOLTAGE_OFF = 248
# Pressostat ausgelöst (Pressure Switch Triggered)
REG_ALARM_PRESSOSTAT_TRIGGERED = 250
# EVU Sperre extern Aktiv (External Utility Lock Active)
REG_ALARM_EXTERNAL_UTILITY_LOCK = 251
# Heizmodul Testbetrieb aktiv (Heating Module Test Active)
REG_ALARM_HEATING_MODULE_TEST = 252
# Notbetrieb aktiv (Emergency Mode Active)
REG_ALARM_EMERGENCY_MODE = 253
# Zuluft zu kalt (Supply Air Too Cold)
REG_ALARM_SUPPLY_AIR_COLD = 254
# Restlaufzeit Gerätefilter (Device Filter Remaining Days)
REG_DEVICE_FILTER_REMAINING = 265
# Restlaufzeit Vorgelagerter Filter (Upstream Filter Remaining Days)
REG_UPSTREAM_FILTER_REMAINING = 263

# Operating hours registers (Betriebsstunden)
REG_OPERATING_HOURS_FAN = 800
REG_OPERATING_HOURS_FAN_LEVEL_1 = 801
REG_OPERATING_HOURS_FAN_LEVEL_2 = 802
REG_OPERATING_HOURS_FAN_LEVEL_3 = 803
REG_OPERATING_HOURS_FAN_LEVEL_4 = 804
REG_OPERATING_HOURS_HEAT_PUMP = 805
REG_OPERATING_HOURS_HEAT_PUMP_COOLING = 806
REG_OPERATING_HOURS_PREHEATING_COIL = 809
REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE = 810
REG_OPERATING_HOURS_GROUND_HEAT_EXCHANGER = 813

# Linear fan power range
# Manuelle Lineare Luftleistung: 30-100%
LINEAR_FAN_POWER_MIN = 30
LINEAR_FAN_POWER_MAX = 100

# Fan override values
# Luftstufen Überschreibung: 0=Inaktiv, 1=Aktiv
FAN_OVERRIDE_ACTIVE = 1

# Time program base level values
# Zeitprogramm Basis Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4

# Shock ventilation values
# Stoßlüftung: 0=Inaktiv, 1=Aktiv
SHOCK_VENTILATION_INACTIVE = 0
SHOCK_VENTILATION_ACTIVE = 1

# Heat pump status enum mapping
# Status Wärmepumpe: 0=Aus, 5=WP Heizen, 49=WP Kühlen
HEAT_PUMP_STATUS_MAP = {
    0: "off",
    5: "heating",
    49: "cooling",
}

# Supply air fan status enum mapping
# Status Gebläse Zuluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
SUPPLY_AIR_FAN_STATUS_MAP = {
    0: "disabled",
    1: "startup",
    2: "active",
    5: "standby",
    6: "error",
}

# Exhaust air fan status enum mapping
# Status Gebläse Abluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
EXHAUST_AIR_FAN_STATUS_MAP = {
    0: "disabled",
    1: "startup",
    2: "active",
    5: "standby",
    6: "error",
}

# Ground heat exchanger state enum mapping
# EWT Zustand: 0=EWT aus/geschlossen, 1=EWT im Heizbetrieb aktiv, 2=EWT im Kühlbetrieb aktiv
GROUND_HEAT_EXCHANGER_STATE_MAP = {
    0: "off",
    1: "heating",
    2: "cooling",
}

# Bypass state enum mapping
# Bypass Zustand: 0=Bypass geschlossen, 1=Bypass offen (Kühlen), 2=Bypass offen (Heizen)
BYPASS_STATE_MAP = {
    0: "closed",
    1: "open_cooling",
    2: "open_heating",
}

# Outdoor damper state values
# Aussenklappe Zustand: 0=geschlossen, 1=offen
OUTDOOR_DAMPER_STATE_CLOSED = 0
OUTDOOR_DAMPER_STATE_OPEN = 1

# Preheater state values
# Vorheizregister Zustand: 0=Aus, 1=VHR 1 aktiv, 2=VHR 2 aktiv, 3=VHR 1 & 2 aktiv
PREHEATER_STATE_PREHEATING_COIL_1_ACTIVE = 1
PREHEATER_STATE_PREHEATING_COIL_2_ACTIVE = 2
PREHEATER_STATE_PREHEATING_COIL_1_2_ACTIVE = 3

# Heat pump heating enable values
# Wärmepumpe Heizen: 0=Heizen Aus, 1=Heizen frei
HEAT_PUMP_HEATING_OFF = 0
HEAT_PUMP_HEATING_ENABLED = 1

# Heat pump cooling enable values
# Wärmepumpe Kühlen: 0=Kühlen Aus, 1=Kühlen frei
HEAT_PUMP_COOLING_OFF = 0
HEAT_PUMP_COOLING_ENABLED = 1

# Auxiliary heating enable values
# Zusatzheizung Haus: 0=Aus, 1=ZH Haus frei
AUXILIARY_HEATING_OFF = 0
AUXILIARY_HEATING_ENABLED = 1

# Alarm values
# All alarms: 0=inaktiv, 1=Meldung steht an
ALARM_ACTIVE = 1

REG_CURRENT_TEMPERATURE_ROOM_1 = 360
REG_CURRENT_TEMPERATURE_ROOM_2 = 361
REG_CURRENT_TEMPERATURE_ROOM_3 = 362
REG_CURRENT_TEMPERATURE_ROOM_4 = 363
REG_CURRENT_TEMPERATURE_ROOM_5 = 364
REG_CURRENT_TEMPERATURE_ROOM_6 = 365
REG_CURRENT_TEMPERATURE_ROOM_7 = 366
REG_CURRENT_TEMPERATURE_ROOM_8 = 367
REG_CURRENT_TEMPERATURE_ROOM_9 = 368
REG_CURRENT_TEMPERATURE_ROOM_10 = 369
REG_CURRENT_TEMPERATURE_ROOM_11 = 370
REG_CURRENT_TEMPERATURE_ROOM_12 = 371
REG_CURRENT_TEMPERATURE_ROOM_13 = 372
REG_CURRENT_TEMPERATURE_ROOM_14 = 373
REG_CURRENT_TEMPERATURE_ROOM_15 = 374
REG_CURRENT_TEMPERATURE_ROOM_16 = 375
REG_CURRENT_TEMPERATURE_ROOM_17 = 376

REG_TARGET_TEMPERATURE_ROOM_1 = 400
REG_TARGET_TEMPERATURE_ROOM_2 = 401
REG_TARGET_TEMPERATURE_ROOM_3 = 402
REG_TARGET_TEMPERATURE_ROOM_4 = 403
REG_TARGET_TEMPERATURE_ROOM_5 = 404
REG_TARGET_TEMPERATURE_ROOM_6 = 405
REG_TARGET_TEMPERATURE_ROOM_7 = 406
REG_TARGET_TEMPERATURE_ROOM_8 = 407
REG_TARGET_TEMPERATURE_ROOM_9 = 408
REG_TARGET_TEMPERATURE_ROOM_10 = 409
REG_TARGET_TEMPERATURE_ROOM_11 = 410
REG_TARGET_TEMPERATURE_ROOM_12 = 411
REG_TARGET_TEMPERATURE_ROOM_13 = 412
REG_TARGET_TEMPERATURE_ROOM_14 = 413
REG_TARGET_TEMPERATURE_ROOM_15 = 414
REG_TARGET_TEMPERATURE_ROOM_16 = 415
REG_TARGET_TEMPERATURE_ROOM_17 = 416

REG_BASE_TEMPERATURE_ROOM_1 = 420
REG_BASE_TEMPERATURE_ROOM_2 = 421
REG_BASE_TEMPERATURE_ROOM_3 = 422
REG_BASE_TEMPERATURE_ROOM_4 = 423
REG_BASE_TEMPERATURE_ROOM_5 = 424
REG_BASE_TEMPERATURE_ROOM_6 = 425
REG_BASE_TEMPERATURE_ROOM_7 = 426
REG_BASE_TEMPERATURE_ROOM_8 = 427
REG_BASE_TEMPERATURE_ROOM_9 = 428
REG_BASE_TEMPERATURE_ROOM_10 = 429
REG_BASE_TEMPERATURE_ROOM_11 = 430
REG_BASE_TEMPERATURE_ROOM_12 = 431
REG_BASE_TEMPERATURE_ROOM_13 = 432
REG_BASE_TEMPERATURE_ROOM_14 = 433
REG_BASE_TEMPERATURE_ROOM_15 = 434
REG_BASE_TEMPERATURE_ROOM_16 = 435
REG_BASE_TEMPERATURE_ROOM_17 = 436

REG_AUXILIARY_HEATING_ENABLED_ROOM_1 = 440
REG_AUXILIARY_HEATING_ENABLED_ROOM_2 = 441
REG_AUXILIARY_HEATING_ENABLED_ROOM_3 = 442
REG_AUXILIARY_HEATING_ENABLED_ROOM_4 = 443
REG_AUXILIARY_HEATING_ENABLED_ROOM_5 = 444
REG_AUXILIARY_HEATING_ENABLED_ROOM_6 = 445
REG_AUXILIARY_HEATING_ENABLED_ROOM_7 = 446
REG_AUXILIARY_HEATING_ENABLED_ROOM_8 = 447
REG_AUXILIARY_HEATING_ENABLED_ROOM_9 = 448
REG_AUXILIARY_HEATING_ENABLED_ROOM_10 = 449
REG_AUXILIARY_HEATING_ENABLED_ROOM_11 = 450
REG_AUXILIARY_HEATING_ENABLED_ROOM_12 = 451
REG_AUXILIARY_HEATING_ENABLED_ROOM_13 = 452
REG_AUXILIARY_HEATING_ENABLED_ROOM_14 = 453
REG_AUXILIARY_HEATING_ENABLED_ROOM_15 = 454
REG_AUXILIARY_HEATING_ENABLED_ROOM_16 = 455
REG_AUXILIARY_HEATING_ENABLED_ROOM_17 = 456

REG_AUXILIARY_HEATING_ACTIVE_ROOM_1 = 460
REG_AUXILIARY_HEATING_ACTIVE_ROOM_2 = 461
REG_AUXILIARY_HEATING_ACTIVE_ROOM_3 = 462
REG_AUXILIARY_HEATING_ACTIVE_ROOM_4 = 463
REG_AUXILIARY_HEATING_ACTIVE_ROOM_5 = 464
REG_AUXILIARY_HEATING_ACTIVE_ROOM_6 = 465
REG_AUXILIARY_HEATING_ACTIVE_ROOM_7 = 466
REG_AUXILIARY_HEATING_ACTIVE_ROOM_8 = 467
REG_AUXILIARY_HEATING_ACTIVE_ROOM_9 = 468
REG_AUXILIARY_HEATING_ACTIVE_ROOM_10 = 469
REG_AUXILIARY_HEATING_ACTIVE_ROOM_11 = 470
REG_AUXILIARY_HEATING_ACTIVE_ROOM_12 = 471
REG_AUXILIARY_HEATING_ACTIVE_ROOM_13 = 472
REG_AUXILIARY_HEATING_ACTIVE_ROOM_14 = 473
REG_AUXILIARY_HEATING_ACTIVE_ROOM_15 = 474
REG_AUXILIARY_HEATING_ACTIVE_ROOM_16 = 475
REG_AUXILIARY_HEATING_ACTIVE_ROOM_17 = 476

REG_SCHEDULED_HEATING_ENABLED_ROOM_1 = 500
REG_SCHEDULED_HEATING_ENABLED_ROOM_2 = 501
REG_SCHEDULED_HEATING_ENABLED_ROOM_3 = 502
REG_SCHEDULED_HEATING_ENABLED_ROOM_4 = 503
REG_SCHEDULED_HEATING_ENABLED_ROOM_5 = 504
REG_SCHEDULED_HEATING_ENABLED_ROOM_6 = 505
REG_SCHEDULED_HEATING_ENABLED_ROOM_7 = 506
REG_SCHEDULED_HEATING_ENABLED_ROOM_8 = 507
REG_SCHEDULED_HEATING_ENABLED_ROOM_9 = 508
REG_SCHEDULED_HEATING_ENABLED_ROOM_10 = 509
REG_SCHEDULED_HEATING_ENABLED_ROOM_11 = 510
REG_SCHEDULED_HEATING_ENABLED_ROOM_12 = 511
REG_SCHEDULED_HEATING_ENABLED_ROOM_13 = 512
REG_SCHEDULED_HEATING_ENABLED_ROOM_14 = 513
REG_SCHEDULED_HEATING_ENABLED_ROOM_15 = 514
REG_SCHEDULED_HEATING_ENABLED_ROOM_16 = 515
REG_SCHEDULED_HEATING_ENABLED_ROOM_17 = 516


REG_KEYS: dict[int, str] = {
    REG_OPERATION_MODE: "operation_mode",
    REG_FAN_SPEED: "fan_speed",
    REG_CURRENT_FAN_LEVEL: "current_fan_level",
    REG_LINEAR_FAN_POWER: "linear_fan_power",
    REG_FAN_OVERRIDE: "fan_override",
    REG_TIME_PROGRAM_BASE_LEVEL: "time_program_base_level",
    REG_SHOCK_VENTILATION: "shock_ventilation",
    REG_SHOCK_VENTILATION_REMAINING: "shock_ventilation_remaining",
    REG_SUPPLY_AIR_FAN_STATUS: "supply_air_fan_status",
    REG_EXHAUST_AIR_FAN_STATUS: "exhaust_air_fan_status",
    REG_GROUND_HEAT_EXCHANGER_STATE: "ground_heat_exchanger_state",
    REG_BYPASS_STATE: "bypass_state",
    REG_OUTDOOR_DAMPER_STATE: "outdoor_damper_state",
    REG_PREHEATER_STATE: "preheater_state",
    REG_TIME_PROGRAM_FAN_LEVEL: "time_program_fan_level",
    REG_SENSOR_FAN_LEVEL: "sensor_fan_level",
    REG_CURRENT_SUPPLY_AIR_FLOW: "current_supply_air_flow",
    REG_CURRENT_EXHAUST_AIR_FLOW: "current_exhaust_air_flow",
    REG_CURRENT_SUPPLY_AIR_RPM: "current_supply_air_rpm",
    REG_CURRENT_EXHAUST_AIR_RPM: "current_exhaust_air_rpm",
    REG_TEMP_T1_AFTER_GROUND_HEAT_EXCHANGER: "temp_t1_after_ground_heat_exchanger",
    REG_TEMP_T2_AFTER_PREHEATING_COIL: "temp_t2_after_preheating_coil",
    REG_TEMP_T3_BEFORE_REHEATER: "temp_t3_before_reheater",
    REG_TEMP_T4_AFTER_REHEATER: "temp_t4_after_reheater",
    REG_TEMP_T5_EXHAUST_AIR: "temp_t5_exhaust_air",
    REG_TEMP_T6_IN_HEAT_EXCHANGER: "temp_t6_in_heat_exchanger",
    REG_TEMP_T7_EVAPORATOR: "temp_t7_evaporator",
    REG_TEMP_T8_CONDENSER: "temp_t8_condenser",
    REG_TEMP_T10_OUTDOOR: "temp_t10_outdoor",
    # Read alarms
    REG_ALARM_PRESSURE_SWITCH: "alarm_pressure_switch",
    REG_ALARM_UTILITY_LOCK: "alarm_utility_lock",
    REG_ALARM_DOOR_OPEN: "alarm_door_open",
    REG_ALARM_DEVICE_FILTER_DIRTY: "alarm_device_filter_dirty",
    REG_ALARM_UPSTREAM_FILTER_DIRTY: "alarm_upstream_filter_dirty",
    REG_ALARM_OFF_PEAK_DISABLED: "alarm_off_peak_disabled",
    REG_ALARM_SUPPLY_VOLTAGE_OFF: "alarm_supply_voltage_off",
    REG_ALARM_PRESSOSTAT_TRIGGERED: "alarm_pressostat_triggered",
    REG_ALARM_EXTERNAL_UTILITY_LOCK: "alarm_external_utility_lock",
    REG_ALARM_HEATING_MODULE_TEST: "alarm_heating_module_test",
    REG_ALARM_EMERGENCY_MODE: "alarm_emergency_mode",
    REG_ALARM_SUPPLY_AIR_COLD: "alarm_supply_air_cold",
    REG_DEVICE_FILTER_REMAINING: "device_filter_remaining",
    REG_UPSTREAM_FILTER_REMAINING: "upstream_filter_remaining",
    REG_ERROR_MESSAGE: "error_message",
    REG_OPERATING_HOURS_FAN: "operating_hours_fan",
    REG_OPERATING_HOURS_FAN_LEVEL_1: "operating_hours_fan_level_1",
    REG_OPERATING_HOURS_FAN_LEVEL_2: "operating_hours_fan_level_2",
    REG_OPERATING_HOURS_FAN_LEVEL_3: "operating_hours_fan_level_3",
    REG_OPERATING_HOURS_FAN_LEVEL_4: "operating_hours_fan_level_4",
    REG_OPERATING_HOURS_HEAT_PUMP: "operating_hours_heat_pump",
    REG_OPERATING_HOURS_HEAT_PUMP_COOLING: "operating_hours_heat_pump_cooling",
    REG_OPERATING_HOURS_PREHEATING_COIL: "operating_hours_preheating_coil",
    REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE: "operating_hours_auxiliary_heating_house",
    REG_OPERATING_HOURS_GROUND_HEAT_EXCHANGER: "operating_hours_ground_heat_exchanger",
    # WGT-only registers
    REG_HEAT_PUMP_STATUS: "heat_pump_status",
    REG_REHEATER_STATE: "reheater_state",
    REG_HEATING_COOLING_FUNCTION: "heating_cooling_function",
    REG_HEAT_PUMP_HEATING_ENABLED: "heat_pump_heating_enabled",
    REG_HEAT_PUMP_COOLING_ENABLED: "heat_pump_cooling_enabled",
    REG_AUXILIARY_HEATING_ENABLED: "auxiliary_heating_enabled",
    REG_CURRENT_TEMPERATURE_ROOM_1: "current_temperature_room_1",
    REG_CURRENT_TEMPERATURE_ROOM_2: "current_temperature_room_2",
    REG_CURRENT_TEMPERATURE_ROOM_3: "current_temperature_room_3",
    REG_CURRENT_TEMPERATURE_ROOM_4: "current_temperature_room_4",
    REG_CURRENT_TEMPERATURE_ROOM_5: "current_temperature_room_5",
    REG_CURRENT_TEMPERATURE_ROOM_6: "current_temperature_room_6",
    REG_CURRENT_TEMPERATURE_ROOM_7: "current_temperature_room_7",
    REG_CURRENT_TEMPERATURE_ROOM_8: "current_temperature_room_8",
    REG_CURRENT_TEMPERATURE_ROOM_9: "current_temperature_room_9",
    REG_CURRENT_TEMPERATURE_ROOM_10: "current_temperature_room_10",
    REG_CURRENT_TEMPERATURE_ROOM_11: "current_temperature_room_11",
    REG_CURRENT_TEMPERATURE_ROOM_12: "current_temperature_room_12",
    REG_CURRENT_TEMPERATURE_ROOM_13: "current_temperature_room_13",
    REG_CURRENT_TEMPERATURE_ROOM_14: "current_temperature_room_14",
    REG_CURRENT_TEMPERATURE_ROOM_15: "current_temperature_room_15",
    REG_CURRENT_TEMPERATURE_ROOM_16: "current_temperature_room_16",
    REG_CURRENT_TEMPERATURE_ROOM_17: "current_temperature_room_17",
    REG_TARGET_TEMPERATURE_ROOM_1: "target_temperature_room_1",
    REG_TARGET_TEMPERATURE_ROOM_2: "target_temperature_room_2",
    REG_TARGET_TEMPERATURE_ROOM_3: "target_temperature_room_3",
    REG_TARGET_TEMPERATURE_ROOM_4: "target_temperature_room_4",
    REG_TARGET_TEMPERATURE_ROOM_5: "target_temperature_room_5",
    REG_TARGET_TEMPERATURE_ROOM_6: "target_temperature_room_6",
    REG_TARGET_TEMPERATURE_ROOM_7: "target_temperature_room_7",
    REG_TARGET_TEMPERATURE_ROOM_8: "target_temperature_room_8",
    REG_TARGET_TEMPERATURE_ROOM_9: "target_temperature_room_9",
    REG_TARGET_TEMPERATURE_ROOM_10: "target_temperature_room_10",
    REG_TARGET_TEMPERATURE_ROOM_11: "target_temperature_room_11",
    REG_TARGET_TEMPERATURE_ROOM_12: "target_temperature_room_12",
    REG_TARGET_TEMPERATURE_ROOM_13: "target_temperature_room_13",
    REG_TARGET_TEMPERATURE_ROOM_14: "target_temperature_room_14",
    REG_TARGET_TEMPERATURE_ROOM_15: "target_temperature_room_15",
    REG_TARGET_TEMPERATURE_ROOM_16: "target_temperature_room_16",
    REG_TARGET_TEMPERATURE_ROOM_17: "target_temperature_room_17",
    REG_BASE_TEMPERATURE_ROOM_1: "base_temperature_room_1",
    REG_BASE_TEMPERATURE_ROOM_2: "base_temperature_room_2",
    REG_BASE_TEMPERATURE_ROOM_3: "base_temperature_room_3",
    REG_BASE_TEMPERATURE_ROOM_4: "base_temperature_room_4",
    REG_BASE_TEMPERATURE_ROOM_5: "base_temperature_room_5",
    REG_BASE_TEMPERATURE_ROOM_6: "base_temperature_room_6",
    REG_BASE_TEMPERATURE_ROOM_7: "base_temperature_room_7",
    REG_BASE_TEMPERATURE_ROOM_8: "base_temperature_room_8",
    REG_BASE_TEMPERATURE_ROOM_9: "base_temperature_room_9",
    REG_BASE_TEMPERATURE_ROOM_10: "base_temperature_room_10",
    REG_BASE_TEMPERATURE_ROOM_11: "base_temperature_room_11",
    REG_BASE_TEMPERATURE_ROOM_12: "base_temperature_room_12",
    REG_BASE_TEMPERATURE_ROOM_13: "base_temperature_room_13",
    REG_BASE_TEMPERATURE_ROOM_14: "base_temperature_room_14",
    REG_BASE_TEMPERATURE_ROOM_15: "base_temperature_room_15",
    REG_BASE_TEMPERATURE_ROOM_16: "base_temperature_room_16",
    REG_BASE_TEMPERATURE_ROOM_17: "base_temperature_room_17",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1: "auxiliary_heating_enabled_room_1",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_2: "auxiliary_heating_enabled_room_2",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_3: "auxiliary_heating_enabled_room_3",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_4: "auxiliary_heating_enabled_room_4",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_5: "auxiliary_heating_enabled_room_5",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_6: "auxiliary_heating_enabled_room_6",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_7: "auxiliary_heating_enabled_room_7",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_8: "auxiliary_heating_enabled_room_8",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_9: "auxiliary_heating_enabled_room_9",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_10: "auxiliary_heating_enabled_room_10",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_11: "auxiliary_heating_enabled_room_11",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_12: "auxiliary_heating_enabled_room_12",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_13: "auxiliary_heating_enabled_room_13",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_14: "auxiliary_heating_enabled_room_14",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_15: "auxiliary_heating_enabled_room_15",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_16: "auxiliary_heating_enabled_room_16",
    REG_AUXILIARY_HEATING_ENABLED_ROOM_17: "auxiliary_heating_enabled_room_17",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_1: "auxiliary_heating_active_room_1",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_2: "auxiliary_heating_active_room_2",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_3: "auxiliary_heating_active_room_3",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_4: "auxiliary_heating_active_room_4",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_5: "auxiliary_heating_active_room_5",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_6: "auxiliary_heating_active_room_6",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_7: "auxiliary_heating_active_room_7",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_8: "auxiliary_heating_active_room_8",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_9: "auxiliary_heating_active_room_9",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_10: "auxiliary_heating_active_room_10",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_11: "auxiliary_heating_active_room_11",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_12: "auxiliary_heating_active_room_12",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_13: "auxiliary_heating_active_room_13",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_14: "auxiliary_heating_active_room_14",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_15: "auxiliary_heating_active_room_15",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_16: "auxiliary_heating_active_room_16",
    REG_AUXILIARY_HEATING_ACTIVE_ROOM_17: "auxiliary_heating_active_room_17",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_1: "scheduled_heating_enabled_room_1",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_2: "scheduled_heating_enabled_room_2",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_3: "scheduled_heating_enabled_room_3",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_4: "scheduled_heating_enabled_room_4",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_5: "scheduled_heating_enabled_room_5",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_6: "scheduled_heating_enabled_room_6",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_7: "scheduled_heating_enabled_room_7",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_8: "scheduled_heating_enabled_room_8",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_9: "scheduled_heating_enabled_room_9",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_10: "scheduled_heating_enabled_room_10",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_11: "scheduled_heating_enabled_room_11",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_12: "scheduled_heating_enabled_room_12",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_13: "scheduled_heating_enabled_room_13",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_14: "scheduled_heating_enabled_room_14",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_15: "scheduled_heating_enabled_room_15",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_16: "scheduled_heating_enabled_room_16",
    REG_SCHEDULED_HEATING_ENABLED_ROOM_17: "scheduled_heating_enabled_room_17",
}

def room_reg(base_reg: int, room_number: int) -> int:
    """Get the register address for a given room number."""
    if room_number < 1 or room_number > 17:
        raise ValueError("Room number must be between 1 and 17")
    return base_reg + (room_number - 1)

# def room_id()
