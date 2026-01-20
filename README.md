# Home Assistant Integration for BIC WRG 134-BP-HK

This is a custom Home Assistant integration for the BIC WRG 134-BP-HK ventilation system with heat recovery.

## Features

- Modbus TCP communication
- Climate control entity
- Temperature sensors
- Configuration via UI

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "BIC WRG" in HACS
3. Install the integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/schwoerer_lueftung` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "BIC WRG"
4. Enter your device's IP address, port (default: 502), and Modbus slave ID (default: 1)

## Development

### Setup Development Environment

```bash
# Install dependencies
make install

# Run linter
make lint

# Run tests
make test
```

### Local Testing with Docker

The integration includes a Docker Compose setup that runs a local Home Assistant instance with your integration automatically loaded.

```bash
# Start Home Assistant with your integration
make dev-up
# Access at: http://localhost:8123

# View logs
make dev-logs

# Restart after code changes
make dev-restart

# Stop Home Assistant
make dev-down
```

The Home Assistant instance will be available at `http://localhost:8123`. Configuration is stored in the `config/` directory (git-ignored). Your integration will be automatically available in the Home Assistant integrations list.

### Continuous Integration

GitHub Actions workflows are set up for:
- **CI** (`ci.yml`): Runs linting, tests, and validation on every push and PR
- **Release** (`release.yml`): Automatically creates a release with zip file when you push a tag

### Release

```bash
# Create and push a new release
./scripts/release.sh 1.0.0
```

This script will:
1. Update the version in `manifest.json`
2. Run tests and linting
3. Create a git tag
4. Push to GitHub (triggers automatic release creation)

## TODO

The integration structure is set up, but you need to:

1. **Define Modbus Register Mappings**: Update `modbus_client.py` with the actual register addresses for your WRG 134-BP-HK device
2. **Implement Sensors**: Uncomment and configure the sensors in `sensor.py` based on available data points
3. **Implement Climate Controls**: Complete the climate entity implementation in `climate.py` with actual register read/write operations
4. **Test**: Test the integration with your actual device

## Register Mapping

You'll need to consult the WRG 134-BP-HK Modbus documentation to map:
- Temperature readings (supply, extract, outdoor, etc.)
- Operating modes
- Fan speeds
- Setpoints
- Status indicators

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

MIT License
