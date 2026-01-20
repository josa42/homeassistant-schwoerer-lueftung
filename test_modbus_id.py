#!/usr/bin/env python3
"""Test Modbus Device Identification (function code 43/0x2B)."""
import asyncio
import sys


async def read_device_identification(host, port=502):
    """Read device identification from Modbus device."""
    from pymodbus.client import AsyncModbusTcpClient
    
    print(f"\n🔍 Reading Device Identification from {host}:{port}")
    print("=" * 60)
    
    client = AsyncModbusTcpClient(host, port=port)
    
    try:
        await client.connect()
        if not client.connected:
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected to device")
        
        print("\n📤 Sending Read Device Identification request...")
        print(f"   Function Code: 0x2B (43)")
        print(f"   MEI Type: 0x0E (14)")
        print(f"   Read Code: 0x01 (Basic)")
        
        # Try without slave parameter
        response = await client.read_device_information(
            read_code=0x01,  # Basic device identification
            object_id=0x00   # Start from VendorName
        )
        
        print(f"\n📥 Response type: {type(response)}")
        print(f"   Response: {response}")
        
        if hasattr(response, 'information'):
            info = response.information
            print("\n✅ Device Identification successful!")
            
            # Object ID mapping
            object_names = {
                0x00: "VendorName",
                0x01: "ProductCode", 
                0x02: "MajorMinorRevision",
                0x03: "VendorUrl",
                0x04: "ProductName",
                0x05: "ModelName",
                0x06: "UserApplicationName",
            }
            
            if info:
                print("\n📋 Device Information:")
                print("-" * 60)
                for obj_id, obj_value in info.items():
                    obj_name = object_names.get(obj_id, f"Object_{obj_id}")
                    # Handle both bytes and string values
                    if isinstance(obj_value, bytes):
                        obj_value = obj_value.decode('utf-8', errors='ignore')
                    print(f"   {obj_name:25s}: {obj_value}")
                print("-" * 60)
                return True
            else:
                print("\n⚠️  No device information returned")
                return False
        elif hasattr(response, 'exception_code'):
            print(f"\n❌ Modbus Exception Code: {response.exception_code}")
            print("   Device does not support Read Device Identification (FC 43)")
            return False
        else:
            print(f"\n⚠️  Response attributes: {dir(response)}")
            return False
            
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
        print("Usage: python3 test_modbus_id.py <host> [port]")
        print("Example: python3 test_modbus_id.py 10.0.0.139")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 502
    
    success = await read_device_identification(host, port)
    
    if success:
        print("\n✅ Device identification successful!")
        sys.exit(0)
    else:
        print("\n❌ Device identification failed")
        print("\nNote: Not all Modbus devices support function code 43.")
        print("The device may not implement Read Device Identification.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
