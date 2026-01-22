"""Modbus register definitions for BIC WRG."""
from __future__ import annotations

from typing import Callable

from .transforms import to_bool, to_temperature

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
REG_NHR_STATE = 116
# Status Gebläse Zuluft (Supply Air Fan Status)
REG_SUPPLY_AIR_FAN_STATUS = 117
# Status Gebläse Abluft (Exhaust Air Fan Status)
REG_EXHAUST_AIR_FAN_STATUS = 118
# EWT Zustand (EWT State)
REG_EWT_STATE = 121
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
REG_TEMP_T1_AFTER_EWT = 200
# T2 nach VHR (T2 after VHR)
REG_TEMP_T2_AFTER_VHR = 201
# T3 vor NE (T3 before NE)
REG_TEMP_T3_BEFORE_NE = 202
# T4 nach NE (T4 after NE)
REG_TEMP_T4_AFTER_NE = 203
# T5 Abluft (T5 exhaust air)
REG_TEMP_T5_EXHAUST_AIR = 204
# T6 im WT (T6 in WT)
REG_TEMP_T6_IN_WT = 205
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
REG_OPERATING_HOURS_VHR = 809
REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE = 810
REG_OPERATING_HOURS_EWT = 813

# Operation mode values
# Betriebsart: 0=Aus, 1=Handbetrieb, 2=Winterbetrieb, 3=Sommerbetrieb, 4=Sommer Abluft
OPERATION_MODE_OFF = 0
OPERATION_MODE_MANUAL = 1
OPERATION_MODE_WINTER = 2
OPERATION_MODE_SUMMER = 3
OPERATION_MODE_SUMMER_EXHAUST = 4

# Fan speed values
# Manuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4, 5=Automatik, 6=Linearbetrieb
FAN_SPEED_OFF = 0
FAN_SPEED_LEVEL_1 = 1
FAN_SPEED_LEVEL_2 = 2
FAN_SPEED_LEVEL_3 = 3
FAN_SPEED_LEVEL_4 = 4
FAN_SPEED_AUTO = 5
FAN_SPEED_LINEAR = 6

# Current fan level values
# Aktuelle Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4

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

# Heat pump status values
# Status Wärmepumpe: 0=Aus, 5=WP Heizen, 49=WP Kühlen
HEAT_PUMP_STATUS_OFF = 0
HEAT_PUMP_STATUS_HEATING = 5
HEAT_PUMP_STATUS_COOLING = 49

# NHR state values
# NHR Zustand: 0=Inaktiv, 1=Aktiv

# Supply air fan status values
# Status Gebläse Zuluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
SUPPLY_AIR_FAN_STATUS_DISABLED = 0
SUPPLY_AIR_FAN_STATUS_STARTUP = 1
SUPPLY_AIR_FAN_STATUS_ACTIVE = 2
SUPPLY_AIR_FAN_STATUS_STANDBY = 5
SUPPLY_AIR_FAN_STATUS_ERROR = 6

# Exhaust air fan status values
# Status Gebläse Abluft: 0=Deaktiviert, 1=Anlaufphase, 2=Aktiv, 5=Standby, 6=Fehler
EXHAUST_AIR_FAN_STATUS_DISABLED = 0
EXHAUST_AIR_FAN_STATUS_STARTUP = 1
EXHAUST_AIR_FAN_STATUS_ACTIVE = 2
EXHAUST_AIR_FAN_STATUS_STANDBY = 5
EXHAUST_AIR_FAN_STATUS_ERROR = 6

# EWT state values
# EWT Zustand: 0=EWT aus/geschlossen, 1=EWT im Heizbetrieb aktiv, 2=EWT im Kühlbetrieb aktiv
EWT_STATE_OFF = 0
EWT_STATE_HEATING = 1
EWT_STATE_COOLING = 2

# Bypass state values
# Bypass Zustand: 0=Bypass geschlossen, 1=Bypass offen (Kühlen), 2=Bypass offen (Heizen)
BYPASS_STATE_CLOSED = 0
BYPASS_STATE_OPEN_COOLING = 1
BYPASS_STATE_OPEN_HEATING = 2

# Outdoor damper state values
# Aussenklappe Zustand: 0=geschlossen, 1=offen
OUTDOOR_DAMPER_STATE_CLOSED = 0
OUTDOOR_DAMPER_STATE_OPEN = 1

# Preheater state values
# Vorheizregister Zustand: 0=Aus, 1=VHR 1 aktiv, 2=VHR 2 aktiv, 3=VHR 1 & 2 aktiv
PREHEATER_STATE_VHR1_ACTIVE = 1
PREHEATER_STATE_VHR2_ACTIVE = 2
PREHEATER_STATE_VHR1_2_ACTIVE = 3

# Time program fan level values
# Luftstufe Zeitprogramm: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4

# Sensor fan level values
# Luftstufe Sensoren: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4

# Heating/Cooling function values
# Heiz-Kühlfunktion: 0=Aus, 1=Heizen, 2=Kühlen, 3=Auto T-Aussen, 4=Auto Digitaler Eingang
HEATING_COOLING_OFF = 0
HEATING_COOLING_HEATING = 1
HEATING_COOLING_COOLING = 2
HEATING_COOLING_AUTO_OUTDOOR = 3
HEATING_COOLING_AUTO_DIGITAL = 4

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

REG_CURRENT_TEMPERATURE_1 = 360
REG_CURRENT_TEMPERATURE_2 = 361
REG_CURRENT_TEMPERATURE_3 = 362
REG_CURRENT_TEMPERATURE_4 = 363
REG_CURRENT_TEMPERATURE_5 = 364
REG_CURRENT_TEMPERATURE_6 = 365
REG_CURRENT_TEMPERATURE_7 = 366
REG_CURRENT_TEMPERATURE_8 = 367
REG_CURRENT_TEMPERATURE_9 = 368
REG_CURRENT_TEMPERATURE_10 = 369
REG_CURRENT_TEMPERATURE_11 = 370
REG_CURRENT_TEMPERATURE_12 = 371
REG_CURRENT_TEMPERATURE_13 = 372
REG_CURRENT_TEMPERATURE_14 = 373
REG_CURRENT_TEMPERATURE_15 = 374
REG_CURRENT_TEMPERATURE_16 = 375
REG_CURRENT_TEMPERATURE_17 = 376

REG_TARGET_TEMPERATURE_1 = 400
REG_TARGET_TEMPERATURE_2 = 401
REG_TARGET_TEMPERATURE_3 = 402
REG_TARGET_TEMPERATURE_4 = 403
REG_TARGET_TEMPERATURE_5 = 404
REG_TARGET_TEMPERATURE_6 = 405
REG_TARGET_TEMPERATURE_7 = 406
REG_TARGET_TEMPERATURE_8 = 407
REG_TARGET_TEMPERATURE_9 = 408
REG_TARGET_TEMPERATURE_10 = 409
REG_TARGET_TEMPERATURE_11 = 410
REG_TARGET_TEMPERATURE_12 = 411
REG_TARGET_TEMPERATURE_13 = 412
REG_TARGET_TEMPERATURE_14 = 413
REG_TARGET_TEMPERATURE_15 = 414
REG_TARGET_TEMPERATURE_16 = 415
REG_TARGET_TEMPERATURE_17 = 416

REG_BASE_TEMPERATURE_1 = 420
REG_BASE_TEMPERATURE_2 = 421
REG_BASE_TEMPERATURE_3 = 422
REG_BASE_TEMPERATURE_4 = 423
REG_BASE_TEMPERATURE_5 = 424
REG_BASE_TEMPERATURE_6 = 425
REG_BASE_TEMPERATURE_7 = 426
REG_BASE_TEMPERATURE_8 = 427
REG_BASE_TEMPERATURE_9 = 428
REG_BASE_TEMPERATURE_10 = 429
REG_BASE_TEMPERATURE_11 = 430
REG_BASE_TEMPERATURE_12 = 431
REG_BASE_TEMPERATURE_13 = 432
REG_BASE_TEMPERATURE_14 = 433
REG_BASE_TEMPERATURE_15 = 434
REG_BASE_TEMPERATURE_16 = 435
REG_BASE_TEMPERATURE_17 = 436

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

REG_HEATING_ACTIVE_1 = 460
REG_HEATING_ACTIVE_2 = 461
REG_HEATING_ACTIVE_3 = 462
REG_HEATING_ACTIVE_4 = 463
REG_HEATING_ACTIVE_5 = 464
REG_HEATING_ACTIVE_6 = 465
REG_HEATING_ACTIVE_7 = 466
REG_HEATING_ACTIVE_8 = 467
REG_HEATING_ACTIVE_9 = 468
REG_HEATING_ACTIVE_10 = 469
REG_HEATING_ACTIVE_11 = 470
REG_HEATING_ACTIVE_12 = 471
REG_HEATING_ACTIVE_13 = 472
REG_HEATING_ACTIVE_14 = 473
REG_HEATING_ACTIVE_15 = 474
REG_HEATING_ACTIVE_16 = 475
REG_HEATING_ACTIVE_17 = 476

REG_SCHEDULED_HEATING_ENABLED_1 = 500
REG_SCHEDULED_HEATING_ENABLED_2 = 501
REG_SCHEDULED_HEATING_ENABLED_3 = 502
REG_SCHEDULED_HEATING_ENABLED_4 = 503
REG_SCHEDULED_HEATING_ENABLED_5 = 504
REG_SCHEDULED_HEATING_ENABLED_6 = 505
REG_SCHEDULED_HEATING_ENABLED_7 = 506
REG_SCHEDULED_HEATING_ENABLED_8 = 507
REG_SCHEDULED_HEATING_ENABLED_9 = 508
REG_SCHEDULED_HEATING_ENABLED_10 = 509
REG_SCHEDULED_HEATING_ENABLED_11 = 510
REG_SCHEDULED_HEATING_ENABLED_12 = 511
REG_SCHEDULED_HEATING_ENABLED_13 = 512
REG_SCHEDULED_HEATING_ENABLED_14 = 513
REG_SCHEDULED_HEATING_ENABLED_15 = 514
REG_SCHEDULED_HEATING_ENABLED_16 = 515
REG_SCHEDULED_HEATING_ENABLED_17 = 516


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
    REG_EWT_STATE: "ewt_state",
    REG_BYPASS_STATE: "bypass_state",
    REG_OUTDOOR_DAMPER_STATE: "outdoor_damper_state",
    REG_PREHEATER_STATE: "preheater_state",
    REG_TIME_PROGRAM_FAN_LEVEL: "time_program_fan_level",
    REG_SENSOR_FAN_LEVEL: "sensor_fan_level",
    REG_CURRENT_SUPPLY_AIR_FLOW: "current_supply_air_flow",
    REG_CURRENT_EXHAUST_AIR_FLOW: "current_exhaust_air_flow",
    REG_CURRENT_SUPPLY_AIR_RPM: "current_supply_air_rpm",
    REG_CURRENT_EXHAUST_AIR_RPM: "current_exhaust_air_rpm",
    REG_TEMP_T1_AFTER_EWT: "temp_t1_after_ewt",
    REG_TEMP_T2_AFTER_VHR: "temp_t2_after_vhr",
    REG_TEMP_T3_BEFORE_NE: "temp_t3_before_ne",
    REG_TEMP_T4_AFTER_NE: "temp_t4_after_ne",
    REG_TEMP_T5_EXHAUST_AIR: "temp_t5_exhaust_air",
    REG_TEMP_T6_IN_WT: "temp_t6_in_wt",
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
    REG_OPERATING_HOURS_VHR: "operating_hours_vhr",
    REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE: "operating_hours_auxiliary_heating_house",
    REG_OPERATING_HOURS_EWT: "operating_hours_ewt",
    # WGT-only registers
    REG_HEAT_PUMP_STATUS: "heat_pump_status",
    REG_NHR_STATE: "nhr_state",
    REG_HEATING_COOLING_FUNCTION: "heating_cooling_function",
    REG_HEAT_PUMP_HEATING_ENABLED: "heat_pump_heating_enabled",
    REG_HEAT_PUMP_COOLING_ENABLED: "heat_pump_cooling_enabled",
    REG_AUXILIARY_HEATING_ENABLED: "auxiliary_heating_enabled",
    REG_CURRENT_TEMPERATURE_1: "current_temperature_1",
    REG_CURRENT_TEMPERATURE_2: "current_temperature_2",
    REG_CURRENT_TEMPERATURE_3: "current_temperature_3",
    REG_CURRENT_TEMPERATURE_4: "current_temperature_4",
    REG_CURRENT_TEMPERATURE_5: "current_temperature_5",
    REG_CURRENT_TEMPERATURE_6: "current_temperature_6",
    REG_CURRENT_TEMPERATURE_7: "current_temperature_7",
    REG_CURRENT_TEMPERATURE_8: "current_temperature_8",
    REG_CURRENT_TEMPERATURE_9: "current_temperature_9",
    REG_CURRENT_TEMPERATURE_10: "current_temperature_10",
    REG_CURRENT_TEMPERATURE_11: "current_temperature_11",
    REG_CURRENT_TEMPERATURE_12: "current_temperature_12",
    REG_CURRENT_TEMPERATURE_13: "current_temperature_13",
    REG_CURRENT_TEMPERATURE_14: "current_temperature_14",
    REG_CURRENT_TEMPERATURE_15: "current_temperature_15",
    REG_CURRENT_TEMPERATURE_16: "current_temperature_16",
    REG_CURRENT_TEMPERATURE_17: "current_temperature_17",
    REG_TARGET_TEMPERATURE_1: "target_temperature_1",
    REG_TARGET_TEMPERATURE_2: "target_temperature_2",
    REG_TARGET_TEMPERATURE_3: "target_temperature_3",
    REG_TARGET_TEMPERATURE_4: "target_temperature_4",
    REG_TARGET_TEMPERATURE_5: "target_temperature_5",
    REG_TARGET_TEMPERATURE_6: "target_temperature_6",
    REG_TARGET_TEMPERATURE_7: "target_temperature_7",
    REG_TARGET_TEMPERATURE_8: "target_temperature_8",
    REG_TARGET_TEMPERATURE_9: "target_temperature_9",
    REG_TARGET_TEMPERATURE_10: "target_temperature_10",
    REG_TARGET_TEMPERATURE_11: "target_temperature_11",
    REG_TARGET_TEMPERATURE_12: "target_temperature_12",
    REG_TARGET_TEMPERATURE_13: "target_temperature_13",
    REG_TARGET_TEMPERATURE_14: "target_temperature_14",
    REG_TARGET_TEMPERATURE_15: "target_temperature_15",
    REG_TARGET_TEMPERATURE_16: "target_temperature_16",
    REG_TARGET_TEMPERATURE_17: "target_temperature_17",
    REG_BASE_TEMPERATURE_1: "base_temperature_1",
    REG_BASE_TEMPERATURE_2: "base_temperature_2",
    REG_BASE_TEMPERATURE_3: "base_temperature_3",
    REG_BASE_TEMPERATURE_4: "base_temperature_4",
    REG_BASE_TEMPERATURE_5: "base_temperature_5",
    REG_BASE_TEMPERATURE_6: "base_temperature_6",
    REG_BASE_TEMPERATURE_7: "base_temperature_7",
    REG_BASE_TEMPERATURE_8: "base_temperature_8",
    REG_BASE_TEMPERATURE_9: "base_temperature_9",
    REG_BASE_TEMPERATURE_10: "base_temperature_10",
    REG_BASE_TEMPERATURE_11: "base_temperature_11",
    REG_BASE_TEMPERATURE_12: "base_temperature_12",
    REG_BASE_TEMPERATURE_13: "base_temperature_13",
    REG_BASE_TEMPERATURE_14: "base_temperature_14",
    REG_BASE_TEMPERATURE_15: "base_temperature_15",
    REG_BASE_TEMPERATURE_16: "base_temperature_16",
    REG_BASE_TEMPERATURE_17: "base_temperature_17",
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
    REG_HEATING_ACTIVE_1: "heating_active_1",
    REG_HEATING_ACTIVE_2: "heating_active_2",
    REG_HEATING_ACTIVE_3: "heating_active_3",
    REG_HEATING_ACTIVE_4: "heating_active_4",
    REG_HEATING_ACTIVE_5: "heating_active_5",
    REG_HEATING_ACTIVE_6: "heating_active_6",
    REG_HEATING_ACTIVE_7: "heating_active_7",
    REG_HEATING_ACTIVE_8: "heating_active_8",
    REG_HEATING_ACTIVE_9: "heating_active_9",
    REG_HEATING_ACTIVE_10: "heating_active_10",
    REG_HEATING_ACTIVE_11: "heating_active_11",
    REG_HEATING_ACTIVE_12: "heating_active_12",
    REG_HEATING_ACTIVE_13: "heating_active_13",
    REG_HEATING_ACTIVE_14: "heating_active_14",
    REG_HEATING_ACTIVE_15: "heating_active_15",
    REG_HEATING_ACTIVE_16: "heating_active_16",
    REG_HEATING_ACTIVE_17: "heating_active_17",
    REG_SCHEDULED_HEATING_ENABLED_1: "scheduled_heating_enabled_1",
    REG_SCHEDULED_HEATING_ENABLED_2: "scheduled_heating_enabled_2",
    REG_SCHEDULED_HEATING_ENABLED_3: "scheduled_heating_enabled_3",
    REG_SCHEDULED_HEATING_ENABLED_4: "scheduled_heating_enabled_4",
    REG_SCHEDULED_HEATING_ENABLED_5: "scheduled_heating_enabled_5",
    REG_SCHEDULED_HEATING_ENABLED_6: "scheduled_heating_enabled_6",
    REG_SCHEDULED_HEATING_ENABLED_7: "scheduled_heating_enabled_7",
    REG_SCHEDULED_HEATING_ENABLED_8: "scheduled_heating_enabled_8",
    REG_SCHEDULED_HEATING_ENABLED_9: "scheduled_heating_enabled_9",
    REG_SCHEDULED_HEATING_ENABLED_10: "scheduled_heating_enabled_10",
    REG_SCHEDULED_HEATING_ENABLED_11: "scheduled_heating_enabled_11",
    REG_SCHEDULED_HEATING_ENABLED_12: "scheduled_heating_enabled_12",
    REG_SCHEDULED_HEATING_ENABLED_13: "scheduled_heating_enabled_13",
    REG_SCHEDULED_HEATING_ENABLED_14: "scheduled_heating_enabled_14",
    REG_SCHEDULED_HEATING_ENABLED_15: "scheduled_heating_enabled_15",
    REG_SCHEDULED_HEATING_ENABLED_16: "scheduled_heating_enabled_16",
    REG_SCHEDULED_HEATING_ENABLED_17: "scheduled_heating_enabled_17",
}



REG_TO_TRANSFORM: dict[int, Callable] = {
    REG_TEMP_T1_AFTER_EWT: to_temperature,
    REG_TEMP_T2_AFTER_VHR: to_temperature,
    REG_TEMP_T3_BEFORE_NE: to_temperature,
    REG_TEMP_T4_AFTER_NE: to_temperature,
    REG_TEMP_T5_EXHAUST_AIR: to_temperature,
    REG_TEMP_T6_IN_WT: to_temperature,
    REG_TEMP_T7_EVAPORATOR: to_temperature,
    REG_TEMP_T8_CONDENSER: to_temperature,
    REG_TEMP_T10_OUTDOOR: to_temperature,
    REG_NHR_STATE: to_bool,
    REG_CURRENT_TEMPERATURE_1: to_temperature,
    REG_CURRENT_TEMPERATURE_2: to_temperature,
    REG_CURRENT_TEMPERATURE_3: to_temperature,
    REG_CURRENT_TEMPERATURE_4: to_temperature,
    REG_CURRENT_TEMPERATURE_5: to_temperature,
    REG_CURRENT_TEMPERATURE_6: to_temperature,
    REG_CURRENT_TEMPERATURE_7: to_temperature,
    REG_CURRENT_TEMPERATURE_8: to_temperature,
    REG_CURRENT_TEMPERATURE_9: to_temperature,
    REG_CURRENT_TEMPERATURE_10: to_temperature,
    REG_CURRENT_TEMPERATURE_11: to_temperature,
    REG_CURRENT_TEMPERATURE_12: to_temperature,
    REG_CURRENT_TEMPERATURE_13: to_temperature,
    REG_CURRENT_TEMPERATURE_14: to_temperature,
    REG_CURRENT_TEMPERATURE_15: to_temperature,
    REG_CURRENT_TEMPERATURE_16: to_temperature,
    REG_CURRENT_TEMPERATURE_17: to_temperature,
    REG_TARGET_TEMPERATURE_1: to_temperature,
    REG_TARGET_TEMPERATURE_2: to_temperature,
    REG_TARGET_TEMPERATURE_3: to_temperature,
    REG_TARGET_TEMPERATURE_4: to_temperature,
    REG_TARGET_TEMPERATURE_5: to_temperature,
    REG_TARGET_TEMPERATURE_6: to_temperature,
    REG_TARGET_TEMPERATURE_7: to_temperature,
    REG_TARGET_TEMPERATURE_8: to_temperature,
    REG_TARGET_TEMPERATURE_9: to_temperature,
    REG_TARGET_TEMPERATURE_10: to_temperature,
    REG_TARGET_TEMPERATURE_11: to_temperature,
    REG_TARGET_TEMPERATURE_12: to_temperature,
    REG_TARGET_TEMPERATURE_13: to_temperature,
    REG_TARGET_TEMPERATURE_14: to_temperature,
    REG_TARGET_TEMPERATURE_15: to_temperature,
    REG_TARGET_TEMPERATURE_16: to_temperature,
    REG_TARGET_TEMPERATURE_17: to_temperature,
    REG_BASE_TEMPERATURE_1: to_temperature,
    REG_BASE_TEMPERATURE_2: to_temperature,
    REG_BASE_TEMPERATURE_3: to_temperature,
    REG_BASE_TEMPERATURE_4: to_temperature,
    REG_BASE_TEMPERATURE_5: to_temperature,
    REG_BASE_TEMPERATURE_6: to_temperature,
    REG_BASE_TEMPERATURE_7: to_temperature,
    REG_BASE_TEMPERATURE_8: to_temperature,
    REG_BASE_TEMPERATURE_9: to_temperature,
    REG_BASE_TEMPERATURE_10: to_temperature,
    REG_BASE_TEMPERATURE_11: to_temperature,
    REG_BASE_TEMPERATURE_12: to_temperature,
    REG_BASE_TEMPERATURE_13: to_temperature,
    REG_BASE_TEMPERATURE_14: to_temperature,
    REG_BASE_TEMPERATURE_15: to_temperature,
    REG_BASE_TEMPERATURE_16: to_temperature,
    REG_BASE_TEMPERATURE_17: to_temperature,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_1: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_2: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_3: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_4: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_5: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_6: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_7: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_8: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_9: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_10: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_11: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_12: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_13: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_14: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_15: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_16: to_bool,
    REG_AUXILIARY_HEATING_ENABLED_ROOM_17: to_bool,
}

def room_reg(base_reg: int, room_number: int) -> int:
    """Get the register address for a given room number."""
    if room_number < 1 or room_number > 17:
        raise ValueError("Room number must be between 1 and 17")
    return base_reg + (room_number - 1)
