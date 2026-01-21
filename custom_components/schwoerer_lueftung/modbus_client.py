"""Modbus TCP client for BIC WRG."""
from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

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
REG_HEAT_PUMP_HEATING_ENABLE = 231
# Wärmepumpe Kühlen (Heat Pump Cooling)
REG_HEAT_PUMP_COOLING_ENABLE = 232
# Zusatzheizung Haus (Auxiliary House Heating)
REG_AUXILIARY_HEATING_ENABLE = 234

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
CURRENT_FAN_LEVEL_OFF = 0
CURRENT_FAN_LEVEL_1 = 1
CURRENT_FAN_LEVEL_2 = 2
CURRENT_FAN_LEVEL_3 = 3
CURRENT_FAN_LEVEL_4 = 4

# Linear fan power range
# Manuelle Lineare Luftleistung: 30-100%
LINEAR_FAN_POWER_MIN = 30
LINEAR_FAN_POWER_MAX = 100

# Fan override values
# Luftstufen Überschreibung: 0=Inaktiv, 1=Aktiv
FAN_OVERRIDE_INACTIVE = 0
FAN_OVERRIDE_ACTIVE = 1

# Time program base level values
# Zeitprogramm Basis Luftstufe: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
TIME_PROGRAM_BASE_LEVEL_OFF = 0
TIME_PROGRAM_BASE_LEVEL_1 = 1
TIME_PROGRAM_BASE_LEVEL_2 = 2
TIME_PROGRAM_BASE_LEVEL_3 = 3
TIME_PROGRAM_BASE_LEVEL_4 = 4

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
NHR_STATE_INACTIVE = 0
NHR_STATE_ACTIVE = 1

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
PREHEATER_STATE_OFF = 0
PREHEATER_STATE_VHR1_ACTIVE = 1
PREHEATER_STATE_VHR2_ACTIVE = 2
PREHEATER_STATE_VHR1_2_ACTIVE = 3

# Time program fan level values
# Luftstufe Zeitprogramm: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
TIME_PROGRAM_FAN_LEVEL_OFF = 0
TIME_PROGRAM_FAN_LEVEL_1 = 1
TIME_PROGRAM_FAN_LEVEL_2 = 2
TIME_PROGRAM_FAN_LEVEL_3 = 3
TIME_PROGRAM_FAN_LEVEL_4 = 4

# Sensor fan level values
# Luftstufe Sensoren: 0=Aus, 1=Stufe 1, 2=Stufe 2, 3=Stufe 3, 4=Stufe 4
SENSOR_FAN_LEVEL_OFF = 0
SENSOR_FAN_LEVEL_1 = 1
SENSOR_FAN_LEVEL_2 = 2
SENSOR_FAN_LEVEL_3 = 3
SENSOR_FAN_LEVEL_4 = 4

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
ALARM_INACTIVE = 0
ALARM_ACTIVE = 1

# Error codes mapping
# Fehlermeldung: Error code to description
ERROR_CODES = {
    0: "No Error",
    257: "Supply Air Fan Speed Missing",
    258: "Exhaust Air Fan Speed Missing",
    259: "Supply Air Fan Minimum Speed Not Reached",
    260: "Exhaust Air Fan Minimum Speed Not Reached",
    261: "Supply Air Fan Maximum Speed Exceeded",
    262: "Exhaust Air Fan Maximum Speed Exceeded",
    513: "Communication Error with BDE",
    514: "Communication Error Auxiliary Control Unit",
    515: "Communication Error Heating Module",
    516: "Communication Error Sensor",
    517: "Communication Error Sensor Adapter",
    518: "Communication Receiver",
    770: "Error Sensor Element T1 After EWT",
    771: "Error Sensor Element T2 After VHR",
    772: "Error Sensor Element T3 Before NHR",
    773: "Error Sensor Element T4 After NHR",
    774: "Error Sensor Element T5 Exhaust Air",
    775: "Error Sensor Element T6 In WT",
    776: "Error Sensor Element T7 Evaporator",
    777: "Error Sensor Element T8 Condenser",
    779: "Error Sensor Element T10 Outdoor Temperature",
    1025: "Error Parameter Memory",
    1026: "Error System Bus",
    1281: "Heat Pump High Pressure",
    1282: "Heat Pump Low Pressure",
    1283: "Maximum Defrost Time Exceeded",
    1284: "Heat Pump Low Pressure in Cooling Mode",
}


class ModbusClient:
    """Modbus TCP client for WRG device."""

    def __init__(self, host: str, port: int, slave_id: int, device_type: str = "wgt") -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.device_type = device_type
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=5,
            retries=3,
        )

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        return self._client.connect()

    def disconnect(self) -> None:
        """Disconnect from the Modbus device."""
        self._client.close()

    def is_connected(self) -> bool:
        """Check if connected to the Modbus device."""
        return self._client.is_socket_open()


    # async def async_read_register(
    #     self, address: int, count: int = 1
    # ) -> int | None:
    #     """Read holding registers from the device."""
    #     try:
    #         result = self._client.read_holding_registers(address=address, count=count)
    #         if result.isError():
    #             _LOGGER.error("Error reading registers at %s: %s", address, result)
    #             return None
    #         _LOGGER.info("Read registers at %s: %s", address, result.registers)
    #         return result.registers[0] if result.registers else None
    #     except ModbusException as err:
    #         _LOGGER.error("Modbus exception reading registers: %s", err)
    #         return None
    #     except Exception as err:
    #         _LOGGER.error("Unexpected error reading registers at %s: %s", address, err)
    #         return None

    def read_register(
        self, address: int, count: int = 1
    ) -> int | None:
        """Read holding registers from the device."""
        try:
            result = self._client.read_holding_registers(address=address, count=count)
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            _LOGGER.info("Read registers at %s: %s", address, result.registers)
            return result.registers[0] if result.registers else None
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading registers: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error reading registers at %s: %s", address, err)
            return None

    def read_temperature_register(self, address: int) -> float | None:
        """Read temperature holding registers from the device."""
        value = self.read_register(address, 1)
        if value is not None:
            return int.from_bytes(value.to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None



    def read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers from the device."""
        try:
            result = self._client.read_holding_registers(address=address, count=count)
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            _LOGGER.info("Read registers at %s: %s", address, result.registers)
            return result.registers
        except ModbusException as err:
            _LOGGER.error("Modbus exception reading registers: %s", err)
            return None
        except Exception as err:
            _LOGGER.error("Unexpected error reading registers at %s: %s", address, err)
            return None

    def write_register(self, address: int, value: int) -> bool:
        """Write a single register to the device using Write Multiple Registers (16)."""
        try:
            # Device requires Write Multiple Registers (16), not Write Single Register (06)
            result = self._client.write_registers(
                address=address, values=[value]
            )
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error writing register at %s: %s", address, err)
            return False


    def read_fan_speed(self) -> int | None:
        """Read manual fan speed (Manuelle Luftstufe)."""
        registers = self.read_holding_registers(REG_FAN_SPEED, 1)
        if registers:
            return registers[0]
        return None

    def write_fan_speed(self, speed: int) -> bool:
        """Write manual fan speed (Manuelle Luftstufe)."""
        return self.write_register(REG_FAN_SPEED, speed)

    def write_linear_fan_power(self, power: int) -> bool:
        """Write manual linear fan power (Manuelle Lineare Luftleistung)."""
        # Validate range 30-100
        if power < LINEAR_FAN_POWER_MIN or power > LINEAR_FAN_POWER_MAX:
            _LOGGER.error(
                "Linear fan power %d out of range (%d-%d)",
                power,
                LINEAR_FAN_POWER_MIN,
                LINEAR_FAN_POWER_MAX,
            )
            return False
        return self.write_register(REG_LINEAR_FAN_POWER, power)

    def read_fan_override(self) -> int | None:
        """Read fan level override (Luftstufen Überschreibung)."""
        registers = self.read_holding_registers(REG_FAN_OVERRIDE, 1)
        if registers:
            return registers[0]
        return None

    def read_time_program_base_level(self) -> int | None:
        """Read time program base fan level (Zeitprogramm Basis Luftstufe)."""
        registers = self.read_holding_registers(REG_TIME_PROGRAM_BASE_LEVEL, 1)
        if registers:
            return registers[0]
        return None

    def read_shock_ventilation(self) -> int | None:
        """Read shock ventilation (Stoßlüftung)."""
        registers = self.read_holding_registers(REG_SHOCK_VENTILATION, 1)
        if registers:
            return registers[0]
        return None

    def write_shock_ventilation(self, active: int) -> bool:
        """Write shock ventilation (Stoßlüftung)."""
        return self.write_register(REG_SHOCK_VENTILATION, active)

    def read_shock_ventilation_remaining(self) -> int | None:
        """Read shock ventilation remaining time (Restlaufzeit Stoßlüftung)."""
        registers = self.read_holding_registers(REG_SHOCK_VENTILATION_REMAINING, 1)
        if registers:
            return registers[0]
        return None

    def read_heat_pump_status(self) -> int | None:
        """Read heat pump status (Status Wärmepumpe)."""
        registers = self.read_holding_registers(REG_HEAT_PUMP_STATUS, 1)
        if registers:
            return registers[0]
        return None

    def read_nhr_state(self) -> int | None:
        """Read NHR state (NHR Zustand)."""
        registers = self.read_holding_registers(REG_NHR_STATE, 1)
        if registers:
            return registers[0]
        return None

    def read_supply_air_fan_status(self) -> int | None:
        """Read supply air fan status (Status Gebläse Zuluft)."""
        registers = self.read_holding_registers(REG_SUPPLY_AIR_FAN_STATUS, 1)
        if registers:
            return registers[0]
        return None

    def read_exhaust_air_fan_status(self) -> int | None:
        """Read exhaust air fan status (Status Gebläse Abluft)."""
        registers = self.read_holding_registers(REG_EXHAUST_AIR_FAN_STATUS, 1)
        if registers:
            return registers[0]
        return None

    def read_ewt_state(self) -> int | None:
        """Read EWT state (EWT Zustand)."""
        registers = self.read_holding_registers(REG_EWT_STATE, 1)
        if registers:
            return registers[0]
        return None

    def read_bypass_state(self) -> int | None:
        """Read bypass state (Bypass Zustand)."""
        registers = self.read_holding_registers(REG_BYPASS_STATE, 1)
        if registers:
            return registers[0]
        return None

    def read_outdoor_damper_state(self) -> int | None:
        """Read outdoor damper state (Aussenklappe Zustand)."""
        registers = self.read_holding_registers(REG_OUTDOOR_DAMPER_STATE, 1)
        if registers:
            return registers[0]
        return None

    def read_preheater_state(self) -> int | None:
        """Read preheater state (Vorheizregister Zustand)."""
        registers = self.read_holding_registers(REG_PREHEATER_STATE, 1)
        if registers:
            return registers[0]
        return None

    def read_time_program_fan_level(self) -> int | None:
        """Read time program fan level (Luftstufe Zeitprogramm)."""
        registers = self.read_holding_registers(REG_TIME_PROGRAM_FAN_LEVEL, 1)
        if registers:
            return registers[0]
        return None

    def read_sensor_fan_level(self) -> int | None:
        """Read sensor fan level (Luftstufe Sensoren)."""
        registers = self.read_holding_registers(REG_SENSOR_FAN_LEVEL, 1)
        if registers:
            return registers[0]
        return None

    def read_current_supply_air_flow(self) -> int | None:
        """Read current supply air flow (Luftleistung aktuell Zuluft)."""
        registers = self.read_holding_registers(REG_CURRENT_SUPPLY_AIR_FLOW, 1)
        if registers:
            return registers[0]
        return None

    def read_current_exhaust_air_flow(self) -> int | None:
        """Read current exhaust air flow (Luftleistung aktuell Abluft)."""
        registers = self.read_holding_registers(REG_CURRENT_EXHAUST_AIR_FLOW, 1)
        if registers:
            return registers[0]
        return None

    def read_current_supply_air_rpm(self) -> int | None:
        """Read current supply air RPM (Aktuelle Drehzahl Zuluft)."""
        registers = self.read_holding_registers(REG_CURRENT_SUPPLY_AIR_RPM, 1)
        if registers:
            return registers[0]
        return None

    def read_current_exhaust_air_rpm(self) -> int | None:
        """Read current exhaust air RPM (Aktuelle Drehzahl Abluft)."""
        registers = self.read_holding_registers(REG_CURRENT_EXHAUST_AIR_RPM, 1)
        if registers:
            return registers[0]
        return None

    def read_temperature_t1_after_ewt(self) -> float | None:
        """Read temperature T1 after EWT (T1 nach EWT)."""
        registers = self.read_holding_registers(REG_TEMP_T1_AFTER_EWT, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t2_after_vhr(self) -> float | None:
        """Read temperature T2 after VHR (T2 nach VHR)."""
        registers = self.read_holding_registers(REG_TEMP_T2_AFTER_VHR, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t3_before_ne(self) -> float | None:
        """Read temperature T3 before NE (T3 vor NE)."""
        registers = self.read_holding_registers(REG_TEMP_T3_BEFORE_NE, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t4_after_ne(self) -> float | None:
        """Read temperature T4 after NE (T4 nach NE)."""
        registers = self.read_holding_registers(REG_TEMP_T4_AFTER_NE, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t5_exhaust_air(self) -> float | None:
        """Read temperature T5 exhaust air (T5 Abluft)."""
        registers = self.read_holding_registers(REG_TEMP_T5_EXHAUST_AIR, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t6_in_wt(self) -> float | None:
        """Read temperature T6 in WT (T6 im WT)."""
        registers = self.read_holding_registers(REG_TEMP_T6_IN_WT, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t7_evaporator(self) -> float | None:
        """Read temperature T7 evaporator (T7 Verdampfer)."""
        registers = self.read_holding_registers(REG_TEMP_T7_EVAPORATOR, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t8_condenser(self) -> float | None:
        """Read temperature T8 condenser (T8 Kondensator)."""
        registers = self.read_holding_registers(REG_TEMP_T8_CONDENSER, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_temperature_t10_outdoor(self) -> float | None:
        """Read temperature T10 outdoor (T10 Aussen)."""
        registers = self.read_holding_registers(REG_TEMP_T10_OUTDOOR, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_heating_cooling_function(self) -> int | None:
        """Read heating/cooling function (Heiz-Kühlfunktion)."""
        registers = self.read_holding_registers(REG_HEATING_COOLING_FUNCTION, 1)
        if registers:
            return registers[0]
        return None

    def write_heating_cooling_function(self, mode: int) -> bool:
        """Write heating/cooling function (Heiz-Kühlfunktion)."""
        return self.write_register(REG_HEATING_COOLING_FUNCTION, mode)

    def read_heat_pump_heating_enable(self) -> int | None:
        """Read heat pump heating enable (Wärmepumpe Heizen)."""
        registers = self.read_holding_registers(REG_HEAT_PUMP_HEATING_ENABLE, 1)
        if registers:
            return registers[0]
        return None

    def write_heat_pump_heating_enable(self, enabled: int) -> bool:
        """Write heat pump heating enable (Wärmepumpe Heizen)."""
        return self.write_register(REG_HEAT_PUMP_HEATING_ENABLE, enabled)

    def read_heat_pump_cooling_enable(self) -> int | None:
        """Read heat pump cooling enable (Wärmepumpe Kühlen)."""
        registers = self.read_holding_registers(REG_HEAT_PUMP_COOLING_ENABLE, 1)
        if registers:
            return registers[0]
        return None

    def write_heat_pump_cooling_enable(self, enabled: int) -> bool:
        """Write heat pump cooling enable (Wärmepumpe Kühlen)."""
        return self.write_register(REG_HEAT_PUMP_COOLING_ENABLE, enabled)

    def read_auxiliary_heating_enable(self) -> int | None:
        """Read auxiliary heating enable (Zusatzheizung Haus)."""
        registers = self.read_holding_registers(REG_AUXILIARY_HEATING_ENABLE, 1)
        if registers:
            return registers[0]
        return None

    def write_auxiliary_heating_enable(self, enabled: int) -> bool:
        """Write auxiliary heating enable (Zusatzheizung Haus)."""
        return self.write_register(REG_AUXILIARY_HEATING_ENABLE, enabled)

    def read_alarm_pressure_switch(self) -> int | None:
        """Read pressure switch alarm (Meldung Druckwächter Aktiv)."""
        registers = self.read_holding_registers(REG_ALARM_PRESSURE_SWITCH, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_utility_lock(self) -> int | None:
        """Read utility lock alarm (EVU Sperre Aktiv)."""
        registers = self.read_holding_registers(REG_ALARM_UTILITY_LOCK, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_door_open(self) -> int | None:
        """Read door open alarm (Tür offen)."""
        registers = self.read_holding_registers(REG_ALARM_DOOR_OPEN, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_device_filter_dirty(self) -> int | None:
        """Read device filter dirty alarm (Gerätefilter verschmutzt)."""
        registers = self.read_holding_registers(REG_ALARM_DEVICE_FILTER_DIRTY, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_upstream_filter_dirty(self) -> int | None:
        """Read upstream filter dirty alarm (Vorgelagerter Filter verschmutzt)."""
        registers = self.read_holding_registers(REG_ALARM_UPSTREAM_FILTER_DIRTY, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_off_peak_disabled(self) -> int | None:
        """Read off-peak disabled alarm (Niedertarif abgeschaltet)."""
        registers = self.read_holding_registers(REG_ALARM_OFF_PEAK_DISABLED, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_supply_voltage_off(self) -> int | None:
        """Read supply voltage off alarm (Versorgungsspannung abgeschaltet)."""
        registers = self.read_holding_registers(REG_ALARM_SUPPLY_VOLTAGE_OFF, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_pressostat_triggered(self) -> int | None:
        """Read pressostat triggered alarm (Pressostat ausgelöst)."""
        registers = self.read_holding_registers(REG_ALARM_PRESSOSTAT_TRIGGERED, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_external_utility_lock(self) -> int | None:
        """Read external utility lock alarm (EVU Sperre extern Aktiv)."""
        registers = self.read_holding_registers(REG_ALARM_EXTERNAL_UTILITY_LOCK, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_heating_module_test(self) -> int | None:
        """Read heating module test alarm (Heizmodul Testbetrieb aktiv)."""
        registers = self.read_holding_registers(REG_ALARM_HEATING_MODULE_TEST, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_emergency_mode(self) -> int | None:
        """Read emergency mode alarm (Notbetrieb aktiv)."""
        registers = self.read_holding_registers(REG_ALARM_EMERGENCY_MODE, 1)
        if registers:
            return registers[0]
        return None

    def read_alarm_supply_air_cold(self) -> int | None:
        """Read supply air too cold alarm (Zuluft zu kalt)."""
        registers = self.read_holding_registers(REG_ALARM_SUPPLY_AIR_COLD, 1)
        if registers:
            return registers[0]
        return None

    def read_device_filter_remaining(self) -> int | None:
        """Read device filter remaining days (Restlaufzeit Gerätefilter)."""
        registers = self.read_holding_registers(REG_DEVICE_FILTER_REMAINING, 1)
        if registers:
            return registers[0]
        return None

    def read_upstream_filter_remaining(self) -> int | None:
        """Read upstream filter remaining days (Restlaufzeit Vorgelagerter Filter)."""
        registers = self.read_holding_registers(REG_UPSTREAM_FILTER_REMAINING, 1)
        if registers:
            return registers[0]
        return None

    def read_error_message(self) -> int | None:
        """Read error message code (Fehlermeldung)."""
        registers = self.read_holding_registers(REG_ERROR_MESSAGE, 1)
        if registers:
            return registers[0]
        return None


    def read_room_temperature(self, room_number: int) -> float | None:
        """Read room current temperature (Ist Temp Raum)."""
        # Rooms 1-17 use registers 360-376
        register = 360 + room_number - 1
        registers = self.read_holding_registers(register, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def read_room_target_temperature(self, room_number: int) -> float | None:
        """Read room target temperature (Soll Temp Raum)."""
        # Rooms 1-17 use registers 400-416
        register = 400 + room_number - 1
        registers = self.read_holding_registers(register, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def write_room_target_temperature(self, room_number: int, temperature: float) -> bool:
        """Write room target temperature (Soll Temp Raum)."""
        # Rooms 1-17 use registers 400-416
        # Temperature range: 10-30°C, stored as value * 10
        register = 400 + room_number - 1
        value = int(temperature * 10)
        return self.write_register(register, value)

    def read_room_heating_enable(self, room_number: int) -> int | None:
        """Read room heating enable (Zusatzheizung Freigabe Raum)."""
        # Rooms 1-17 have heating enable (registers 440-456)
        if room_number < 1 or room_number > 17:
            return None
        register = 440 + room_number - 1
        registers = self.read_holding_registers(register, 1)
        if registers:
            return registers[0]
        return None

    def write_room_heating_enable(self, room_number: int, enabled: int) -> bool:
        """Write room heating enable (Zusatzheizung Freigabe Raum)."""
        # Rooms 1-17 have heating enable (registers 440-456)
        if room_number < 1 or room_number > 17:
            return False
        register = 440 + room_number - 1
        return self.write_register(register, enabled)

    def read_room_heating_active(self, room_number: int) -> int | None:
        """Read room heating active state (Zusatzheizung aktiv Raum)."""
        # Rooms 1-17 have heating active state (registers 460-476)
        if room_number < 1 or room_number > 17:
            return None
        register = 460 + room_number - 1
        registers = self.read_holding_registers(register, 1)
        if registers:
            return registers[0]
        return None

    def read_room_base_temperature(self, room_number: int) -> float | None:
        """Read room base temperature (Grundtemperatur Raum)."""
        # Rooms 1-17 use registers 420-436
        register = 420 + room_number - 1
        registers = self.read_holding_registers(register, 1)
        if registers:
            return int.from_bytes(registers[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
        return None

    def write_room_base_temperature(self, room_number: int, temperature: float) -> bool:
        """Write room base temperature (Grundtemperatur Raum)."""
        # Rooms 1-17 use registers 420-436
        # Temperature range: 10-30°C, stored as value * 10
        register = 420 + room_number - 1
        value = int(temperature * 10)
        return self.write_register(register, value)

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        data = {}

        data["operation_mode"] = self.read_register(REG_OPERATION_MODE, 1)
        data["fan_speed"] =  self.read_register(REG_FAN_SPEED, 1)
        data["current_fan_level"] = self.read_register(REG_CURRENT_FAN_LEVEL, 1)
        data["linear_fan_power"] = self.read_register(REG_LINEAR_FAN_POWER, 1)

        # Read fan override (Luftstufen Überschreibung)
        fan_override = self.read_fan_override()
        if fan_override is not None:
            data["fan_override"] = fan_override

        # Read time program base level (Zeitprogramm Basis Luftstufe)
        time_program_base_level = self.read_time_program_base_level()
        if time_program_base_level is not None:
            data["time_program_base_level"] = time_program_base_level

        # Read shock ventilation (Stoßlüftung)
        shock_ventilation = self.read_shock_ventilation()
        if shock_ventilation is not None:
            data["shock_ventilation"] = shock_ventilation

        # Read shock ventilation remaining time (Restlaufzeit Stoßlüftung)
        shock_ventilation_remaining = self.read_shock_ventilation_remaining()
        if shock_ventilation_remaining is not None:
            data["shock_ventilation_remaining"] = shock_ventilation_remaining

        # WGT-only: heat pump status and NHR state
        if self.device_type == "wgt":
            # Read heat pump status (Status Wärmepumpe)
            heat_pump_status = self.read_heat_pump_status()
            if heat_pump_status is not None:
                data["heat_pump_status"] = heat_pump_status

            # Read NHR state (NHR Zustand)
            nhr_state = self.read_nhr_state()
            if nhr_state is not None:
                data["nhr_state"] = nhr_state

        # Read supply air fan status (Status Gebläse Zuluft)
        supply_air_fan_status = self.read_supply_air_fan_status()
        if supply_air_fan_status is not None:
            data["supply_air_fan_status"] = supply_air_fan_status

        # Read exhaust air fan status (Status Gebläse Abluft)
        exhaust_air_fan_status = self.read_exhaust_air_fan_status()
        if exhaust_air_fan_status is not None:
            data["exhaust_air_fan_status"] = exhaust_air_fan_status

        # Read EWT state (EWT Zustand)
        ewt_state = self.read_ewt_state()
        if ewt_state is not None:
            data["ewt_state"] = ewt_state

        # Read bypass state (Bypass Zustand)
        bypass_state = self.read_bypass_state()
        if bypass_state is not None:
            data["bypass_state"] = bypass_state

        # Read outdoor damper state (Aussenklappe Zustand)
        outdoor_damper_state = self.read_outdoor_damper_state()
        if outdoor_damper_state is not None:
            data["outdoor_damper_state"] = outdoor_damper_state

        # Read preheater state (Vorheizregister Zustand)
        preheater_state = self.read_preheater_state()
        if preheater_state is not None:
            data["preheater_state"] = preheater_state

        # Read time program fan level (Luftstufe Zeitprogramm)
        time_program_fan_level = self.read_time_program_fan_level()
        if time_program_fan_level is not None:
            data["time_program_fan_level"] = time_program_fan_level

        # Read sensor fan level (Luftstufe Sensoren)
        sensor_fan_level = self.read_sensor_fan_level()
        if sensor_fan_level is not None:
            data["sensor_fan_level"] = sensor_fan_level

        # Read current supply air flow (Luftleistung aktuell Zuluft)
        current_supply_air_flow = self.read_current_supply_air_flow()
        if current_supply_air_flow is not None:
            data["current_supply_air_flow"] = current_supply_air_flow

        # Read current exhaust air flow (Luftleistung aktuell Abluft)
        current_exhaust_air_flow = self.read_current_exhaust_air_flow()
        if current_exhaust_air_flow is not None:
            data["current_exhaust_air_flow"] = current_exhaust_air_flow

        # Read current supply air RPM (Aktuelle Drehzahl Zuluft)
        current_supply_air_rpm = self.read_current_supply_air_rpm()
        if current_supply_air_rpm is not None:
            data["current_supply_air_rpm"] = current_supply_air_rpm

        # Read current exhaust air RPM (Aktuelle Drehzahl Abluft)
        current_exhaust_air_rpm = self.read_current_exhaust_air_rpm()
        if current_exhaust_air_rpm is not None:
            data["current_exhaust_air_rpm"] = current_exhaust_air_rpm

        # Read temperature T1 after EWT (T1 nach EWT)
        temp_t1_after_ewt = self.read_temperature_t1_after_ewt()
        if temp_t1_after_ewt is not None:
            data["temp_t1_after_ewt"] = temp_t1_after_ewt

        # Read temperature T2 after VHR (T2 nach VHR)
        temp_t2_after_vhr = self.read_temperature_t2_after_vhr()
        if temp_t2_after_vhr is not None:
            data["temp_t2_after_vhr"] = temp_t2_after_vhr

        # Read temperature T3 before NE (T3 vor NE)
        temp_t3_before_ne = self.read_temperature_t3_before_ne()
        if temp_t3_before_ne is not None:
            data["temp_t3_before_ne"] = temp_t3_before_ne

        # Read temperature T4 after NE (T4 nach NE)
        temp_t4_after_ne = self.read_temperature_t4_after_ne()
        if temp_t4_after_ne is not None:
            data["temp_t4_after_ne"] = temp_t4_after_ne

        # Read temperature T5 exhaust air (T5 Abluft)
        temp_t5_exhaust_air = self.read_temperature_t5_exhaust_air()
        if temp_t5_exhaust_air is not None:
            data["temp_t5_exhaust_air"] = temp_t5_exhaust_air

        # Read temperature T6 in WT (T6 im WT)
        temp_t6_in_wt = self.read_temperature_t6_in_wt()
        if temp_t6_in_wt is not None:
            data["temp_t6_in_wt"] = temp_t6_in_wt

        # Read temperature T7 evaporator (T7 Verdampfer)
        temp_t7_evaporator = self.read_temperature_t7_evaporator()
        if temp_t7_evaporator is not None:
            data["temp_t7_evaporator"] = temp_t7_evaporator

        # Read temperature T8 condenser (T8 Kondensator)
        temp_t8_condenser = self.read_temperature_t8_condenser()
        if temp_t8_condenser is not None:
            data["temp_t8_condenser"] = temp_t8_condenser

        # Read temperature T10 outdoor (T10 Aussen)
        temp_t10_outdoor = self.read_temperature_t10_outdoor()
        if temp_t10_outdoor is not None:
            data["temp_t10_outdoor"] = temp_t10_outdoor

        # WGT-specific registers (heating/cooling)
        if self.device_type == "wgt":
            # Read heating/cooling function (Heiz-Kühlfunktion)
            heating_cooling_function = self.read_heating_cooling_function()
            if heating_cooling_function is not None:
                data["heating_cooling_function"] = heating_cooling_function

            # Read heat pump heating enable (Wärmepumpe Heizen)
            heat_pump_heating_enable = self.read_heat_pump_heating_enable()
            if heat_pump_heating_enable is not None:
                data["heat_pump_heating_enable"] = heat_pump_heating_enable

            # Read heat pump cooling enable (Wärmepumpe Kühlen)
            heat_pump_cooling_enable = self.read_heat_pump_cooling_enable()
            if heat_pump_cooling_enable is not None:
                data["heat_pump_cooling_enable"] = heat_pump_cooling_enable

            # Read auxiliary heating enable (Zusatzheizung Haus)
            auxiliary_heating_enable = self.read_auxiliary_heating_enable()
            if auxiliary_heating_enable is not None:
                data["auxiliary_heating_enable"] = auxiliary_heating_enable

        # Read alarms
        alarm_pressure_switch = self.read_alarm_pressure_switch()
        if alarm_pressure_switch is not None:
            data["alarm_pressure_switch"] = alarm_pressure_switch

        alarm_utility_lock = self.read_alarm_utility_lock()
        if alarm_utility_lock is not None:
            data["alarm_utility_lock"] = alarm_utility_lock

        alarm_door_open = self.read_alarm_door_open()
        if alarm_door_open is not None:
            data["alarm_door_open"] = alarm_door_open

        alarm_device_filter_dirty = self.read_alarm_device_filter_dirty()
        if alarm_device_filter_dirty is not None:
            data["alarm_device_filter_dirty"] = alarm_device_filter_dirty

        alarm_upstream_filter_dirty = self.read_alarm_upstream_filter_dirty()
        if alarm_upstream_filter_dirty is not None:
            data["alarm_upstream_filter_dirty"] = alarm_upstream_filter_dirty

        alarm_off_peak_disabled = self.read_alarm_off_peak_disabled()
        if alarm_off_peak_disabled is not None:
            data["alarm_off_peak_disabled"] = alarm_off_peak_disabled

        alarm_supply_voltage_off = self.read_alarm_supply_voltage_off()
        if alarm_supply_voltage_off is not None:
            data["alarm_supply_voltage_off"] = alarm_supply_voltage_off

        alarm_pressostat_triggered = self.read_alarm_pressostat_triggered()
        if alarm_pressostat_triggered is not None:
            data["alarm_pressostat_triggered"] = alarm_pressostat_triggered

        alarm_external_utility_lock = self.read_alarm_external_utility_lock()
        if alarm_external_utility_lock is not None:
            data["alarm_external_utility_lock"] = alarm_external_utility_lock

        alarm_heating_module_test = self.read_alarm_heating_module_test()
        if alarm_heating_module_test is not None:
            data["alarm_heating_module_test"] = alarm_heating_module_test

        alarm_emergency_mode = self.read_alarm_emergency_mode()
        if alarm_emergency_mode is not None:
            data["alarm_emergency_mode"] = alarm_emergency_mode

        alarm_supply_air_cold = self.read_alarm_supply_air_cold()
        if alarm_supply_air_cold is not None:
            data["alarm_supply_air_cold"] = alarm_supply_air_cold

        device_filter_remaining = self.read_device_filter_remaining()
        if device_filter_remaining is not None:
            data["device_filter_remaining"] = device_filter_remaining

        upstream_filter_remaining = self.read_upstream_filter_remaining()
        if upstream_filter_remaining is not None:
            data["upstream_filter_remaining"] = upstream_filter_remaining

        # Read error message (Fehlermeldung)
        error_message = self.read_error_message()
        if error_message is not None:
            data["error_message"] = error_message

        # Read room temperatures (registers 360-376 for current, 400-416 for target)
        # and heating enable (registers 440-456 for rooms 1-17)
        # and heating active (registers 460-476 for rooms 1-17)
        for room_number in range(1, 18):  # Rooms 1-17
            # Current temperature
            current_temp = self.read_room_temperature(room_number)
            if current_temp is not None:
                data[f"register_{360 + room_number - 1}"] = int(current_temp * 10)

            # WGT-only: target and base temperatures, heating controls
            if self.device_type == "wgt":
                # Target temperature
                target_temp = self.read_room_target_temperature(room_number)
                if target_temp is not None:
                    data[f"register_{400 + room_number - 1}"] = int(target_temp * 10)

                # Base temperature
                base_temp = self.read_room_base_temperature(room_number)
                if base_temp is not None:
                    data[f"room_{room_number}_base_temp"] = base_temp

                # Heating enable (registers 440-456 for rooms 1-17)
                heating_enable = self.read_room_heating_enable(room_number)
                if heating_enable is not None:
                    data[f"register_{440 + room_number - 1}"] = heating_enable

                # Heating active (registers 460-476 for rooms 1-17)
                heating_active = self.read_room_heating_active(room_number)
                if heating_active is not None:
                    data[f"register_{460 + room_number - 1}"] = heating_active

                # Time program heating enable (registers 500-516 for rooms 1-17)
                time_program_heating = self.read_holding_registers(500 + room_number - 1, 1)
                if time_program_heating:
                    data[f"register_{500 + room_number - 1}"] = time_program_heating[0]

        # Read operating hours (Betriebsstunden)
        operating_hours_registers = [
            (800, REG_OPERATING_HOURS_FAN),
            (801, REG_OPERATING_HOURS_FAN_LEVEL_1),
            (802, REG_OPERATING_HOURS_FAN_LEVEL_2),
            (803, REG_OPERATING_HOURS_FAN_LEVEL_3),
            (804, REG_OPERATING_HOURS_FAN_LEVEL_4),
        ]

        # Add WGT-specific operating hours only for WGT devices
        if self.device_type == "wgt":
            operating_hours_registers.extend([
                (805, REG_OPERATING_HOURS_HEAT_PUMP),
                (806, REG_OPERATING_HOURS_HEAT_PUMP_COOLING),
                (809, REG_OPERATING_HOURS_VHR),
                (810, REG_OPERATING_HOURS_AUXILIARY_HEATING_HOUSE),
                (813, REG_OPERATING_HOURS_EWT),
            ])

        for reg_num, reg_const in operating_hours_registers:
            registers = self.read_holding_registers(reg_const, 1)
            if registers:
                data[f"register_{reg_num}"] = registers[0]

        return data
