# PULSAR KiCad Library

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A KiCad library containing schematic symbols, PCB footprints, and 3D STEP models for components used in the **PULSAR** competition rover.

## Components Included

| Component | Type | Description |
|-----------|------|-------------|
| BC846A | NPN BJT | SOT-23, 65V, 100mA |
| LDL212PV33R | LDO Regulator | 3.3V, VFDFPN-6 |
| LTV-356T-TP1-B | Optocoupler | Transistor output |
| PXP062-60QLJ | P-ch MOSFET | 40V Trench MOSFET |
| ST1S14PHR | Buck Converter | SOIC-8 |
| STPS3L60U | Schottky Diode | SMB package |
| VLS6045EX-6R8M | Inductor | 6.8µH, SMD |

## Install via KiCad Plugin & Content Manager

1. Open KiCad → **Plugin and Content Manager**
2. Click **Manage** (repository dropdown) → **Add Repository**
3. Paste this URL:

```
https://raw.githubusercontent.com/Alex-C-EE/PULSAR-KiCad-Lib/main/docs/repository.json
```

4. Select **PULSAR KiCad Repository** from the dropdown
5. Click **PULSAR KiCad Library** → **Install** → **Apply Pending Changes**

Libraries will be automatically added to your symbol and footprint tables with the `PCM_` prefix.

## Manual Install

Download the latest `.zip` from [Releases](https://github.com/Alex-C-EE/PULSAR-KiCad-Lib/releases) and extract to your KiCad libraries path.

## Building a Release

```bash
python scripts/package.py --version 1.0.0
```

This creates `PULSAR-KiCad-Lib-1.0.0.zip` and updates `docs/packages.json` with the correct SHA256 hash and sizes.

## License

This library is released under the MIT License.

© 2025 Alexandru Constantinescu
