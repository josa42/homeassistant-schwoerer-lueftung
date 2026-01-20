#!/usr/bin/env python3
"""Test Schwörer ventilation unit specific register locations."""
import asyncio
import sys


def decode_registers_as_ascii(registers):
    """Decode register values as ASCII string (big-endian)."""
    chars = []
    for val in registers:
        # Big-endian: high byte first, then low byte
        high_byte = (val >> 8) & 0xFF
        low_byte = val & 0xFF
        
        for byte_val in [high_byte, low_byte]:
            if 32 <= byte_val <= 126:  # Printable ASCII
                chars.append(chr(byte_val))
            elif byte_val == 0:
                break
            else:
                chars.append('.')
    
    return ''.join(chars).strip()


async def test_schwoerer_registers(host, port=502):
    """Test Schwörer ventilation unit specific register locations."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔍 Testing Schwörer Ventilation Unit Registers on {host}:{port}")
    print("=" * 80)
    
    client = AsyncModbusTcpClient(host, port=port)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected to device\n")
        
        # Test locations based on Schwörer documentation
        test_blocks = [
            # Registers 0-10: Vendor ID / Firmware / Hardware
            (0, 10, "Registers 0-9: Vendor ID / Firmware"),
            (1, 10, "Registers 1-10: Vendor ID / Firmware (alt)"),
            
            # Common Modbus addressing (40001 = register 0)
            (40001, 10, "Registers 40001-40010: Device Info"),
            
            # Registers 10-20
            (10, 10, "Registers 10-19: Extended Info"),
            
            # Status/Config blocks
            (400, 20, "Registers 400-419: Status/Config Block"),
            (500, 20, "Registers 500-519: Config Block"),
            
            # Your integration uses 100+ for device data
            (100, 20, "Registers 100-119: Device Operation"),
            (200, 20, "Registers 200-219: Temperature Sensors"),
            (240, 10, "Registers 240-249: Error/Status"),
        ]
        
        results_found = []
        
        for start_addr, count, description in test_blocks:
            try:
                print(f"\n{'=' * 80}")
                print(f"📍 {description}")
                print(f"   Reading address {start_addr}, count {count}")
                print('-' * 80)
                
                response = await client.read_holding_registers(
                    address=start_addr,
                    count=count
                )
                
                if hasattr(response, 'registers'):
                    registers = response.registers
                    
                    # Check if any registers have meaningful values
                    non_zero = [r for r in registers if r != 0]
                    if non_zero:
                        print(f"✅ Success! Found {len(non_zero)} non-zero registers\n")
                        
                        # Show register values
                        print("   Dec  Hex    Binary          ASCII")
                        print("   " + "-" * 55)
                        for i, val in enumerate(registers):
                            reg_num = start_addr + i
                            high = (val >> 8) & 0xFF
                            low = val & 0xFF
                            
                            # ASCII interpretation
                            ascii_str = ""
                            for byte_val in [high, low]:
                                if 32 <= byte_val <= 126:
                                    ascii_str += chr(byte_val)
                                else:
                                    ascii_str += "."
                            
                            if val != 0:
                                print(f"   R{reg_num:4d}: {val:5d}  0x{val:04X}  "
                                      f"{val:016b}  [{ascii_str}]")
                        
                        # Try to decode as ASCII string
                        ascii_text = decode_registers_as_ascii(registers)
                        if ascii_text and len(ascii_text) > 2:
                            print(f"\n   📝 ASCII String: '{ascii_text}'")
                            results_found.append((description, ascii_text))
                        
                        # Check for known patterns
                        if any('WGT' in ascii_text or 'Vent' in ascii_text or 
                               'Schwörer' in ascii_text.lower() for ascii_text in [ascii_text]):
                            print(f"   🎯 POSSIBLE DEVICE IDENTIFIER FOUND!")
                            
                    else:
                        print(f"⚠️  All registers are 0 (empty)")
                        
                elif hasattr(response, 'exception_code'):
                    print(f"❌ Modbus Exception Code: {response.exception_code}")
                    if response.exception_code == 2:
                        print("   (Illegal Data Address - register not available)")
                    elif response.exception_code == 1:
                        print("   (Illegal Function - operation not supported)")
                        
            except Exception as e:
                print(f"❌ Error reading: {e}")
        
        # Summary
        print(f"\n\n{'=' * 80}")
        print("📊 SUMMARY OF FINDINGS")
        print('=' * 80)
        
        if results_found:
            print("\n✅ Potential Device Identifiers Found:\n")
            for desc, value in results_found:
                print(f"   • {desc}")
                print(f"     → '{value}'")
        else:
            print("\n⚠️  No clear device identifiers found in tested registers.")
            print("\nPossible reasons:")
            print("   • Device uses different register layout")
            print("   • Identification stored in input registers instead")
            print("   • No ASCII strings stored (numeric codes only)")
            print("   • Need to test different address ranges")
        
        return len(results_found) > 0
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 test_schwoerer_registers.py <host> [port]")
        print("Example: python3 test_schwoerer_registers.py 10.0.0.139")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    
    success = await test_schwoerer_registers(host, port)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Found potential device identification data!")
    else:
        print("⚠️  No device identification found in common locations")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
