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

    def write_shock_ventilation(self, active: int) -> bool:
        """Write shock ventilation (Stoßlüftung)."""
        return self.write_register(REG_SHOCK_VENTILATION, active)

    def write_heating_cooling_function(self, mode: int) -> bool:
        """Write heating/cooling function (Heiz-Kühlfunktion)."""
        return self.write_register(REG_HEATING_COOLING_FUNCTION, mode)

    def write_heat_pump_heating_enable(self, enabled: int) -> bool:
        """Write heat pump heating enable (Wärmepumpe Heizen)."""
        return self.write_register(REG_HEAT_PUMP_HEATING_ENABLE, enabled)

    def write_heat_pump_cooling_enable(self, enabled: int) -> bool:
        """Write heat pump cooling enable (Wärmepumpe Kühlen)."""
        return self.write_register(REG_HEAT_PUMP_COOLING_ENABLE, enabled)

    def write_auxiliary_heating_enable(self, enabled: int) -> bool:
        """Write auxiliary heating enable (Zusatzheizung Haus)."""
        return self.write_register(REG_AUXILIARY_HEATING_ENABLE, enabled)


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

        if (val := self.read_register(REG_FAN_OVERRIDE, 1)) is not None:
            data["fan_override"] = val

        if (val := self.read_register(REG_TIME_PROGRAM_BASE_LEVEL, 1)) is not None:
            data["time_program_base_level"] = val

        if (val := self.read_register(REG_SHOCK_VENTILATION, 1)) is not None:
            data["shock_ventilation"] = val

        if (val := self.read_register(REG_SHOCK_VENTILATION_REMAINING, 1)) is not None:
            data["shock_ventilation_remaining"] = val

        # WGT-only: heat pump status and NHR state
        if self.device_type == "wgt":
            if (val := self.read_register(REG_HEAT_PUMP_STATUS, 1)) is not None:
                data["heat_pump_status"] = val

            if (val := self.read_register(REG_NHR_STATE, 1)) is not None:
                data["nhr_state"] = val

        if (val := self.read_register(REG_SUPPLY_AIR_FAN_STATUS, 1)) is not None:
            data["supply_air_fan_status"] = val

        if (val := self.read_register(REG_EXHAUST_AIR_FAN_STATUS, 1)) is not None:
            data["exhaust_air_fan_status"] = val

        if (val := self.read_register(REG_EWT_STATE, 1)) is not None:
            data["ewt_state"] = val

        if (val := self.read_register(REG_BYPASS_STATE, 1)) is not None:
            data["bypass_state"] = val

        if (val := self.read_register(REG_OUTDOOR_DAMPER_STATE, 1)) is not None:
            data["outdoor_damper_state"] = val

        if (val := self.read_register(REG_PREHEATER_STATE, 1)) is not None:
            data["preheater_state"] = val

        if (val := self.read_register(REG_TIME_PROGRAM_FAN_LEVEL, 1)) is not None:
            data["time_program_fan_level"] = val

        if (val := self.read_register(REG_SENSOR_FAN_LEVEL, 1)) is not None:
            data["sensor_fan_level"] = val

        if (val := self.read_register(REG_CURRENT_SUPPLY_AIR_FLOW, 1)) is not None:
            data["current_supply_air_flow"] = val

        if (val := self.read_register(REG_CURRENT_EXHAUST_AIR_FLOW, 1)) is not None:
            data["current_exhaust_air_flow"] = val

        if (val := self.read_register(REG_CURRENT_SUPPLY_AIR_RPM, 1)) is not None:
            data["current_supply_air_rpm"] = val

        if (val := self.read_register(REG_CURRENT_EXHAUST_AIR_RPM, 1)) is not None:
            data["current_exhaust_air_rpm"] = val

        # Helper for temperature conversion
        def read_temp(reg):
            if (regs := self.read_holding_registers(reg, 1)):
                return int.from_bytes(regs[0].to_bytes(2, 'big'), 'big', signed=True) / 10.0
            return None

        if (val := read_temp(REG_TEMP_T1_AFTER_EWT)) is not None:
            data["temp_t1_after_ewt"] = val

        if (val := read_temp(REG_TEMP_T2_AFTER_VHR)) is not None:
            data["temp_t2_after_vhr"] = val

        if (val := read_temp(REG_TEMP_T3_BEFORE_NE)) is not None:
            data["temp_t3_before_ne"] = val

        if (val := read_temp(REG_TEMP_T4_AFTER_NE)) is not None:
            data["temp_t4_after_ne"] = val

        if (val := read_temp(REG_TEMP_T5_EXHAUST_AIR)) is not None:
            data["temp_t5_exhaust_air"] = val

        if (val := read_temp(REG_TEMP_T6_IN_WT)) is not None:
            data["temp_t6_in_wt"] = val

        if (val := read_temp(REG_TEMP_T7_EVAPORATOR)) is not None:
            data["temp_t7_evaporator"] = val

        if (val := read_temp(REG_TEMP_T8_CONDENSER)) is not None:
            data["temp_t8_condenser"] = val

        if (val := read_temp(REG_TEMP_T10_OUTDOOR)) is not None:
            data["temp_t10_outdoor"] = val

        # WGT-specific registers (heating/cooling)
        if self.device_type == "wgt":
            if (val := self.read_register(REG_HEATING_COOLING_FUNCTION, 1)) is not None:
                data["heating_cooling_function"] = val

            if (val := self.read_register(REG_HEAT_PUMP_HEATING_ENABLE, 1)) is not None:
                data["heat_pump_heating_enable"] = val

            if (val := self.read_register(REG_HEAT_PUMP_COOLING_ENABLE, 1)) is not None:
                data["heat_pump_cooling_enable"] = val

            if (val := self.read_register(REG_AUXILIARY_HEATING_ENABLE, 1)) is not None:
                data["auxiliary_heating_enable"] = val

        # Read alarms
        if (val := self.read_register(REG_ALARM_PRESSURE_SWITCH, 1)) is not None:
            data["alarm_pressure_switch"] = val

        if (val := self.read_register(REG_ALARM_UTILITY_LOCK, 1)) is not None:
            data["alarm_utility_lock"] = val

        if (val := self.read_register(REG_ALARM_DOOR_OPEN, 1)) is not None:
            data["alarm_door_open"] = val

        if (val := self.read_register(REG_ALARM_DEVICE_FILTER_DIRTY, 1)) is not None:
            data["alarm_device_filter_dirty"] = val

        if (val := self.read_register(REG_ALARM_UPSTREAM_FILTER_DIRTY, 1)) is not None:
            data["alarm_upstream_filter_dirty"] = val

        if (val := self.read_register(REG_ALARM_OFF_PEAK_DISABLED, 1)) is not None:
            data["alarm_off_peak_disabled"] = val

        if (val := self.read_register(REG_ALARM_SUPPLY_VOLTAGE_OFF, 1)) is not None:
            data["alarm_supply_voltage_off"] = val

        if (val := self.read_register(REG_ALARM_PRESSOSTAT_TRIGGERED, 1)) is not None:
            data["alarm_pressostat_triggered"] = val

        if (val := self.read_register(REG_ALARM_EXTERNAL_UTILITY_LOCK, 1)) is not None:
            data["alarm_external_utility_lock"] = val

        if (val := self.read_register(REG_ALARM_HEATING_MODULE_TEST, 1)) is not None:
            data["alarm_heating_module_test"] = val

        if (val := self.read_register(REG_ALARM_EMERGENCY_MODE, 1)) is not None:
            data["alarm_emergency_mode"] = val

        if (val := self.read_register(REG_ALARM_SUPPLY_AIR_COLD, 1)) is not None:
            data["alarm_supply_air_cold"] = val

        if (val := self.read_register(REG_DEVICE_FILTER_REMAINING, 1)) is not None:
            data["device_filter_remaining"] = val

        if (val := self.read_register(REG_UPSTREAM_FILTER_REMAINING, 1)) is not None:
            data["upstream_filter_remaining"] = val

        if (val := self.read_register(REG_ERROR_MESSAGE, 1)) is not None:
            data["error_message"] = val

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
