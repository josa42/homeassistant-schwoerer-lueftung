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


class BicWrgModbusClient:
    """Modbus TCP client for WRG device."""

    def __init__(self, host: str, port: int, slave_id: int) -> None:
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave_id = slave_id
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

    def read_holding_registers(
        self, address: int, count: int = 1
    ) -> list[int] | None:
        """Read holding registers from the device."""
        try:
            result = self._client.read_holding_registers(
                address=address, count=count, slave=self.slave_id
            )
            if result.isError():
                _LOGGER.error("Error reading registers at %s: %s", address, result)
                return None
            return result.registers
        except TypeError:
            # Try without slave parameter (newer pymodbus API)
            try:
                result = self._client.read_holding_registers(
                    address=address, count=count
                )
                if result.isError():
                    _LOGGER.error("Error reading registers at %s: %s", address, result)
                    return None
                return result.registers
            except Exception as err:
                _LOGGER.error("Error reading registers at %s: %s", address, err)
                return None
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
                address=address, values=[value], slave=self.slave_id
            )
            if result.isError():
                _LOGGER.error("Error writing register at %s: %s", address, result)
                return False
            return True
        except TypeError:
            # Try without slave parameter (newer pymodbus API)
            try:
                result = self._client.write_registers(
                    address=address, values=[value]
                )
                if result.isError():
                    _LOGGER.error("Error writing register at %s: %s", address, result)
                    return False
                return True
            except Exception as err:
                _LOGGER.error("Error writing register at %s: %s", address, err)
                return False
        except ModbusException as err:
            _LOGGER.error("Modbus exception writing register: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error writing register at %s: %s", address, err)
            return False

    def read_operation_mode(self) -> int | None:
        """Read operation mode (Betriebsart)."""
        registers = self.read_holding_registers(REG_OPERATION_MODE, 1)
        if registers:
            return registers[0]
        return None

    def write_operation_mode(self, mode: int) -> bool:
        """Write operation mode (Betriebsart)."""
        return self.write_register(REG_OPERATION_MODE, mode)

    def read_fan_speed(self) -> int | None:
        """Read manual fan speed (Manuelle Luftstufe)."""
        registers = self.read_holding_registers(REG_FAN_SPEED, 1)
        if registers:
            return registers[0]
        return None

    def write_fan_speed(self, speed: int) -> bool:
        """Write manual fan speed (Manuelle Luftstufe)."""
        return self.write_register(REG_FAN_SPEED, speed)

    def read_current_fan_level(self) -> int | None:
        """Read current fan level (Aktuelle Luftstufe)."""
        registers = self.read_holding_registers(REG_CURRENT_FAN_LEVEL, 1)
        if registers:
            return registers[0]
        return None

    def read_linear_fan_power(self) -> int | None:
        """Read manual linear fan power (Manuelle Lineare Luftleistung)."""
        registers = self.read_holding_registers(REG_LINEAR_FAN_POWER, 1)
        if registers:
            return registers[0]
        return None

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
            return registers[0] / 10.0
        return None

    def read_temperature_t2_after_vhr(self) -> float | None:
        """Read temperature T2 after VHR (T2 nach VHR)."""
        registers = self.read_holding_registers(REG_TEMP_T2_AFTER_VHR, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t3_before_ne(self) -> float | None:
        """Read temperature T3 before NE (T3 vor NE)."""
        registers = self.read_holding_registers(REG_TEMP_T3_BEFORE_NE, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t4_after_ne(self) -> float | None:
        """Read temperature T4 after NE (T4 nach NE)."""
        registers = self.read_holding_registers(REG_TEMP_T4_AFTER_NE, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t5_exhaust_air(self) -> float | None:
        """Read temperature T5 exhaust air (T5 Abluft)."""
        registers = self.read_holding_registers(REG_TEMP_T5_EXHAUST_AIR, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t6_in_wt(self) -> float | None:
        """Read temperature T6 in WT (T6 im WT)."""
        registers = self.read_holding_registers(REG_TEMP_T6_IN_WT, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t7_evaporator(self) -> float | None:
        """Read temperature T7 evaporator (T7 Verdampfer)."""
        registers = self.read_holding_registers(REG_TEMP_T7_EVAPORATOR, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t8_condenser(self) -> float | None:
        """Read temperature T8 condenser (T8 Kondensator)."""
        registers = self.read_holding_registers(REG_TEMP_T8_CONDENSER, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_temperature_t10_outdoor(self) -> float | None:
        """Read temperature T10 outdoor (T10 Aussen)."""
        registers = self.read_holding_registers(REG_TEMP_T10_OUTDOOR, 1)
        if registers:
            return registers[0] / 10.0
        return None

    def read_data(self) -> dict[str, Any]:
        """Read all relevant data from the device."""
        data = {}
        
        # Read operation mode (Betriebsart)
        operation_mode = self.read_operation_mode()
        if operation_mode is not None:
            data["operation_mode"] = operation_mode
        
        # Read fan speed (Manuelle Luftstufe)
        fan_speed = self.read_fan_speed()
        if fan_speed is not None:
            data["fan_speed"] = fan_speed
        
        # Read current fan level (Aktuelle Luftstufe)
        current_fan_level = self.read_current_fan_level()
        if current_fan_level is not None:
            data["current_fan_level"] = current_fan_level
        
        # Read linear fan power (Manuelle Lineare Luftleistung)
        linear_fan_power = self.read_linear_fan_power()
        if linear_fan_power is not None:
            data["linear_fan_power"] = linear_fan_power
        
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
        
        return data
