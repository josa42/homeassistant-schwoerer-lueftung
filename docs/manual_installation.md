# Manual installation

The [button in the README](../README.md#installation) does all of this in one
click. These steps are for when that button does not work, or when you would
rather not use HACS at all.

## Adding the repository to HACS by hand

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Open HACS → Integrations
3. Click the three dots menu (top right) → Custom repositories
4. Add repository URL: `https://github.com/josa42/homeassistant-schwoerer-lueftung`
5. Category: Integration
6. Click "Add"
7. Click "Download" on the Schwörer Lüftung card
8. Restart Home Assistant

## Without HACS

1. Download the latest release from [GitHub releases](https://github.com/josa42/homeassistant-schwoerer-lueftung/releases)
2. Extract the `custom_components/schwoerer_lueftung` folder
3. Copy it to your Home Assistant `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── schwoerer_lueftung/
   ```
4. Restart Home Assistant

Updating means repeating this with the new release and restarting again. HACS
does it in one click instead, which is why it is the recommended route.
