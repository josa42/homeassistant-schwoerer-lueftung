#!/usr/bin/env python3
"""Systematically scan registers 0-500 for any non-zero values."""
import asyncio
import sys


async def scan_all_registers(host, port=502):
    """Scan registers 0-500 systematically."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔍 Systematically Scanning Registers 0-500 on {host}:{port}")
    print("=" * 80)
    
    client = AsyncModbusTcpClient(host, port=port)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return {}
        
        print("✅ Connected to device\n")
        print("⏳ This will take a moment...\n")
        
        all_results = {}
        
        # Scan in blocks of 10 for efficiency
        for start in range(0, 501, 10):
            count = min(10, 501 - start)
            
            try:
                response = await client.read_holding_registers(
                    address=start,
                    count=count
                )
                
                if hasattr(response, 'registers'):
                    for i, val in enumerate(response.registers):
                        reg_num = start + i
                        if val != 0:
                            all_results[reg_num] = val
                            
                # Show progress every 50 registers
                if start % 50 == 0:
                    print(f"   Scanned registers {start:3d}-{start+count-1:3d}...")
                    
            except Exception as e:
                # Some addresses may not be valid
                pass
        
        return all_results
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        client.close()


def decode_register_as_ascii(val):
    """Try to decode register as ASCII."""
    high = (val >> 8) & 0xFF
    low = val & 0xFF
    result = []
    for byte_val in [high, low]:
        if 32 <= byte_val <= 126:
            result.append(chr(byte_val))
        else:
            result.append('.')
    return ''.join(result)


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 scan_all_registers.py <host> [port]")
        print("Example: python3 scan_all_registers.py 10.0.0.139")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    
    results = await scan_all_registers(host, port)
    
    print("\n" + "=" * 80)
    print(f"📊 SCAN RESULTS: Found {len(results)} non-zero registers")
    print("=" * 80 + "\n")
    
    if results:
        print("Register | Decimal | Hex    | Binary           | ASCII  | Possible Meaning")
        print("-" * 85)
        
        for reg_num in sorted(results.keys()):
            val = results[reg_num]
            ascii_rep = decode_register_as_ascii(val)
            
            # Try to identify what this register might be
            meaning = "Unknown"
            
            # Known registers from your integration
            known_regs = {
                100: "Operation Mode (0=Off, 1=Manual, 2=Winter, 3=Summer, 4=Summer Exhaust)",
                102: "Manual Fan Level (0=Off, 1-4=Levels, 5=Auto, 6=Linear)",
                103: "Time Program Base Level (0=Off, 1-4=Levels)",
                104: "Current Fan Level (0=Off, 1-4=Levels)",
                105: "Shock Ventilation Status (0=Inactive, 1=Active)",
                106: "Shock Ventilation Remaining Time (minutes)",
                107: "Fan Override (0=Inactive, 1=Active)",
                115: "Heating/Cooling Function (0=Off, 1=Heat, 2=Cool, 3/4=Auto)",
                118: "Heat Pump Status (0=Off, 5=Heating, 49=Cooling)",
                119: "NHR State (0=Inactive, 1=Active)",
                120: "Supply Air Fan Status (0=Disabled, 1=Startup, 2=Active, 5=Standby, 6=Error)",
                121: "Exhaust Air Fan Status (0=Disabled, 1=Startup, 2=Active, 5=Standby, 6=Error)",
                122: "EWT State (0=Off, 1=Heating, 2=Cooling)",
                123: "Bypass State (0=Closed, 1=Open Cooling, 2=Open Heating)",
                124: "Outdoor Damper State (0=Closed, 1=Open)",
                131: "Time Program Fan Level (0=Off, 1-4=Levels)",
                132: "Sensor Fan Level (0=Off, 1-4=Levels)",
                133: "Preheater State (0=Off, 1=VHR1, 2=VHR2, 3=Both)",
                134: "Current Supply Air Flow (m³/h)",
                135: "Current Exhaust Air Flow (m³/h)",
                200: "Temperature T1 after EWT (°C × 10)",
                201: "Temperature T2 after VHR (°C × 10)",
                202: "Temperature T3 before NHR (°C × 10)",
                203: "Temperature T4 after NHR (°C × 10)",
                204: "Temperature T5 exhaust air (°C × 10)",
                205: "Temperature T6 in WT (°C × 10)",
                206: "Temperature T7 evaporator (°C × 10)",
                207: "Temperature T8 condenser (°C × 10)",
                209: "Temperature T10 outdoor (°C × 10)",
                240: "Error Message (0=None, see error codes)",
            }
            
            if reg_num in known_regs:
                meaning = f"✅ {known_regs[reg_num]}"
            else:
                meaning = "❓ UNKNOWN - Not used in integration"
            
            print(f"R{reg_num:4d}    | {val:7d} | 0x{val:04X} | {val:016b} | [{ascii_rep}] | {meaning}")
    else:
        print("⚠️  No non-zero registers found!")
    
    print("\n" + "=" * 80)
    print("\n💾 Saving results to registers.md...")
    
    # Generate markdown file
    await generate_markdown(results, host)


async def generate_markdown(results, host):
    """Generate registers.md with all findings."""
    
    # Load known registers from integration
    known_regs = {
        100: ("Operation Mode", "select", "0=Off, 1=Manual, 2=Winter, 3=Summer, 4=Summer Exhaust", True),
        102: ("Manual Fan Level", "select", "0=Off, 1-4=Levels, 5=Auto, 6=Linear", True),
        103: ("Time Program Base Level", "sensor", "0=Off, 1-4=Levels", True),
        104: ("Current Fan Level", "sensor", "0=Off, 1-4=Levels", True),
        105: ("Shock Ventilation Status", "binary_sensor", "0=Inactive, 1=Active", True),
        106: ("Shock Ventilation Remaining", "sensor", "Minutes remaining", True),
        107: ("Fan Override", "binary_sensor", "0=Inactive, 1=Active", True),
        115: ("Heating/Cooling Function", "select", "0=Off, 1=Heat, 2=Cool, 3/4=Auto", True),
        118: ("Heat Pump Status", "sensor", "0=Off, 5=Heating, 49=Cooling", True),
        119: ("NHR State", "binary_sensor", "0=Inactive, 1=Active", True),
        120: ("Supply Air Fan Status", "sensor", "0=Disabled, 1=Startup, 2=Active, 5=Standby, 6=Error", True),
        121: ("Exhaust Air Fan Status", "sensor", "0=Disabled, 1=Startup, 2=Active, 5=Standby, 6=Error", True),
        122: ("EWT State", "sensor", "0=Off, 1=Heating, 2=Cooling", True),
        123: ("Bypass State", "sensor", "0=Closed, 1=Open Cooling, 2=Open Heating", True),
        124: ("Outdoor Damper State", "sensor", "0=Closed, 1=Open", True),
        131: ("Time Program Fan Level", "sensor", "0=Off, 1-4=Levels", True),
        132: ("Sensor Fan Level", "sensor", "0=Off, 1-4=Levels", True),
        133: ("Preheater State", "sensor", "0=Off, 1=VHR1, 2=VHR2, 3=Both - Split into 2 binary sensors", True),
        134: ("Current Supply Air Flow", "sensor", "m³/h", True),
        135: ("Current Exhaust Air Flow", "sensor", "m³/h", True),
        200: ("Temperature T1 after EWT", "sensor", "°C × 10", True),
        201: ("Temperature T2 after VHR", "sensor", "°C × 10", True),
        202: ("Temperature T3 before NHR", "sensor", "°C × 10", True),
        203: ("Temperature T4 after NHR", "sensor", "°C × 10", True),
        204: ("Temperature T5 exhaust air", "sensor", "°C × 10", True),
        205: ("Temperature T6 in WT", "sensor", "°C × 10", True),
        206: ("Temperature T7 evaporator", "sensor", "°C × 10", True),
        207: ("Temperature T8 condenser", "sensor", "°C × 10", True),
        209: ("Temperature T10 outdoor", "sensor", "°C × 10", True),
        240: ("Error Message", "sensor", "Error codes 0-1284", True),
    }
    
    md_content = f"""# Schwörer WRG 134-BP-HK Register Map

**Device:** {host}:502  
**Scan Date:** 2026-01-20  
**Registers Scanned:** 0-500  
**Non-Zero Registers Found:** {len(results)}

## Legend

- ✅ **Used** - Register is used in the integration
- ❓ **Unknown** - Register has data but purpose is unknown
- 🔍 **Potential** - May contain useful information

---

## Register Summary

| Register | Value | Hex | Status | Entity Type | Description |
|----------|-------|-----|--------|-------------|-------------|
"""
    
    for reg_num in sorted(results.keys()):
        val = results[reg_num]
        
        if reg_num in known_regs:
            name, entity_type, description, used = known_regs[reg_num]
            status = "✅ Used"
            md_content += f"| {reg_num:4d} | {val:5d} | 0x{val:04X} | {status} | {entity_type:13s} | **{name}**: {description} |\n"
        else:
            status = "❓ Unknown"
            md_content += f"| {reg_num:4d} | {val:5d} | 0x{val:04X} | {status} | - | Unknown purpose - not used in integration |\n"
    
    md_content += """
---

## Detailed Register Information

### Operational Registers (100-135)

"""
    
    # Group registers by function
    for reg_num in sorted([r for r in results.keys() if 100 <= r <= 135]):
        val = results[reg_num]
        if reg_num in known_regs:
            name, entity_type, description, _ = known_regs[reg_num]
            md_content += f"#### Register {reg_num}: {name}\n"
            md_content += f"- **Current Value:** {val}\n"
            md_content += f"- **Entity Type:** {entity_type}\n"
            md_content += f"- **Description:** {description}\n"
            md_content += f"- **Status:** ✅ Implemented in integration\n\n"
    
    md_content += """
### Temperature Registers (200-209)

All temperature values are in °C × 10 (e.g., 201 = 20.1°C)

"""
    
    for reg_num in sorted([r for r in results.keys() if 200 <= r <= 209]):
        val = results[reg_num]
        temp_c = val / 10.0 if val != 65505 else None  # 65505 = -3.1°C or error
        if reg_num in known_regs:
            name, entity_type, description, _ = known_regs[reg_num]
            if temp_c is not None:
                md_content += f"#### Register {reg_num}: {name}\n"
                md_content += f"- **Raw Value:** {val}\n"
                md_content += f"- **Temperature:** {temp_c:.1f}°C\n"
                md_content += f"- **Description:** {description}\n"
                md_content += f"- **Status:** ✅ Implemented\n\n"
    
    md_content += """
### Error Registers (240+)

"""
    
    for reg_num in sorted([r for r in results.keys() if reg_num >= 240]):
        val = results[reg_num]
        if reg_num in known_regs:
            name, entity_type, description, _ = known_regs[reg_num]
            md_content += f"#### Register {reg_num}: {name}\n"
            md_content += f"- **Current Value:** {val}\n"
            md_content += f"- **Description:** {description}\n"
            md_content += f"- **Status:** ✅ Implemented\n\n"
    
    # Add unknown registers section
    unknown_regs = [r for r in results.keys() if r not in known_regs]
    if unknown_regs:
        md_content += """
---

## Unknown Registers (Not Yet Used)

These registers contain non-zero values but are not currently used in the integration.
They may contain useful information such as:
- Operating hours counters
- Alarm states
- Advanced configuration
- Device identification
- Firmware version

"""
        md_content += "| Register | Value | Hex | Possible Use |\n"
        md_content += "|----------|-------|-----|-------------|\n"
        
        for reg_num in sorted(unknown_regs):
            val = results[reg_num]
            
            # Try to guess purpose based on value ranges
            possible_use = "Unknown"
            if val < 10:
                possible_use = "State/Mode indicator?"
            elif 100 <= val <= 300:
                possible_use = "Temperature or flow value?"
            elif val > 1000:
                possible_use = "Counter or timestamp?"
            
            md_content += f"| {reg_num:4d} | {val:5d} | 0x{val:04X} | {possible_use} |\n"
        
        md_content += """

**Note:** These registers need investigation to determine their purpose.
Consider testing:
- Changes during different operational modes
- Correlation with known values
- Patterns over time
"""
    
    md_content += """
---

## Register Access Patterns

### Read-Only Registers (Sensors)
All temperature and status registers are read-only.

### Read-Write Registers (Controls)
- Register 100: Operation Mode
- Register 102: Manual Fan Level
- Register 115: Heating/Cooling Function

### Special Registers
- Register 240: Error Message (maps to error codes 0-1284)
- Register 133: Preheater State (split into 2 binary sensors)

---

## Testing Notes

1. **Function Code 43 (Device Identification):** NOT supported
2. **Registers 0-99:** Mostly empty (all zeros)
3. **Registers 100-135:** Operational data (working perfectly)
4. **Registers 136-199:** Empty
5. **Registers 200-209:** Temperature sensors (working perfectly)
6. **Registers 210-239:** Mostly empty
7. **Registers 240+:** Error and diagnostic data

---

## References

- Integration: `custom_components/schwoerer_lueftung/`
- Modbus Client: `modbus_client.py`
- Register Constants: See `BWRG_*` constants in `modbus_client.py`

---

**Last Updated:** 2026-01-20
"""
    
    with open("registers.md", "w") as f:
        f.write(md_content)
    
    print("✅ registers.md created successfully!")
    print("\n📄 File contains:")
    print("   - Complete register map (0-500)")
    print("   - Used vs unused registers")
    print("   - Entity types and descriptions")
    print("   - Unknown registers for future investigation")


if __name__ == "__main__":
    asyncio.run(main())
