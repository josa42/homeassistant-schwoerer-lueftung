#!/usr/bin/env python3
"""Investigate specific registers by monitoring changes over time."""
import asyncio
import sys
from datetime import datetime


async def monitor_registers(host, registers, duration=60, interval=2):
    """Monitor specific registers over time."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔍 Monitoring Registers {registers} on {host}")
    print(f"Duration: {duration}s, Interval: {interval}s")
    print("=" * 80)
    
    client = AsyncModbusTcpClient(host, port=502)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return
        
        print("✅ Connected to device\n")
        
        # Initial read to establish baseline
        print("📊 Initial Values:")
        print("-" * 80)
        baseline = {}
        for reg in registers:
            try:
                response = await client.read_holding_registers(address=reg, count=1)
                if hasattr(response, 'registers'):
                    val = response.registers[0]
                    baseline[reg] = val
                    print(f"   R{reg}: {val:5d} (0x{val:04X}, binary: {val:08b})")
            except Exception as e:
                print(f"   R{reg}: Error - {e}")
        
        print("\n⏰ Monitoring for changes...")
        print(f"   Press Ctrl+C to stop early\n")
        
        changes_detected = []
        iterations = duration // interval
        
        for i in range(iterations):
            await asyncio.sleep(interval)
            
            # Read all registers
            current_values = {}
            for reg in registers:
                try:
                    response = await client.read_holding_registers(address=reg, count=1)
                    if hasattr(response, 'registers'):
                        current_values[reg] = response.registers[0]
                except:
                    pass
            
            # Check for changes
            for reg, val in current_values.items():
                if reg in baseline and baseline[reg] != val:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    change = {
                        'time': timestamp,
                        'register': reg,
                        'old': baseline[reg],
                        'new': val,
                        'diff': val - baseline[reg]
                    }
                    changes_detected.append(change)
                    print(f"   🔔 [{timestamp}] R{reg}: {baseline[reg]:5d} → {val:5d} (diff: {change['diff']:+d})")
                    baseline[reg] = val
            
            # Progress indicator
            if (i + 1) % 5 == 0:
                print(f"   ⏱️  {i + 1}/{iterations} readings completed...")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 MONITORING SUMMARY")
        print("=" * 80)
        
        if changes_detected:
            print(f"\n✅ Detected {len(changes_detected)} changes:\n")
            for change in changes_detected:
                print(f"   [{change['time']}] R{change['register']}: "
                      f"{change['old']:5d} → {change['new']:5d} ({change['diff']:+d})")
        else:
            print("\n⚠️  No changes detected during monitoring period")
            print("   These registers appear to be:")
            print("   - Static configuration values")
            print("   - Slowly changing counters")
            print("   - Or require specific device state changes to update")
        
        # Final values
        print("\n📊 Final Values:")
        print("-" * 80)
        for reg, val in baseline.items():
            print(f"   R{reg}: {val:5d} (0x{val:04X}, binary: {val:08b})")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


async def analyze_register_bits(host, registers):
    """Analyze bit patterns in registers."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔬 Detailed Bit Analysis of Registers {registers}")
    print("=" * 80)
    
    client = AsyncModbusTcpClient(host, port=502)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return
        
        print("✅ Connected to device\n")
        
        for reg in registers:
            try:
                response = await client.read_holding_registers(address=reg, count=1)
                if hasattr(response, 'registers'):
                    val = response.registers[0]
                    
                    print(f"Register {reg}:")
                    print(f"  Decimal: {val}")
                    print(f"  Hex:     0x{val:04X}")
                    print(f"  Binary:  {val:016b}")
                    print(f"  Bits:    ", end="")
                    for i in range(15, -1, -1):
                        print(f"{i:2d}", end=" ")
                    print()
                    print(f"  Values:  ", end="")
                    for i in range(15, -1, -1):
                        bit = (val >> i) & 1
                        print(f" {bit}", end=" ")
                    print()
                    
                    # Show which bits are set
                    set_bits = [i for i in range(16) if (val >> i) & 1]
                    if set_bits:
                        print(f"  Set bits: {set_bits}")
                    else:
                        print(f"  Set bits: None (all 0)")
                    
                    # Possible interpretations
                    print(f"  Possible meanings:")
                    if val < 10:
                        print(f"    - Mode/state indicator (value {val})")
                    elif val < 60:
                        print(f"    - Time-related? (minutes: {val})")
                    elif val < 256:
                        print(f"    - Counter or small value")
                    elif val > 1000:
                        print(f"    - Large counter or timestamp")
                    
                    print()
                    
            except Exception as e:
                print(f"  Error reading R{reg}: {e}\n")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()


async def correlate_with_known_registers(host, unknown_regs):
    """Try to correlate unknown registers with known operational data."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔗 Correlating Unknown Registers with Known Values")
    print("=" * 80)
    
    client = AsyncModbusTcpClient(host, port=502)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return
        
        print("✅ Connected to device\n")
        
        # Read known registers for context
        known_regs = {
            100: "Operation Mode",
            102: "Manual Fan Level",
            104: "Current Fan Level",
            115: "Heating/Cooling Function",
            122: "EWT State",
            133: "Preheater State",
            204: "Temperature T5 (exhaust)",
            209: "Temperature T10 (outdoor)",
        }
        
        print("📊 Current Device State:")
        print("-" * 80)
        known_values = {}
        for reg, name in known_regs.items():
            try:
                response = await client.read_holding_registers(address=reg, count=1)
                if hasattr(response, 'registers'):
                    val = response.registers[0]
                    known_values[reg] = val
                    print(f"   R{reg:3d} ({name:30s}): {val}")
            except:
                pass
        
        print("\n" + "=" * 80)
        print("📊 Unknown Registers (480-485):")
        print("-" * 80)
        unknown_values = {}
        for reg in unknown_regs:
            try:
                response = await client.read_holding_registers(address=reg, count=1)
                if hasattr(response, 'registers'):
                    val = response.registers[0]
                    unknown_values[reg] = val
                    print(f"   R{reg}: {val:5d} (0x{val:04X})")
            except Exception as e:
                print(f"   R{reg}: Error - {e}")
        
        # Try to find correlations
        print("\n" + "=" * 80)
        print("🔍 Correlation Analysis:")
        print("-" * 80)
        
        # Check if any unknown registers match known values
        for ureg, uval in unknown_values.items():
            matches = []
            for kreg, kval in known_values.items():
                if uval == kval:
                    matches.append(f"R{kreg} ({known_regs[kreg]})")
            
            if matches:
                print(f"   R{ureg} ({uval}) matches: {', '.join(matches)}")
        
        # Check sequential patterns
        if len(unknown_values) > 1:
            vals = [unknown_values[r] for r in sorted(unknown_values.keys())]
            if all(vals[i] <= vals[i+1] for i in range(len(vals)-1)):
                print("\n   📈 Values are sequential/ascending - possibly counter array")
            elif len(set(vals)) == len(vals):
                print("\n   🔢 All values are unique - possibly enum/flags")
            elif len(set(vals)) == 1:
                print("\n   ⚖️  All values identical - possibly default/config value")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 investigate_registers.py <host> [mode]")
        print("\nModes:")
        print("  monitor   - Monitor R480-485 for changes over 60s (default)")
        print("  bits      - Analyze bit patterns")
        print("  correlate - Correlate with known registers")
        print("  all       - Run all analyses")
        print("\nExample: python3 investigate_registers.py 10.0.0.139 all")
        sys.exit(1)
    
    host = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "monitor"
    
    registers = [480, 481, 482, 483, 484, 485]
    
    if mode == "monitor":
        await monitor_registers(host, registers, duration=60, interval=2)
    elif mode == "bits":
        await analyze_register_bits(host, registers)
    elif mode == "correlate":
        await correlate_with_known_registers(host, registers)
    elif mode == "all":
        await analyze_register_bits(host, registers)
        print("\n" + "=" * 80 + "\n")
        await correlate_with_known_registers(host, registers)
        print("\n" + "=" * 80 + "\n")
        await monitor_registers(host, registers, duration=30, interval=2)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
