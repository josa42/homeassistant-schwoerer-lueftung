# Modbus Device Identification Test Results

## Device Information
- **IP Address:** 10.0.0.139
- **Port:** 502 (Modbus TCP)
- **Device Type:** Schwörer WRG 134-BP-HK Ventilation Unit

## Tests Performed

### 1. Read Device Identification (FC 43, MEI 0x0E)
**Status:** ❌ NOT SUPPORTED

- Function Code: 0x2B (43)
- MEI Type: 0x0E (Read Device Identification)
- Result: Exception Code 1 (Illegal Function)
- **Conclusion:** Device does not implement Modbus Device Identification

### 2. Register Scanning for ASCII Strings
**Status:** ❌ NO DEVICE ID FOUND

Tested register ranges:
- Registers 0-10: Empty
- Registers 40001-40010: Empty
- Registers 100-119: Operational data only
- Registers 200-219: Temperature sensors only
- Registers 240-249: Empty
- Registers 400-419: Empty
- Registers 500-519: Empty
- Registers 1000-5000: Empty
- **Conclusion:** No ASCII device identifiers stored in registers

### 3. Known Operational Registers
**Status:** ✅ WORKING

Successfully read operational data:
- Reg 100 (Operation Mode): 1 (Manual mode)
- Reg 102 (Manual Fan Level): 3 (Level 3)
- Reg 104 (Current Fan Level): 2 (Level 2)
- Reg 115 (Heating/Cooling Function): 0 (Off)
- Reg 133 (Preheater State): 0 (Off)
- Reg 200-219: Temperature sensors (°C × 10)
- Reg 240 (Error Message): 0 (No error)

**Conclusion:** Device works perfectly with operational registers,
but stores NO model/vendor identification in Modbus.

## Alternative Identification Methods

### ✅ HTTP Server (Keil-EWEB)
The device CAN be identified via HTTP:

```bash
curl -v http://10.0.0.139
```

Response headers:
```
HTTP/1.1 401 Unauthorized
Server: Keil-EWEB/2.1
WWW-Authenticate: Basic realm="Embedded WEB Server"
```

**This is the reliable identification method!**

### ⚠️  Hostname/mDNS
Check if device broadcasts hostname via mDNS:
```bash
dns-sd -B _http._tcp local.
```

### ℹ️  Manual Configuration
Since Modbus provides no device identification, users must:
1. Manually specify device model during setup
2. Or auto-detect via HTTP headers + Modbus validation

## Recommendations

### For Integration Discovery:
1. **Detect via HTTP headers** (Keil-EWEB/2.1)
2. **Validate Modbus connection** (port 502)
3. **Read test register** (e.g., reg 100) to confirm it's a WRG device
4. **Assume model:** WRG 134-BP-HK (or let user select)

### Device Model Detection Strategy:
```python
async def identify_device(host):
    # 1. Check HTTP server
    response = await http_client.get(f"http://{host}")
    if "Keil-EWEB" in response.headers.get("Server", ""):
        # 2. Validate Modbus
        if await test_modbus_connection(host, 502):
            # 3. Read known register
            operation_mode = await read_register(host, 100)
            if operation_mode is not None:
                return {
                    "vendor": "Schwörer",
                    "model": "WRG 134-BP-HK",  # or "Unknown WRG"
                    "detection_method": "HTTP + Modbus validation"
                }
    return None
```

## Conclusion

**The Schwörer WRG 134-BP-HK does NOT support Modbus device identification.**

- ❌ No FC 43 support
- ❌ No device info in registers
- ✅ Operational Modbus works perfectly
- ✅ HTTP headers can identify device class

**Recommendation:** Use HTTP-based detection combined with Modbus validation.

---

**Test Date:** 2026-01-20
**Device:** 10.0.0.139:502
**Test Scripts:** 
- test_modbus_id.py
- test_modbus_methods.py
- test_schwoerer_registers.py
