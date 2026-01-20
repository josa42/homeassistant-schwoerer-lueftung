#!/usr/bin/env python3
"""Test various Modbus methods to identify the device."""
import asyncio
import sys


async def test_all_methods(host, port=502):
    """Try multiple methods to identify the Modbus device."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔍 Testing Multiple Identification Methods on {host}:{port}")
    print("=" * 70)
    
    client = AsyncModbusTcpClient(host, port=port)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected to device\n")
        
        # Method 1: Read Device Identification (FC 43, MEI 0x0E)
        print("=" * 70)
        print("METHOD 1: Read Device Identification (FC 43, MEI 0x0E)")
        print("-" * 70)
        try:
            response = await client.read_device_information(
                read_code=0x01,
                object_id=0x00
            )
            if hasattr(response, 'exception_code'):
                print(f"❌ Exception Code: {response.exception_code}")
            elif hasattr(response, 'information'):
                print("✅ Success!")
                for obj_id, value in response.information.items():
                    print(f"   {obj_id}: {value}")
            else:
                print(f"⚠️  Unexpected: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Method 2: Read Holding Registers - Common identification registers
        print("\n" + "=" * 70)
        print("METHOD 2: Read Holding Registers (Common ID Locations)")
        print("-" * 70)
        
        # Try common register addresses for device information
        test_registers = [
            (0, 10, "Registers 0-9 (Often device info)"),
            (100, 10, "Registers 100-109"),
            (1000, 10, "Registers 1000-1009"),
            (40000, 10, "Registers 40000-40009"),
        ]
        
        for start_addr, count, description in test_registers:
            try:
                response = await client.read_holding_registers(start_addr, count)
                if hasattr(response, 'registers'):
                    # Check if any registers have non-zero values
                    if any(r != 0 for r in response.registers):
                        print(f"\n📍 {description}:")
                        for i, val in enumerate(response.registers):
                            if val != 0:
                                print(f"   Reg {start_addr + i:5d}: {val:5d} (0x{val:04X}) ", end="")
                                # Try to interpret as ASCII
                                chars = []
                                for byte_val in [(val >> 8) & 0xFF, val & 0xFF]:
                                    if 32 <= byte_val <= 126:
                                        chars.append(chr(byte_val))
                                if chars:
                                    print(f"['{' '.join(chars)}']")
                                else:
                                    print()
                elif hasattr(response, 'exception_code'):
                    print(f"⚠️  {description}: Exception {response.exception_code}")
            except Exception as e:
                print(f"⚠️  {description}: {e}")
        
        # Method 3: Read Input Registers
        print("\n" + "=" * 70)
        print("METHOD 3: Read Input Registers (First 20)")
        print("-" * 70)
        try:
            response = await client.read_input_registers(0, 20)
            if hasattr(response, 'registers'):
                print("✅ Input Registers 0-19:")
                for i, val in enumerate(response.registers):
                    if val != 0:
                        print(f"   Reg {i:3d}: {val:5d} (0x{val:04X})")
            elif hasattr(response, 'exception_code'):
                print(f"❌ Exception Code: {response.exception_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Method 4: Read Coils
        print("\n" + "=" * 70)
        print("METHOD 4: Read Coils (Status indicators)")
        print("-" * 70)
        try:
            response = await client.read_coils(0, 20)
            if hasattr(response, 'bits'):
                bits_set = [i for i, bit in enumerate(response.bits[:20]) if bit]
                if bits_set:
                    print(f"✅ Coils set: {bits_set}")
                else:
                    print("⚠️  No coils set (all 0)")
            elif hasattr(response, 'exception_code'):
                print(f"❌ Exception Code: {response.exception_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Method 5: Read known WRG registers (from your integration)
        print("\n" + "=" * 70)
        print("METHOD 5: Read Known WRG Device Registers")
        print("-" * 70)
        
        known_registers = [
            (100, "Operation Mode"),
            (102, "Manual Fan Level"),
            (104, "Current Fan Level"),
            (115, "Heating/Cooling Function"),
            (200, "Temp T1 after EWT (÷10)"),
            (240, "Error Message"),
        ]
        
        for reg_addr, description in known_registers:
            try:
                response = await client.read_holding_registers(reg_addr, 1)
                if hasattr(response, 'registers'):
                    val = response.registers[0]
                    print(f"   Reg {reg_addr:3d} ({description:30s}): {val}")
            except:
                pass
        
        # Method 6: Try reading with different slave IDs
        print("\n" + "=" * 70)
        print("METHOD 6: Test Different Slave IDs (1-10)")
        print("-" * 70)
        
        # Close and reconnect to test slave IDs
        client.close()
        
        for slave_id in range(1, 11):
            try:
                client = AsyncModbusTcpClient(host, port=port)
                await client.connect()
                
                # Try to set slave ID and read a register
                response = await client.read_holding_registers(100, 1, slave=slave_id)
                if hasattr(response, 'registers'):
                    print(f"✅ Slave ID {slave_id}: Responded (Value: {response.registers[0]})")
                    break
                elif hasattr(response, 'exception_code'):
                    if slave_id <= 3:  # Only show first few exceptions
                        print(f"⚠️  Slave ID {slave_id}: Exception {response.exception_code}")
                
                client.close()
            except Exception as e:
                if slave_id == 1:
                    print(f"❌ Slave ID test error: {e}")
                break
        
        print("\n" + "=" * 70)
        return True
            
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
        print("Usage: python3 test_modbus_methods.py <host> [port]")
        print("Example: python3 test_modbus_methods.py 10.0.0.139")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    
    await test_all_methods(host, port)
    
    print("\n📝 Summary:")
    print("   This test tried multiple methods to identify the Modbus device.")
    print("   Check the results above to see what information is available.")


if __name__ == "__main__":
    asyncio.run(main())
