# PipeOra

Modern, lightweight, and exclusive Linux desktop audio manager built with Python 3 and PySide6 (Qt 6) for PipeWire, WirePlumber, and BlueZ.

Designed specifically for Arch Linux and Parch Linux on KDE Plasma (Wayland & X11).

---

## Highlights

- **Pure Audio Output Focus**: Clean interface strictly focused on playback output management, with zero unnecessary microphone clutter.
- **Smart Headset Mode Routing**: Seamless switching between High Fidelity Stereo (A2DP AAC/SBC at 48kHz) and Communication Mode (HFP), automatically migrating active audio streams and system default sources.
- **Real-Time PipeWire Integration**: Real-time event monitoring through native IPC without CPU-heavy polling.
- **Graphite Dark UI**: Designed according to modern Linux desktop ergonomics, with native RTL layout and high-precision vector SVG icons.
- **Bluetooth Device Management**: Direct D-Bus communication with BlueZ for instant pairing, connect/disconnect, battery status, and favorite auto-switch.
- **App Stream Mixer**: Per-application volume control and sink reassignment.
- **Desktop Integration**: System tray menu, single-instance socket server, and XDG Autostart support.

---

## Installation

### From Source

```bash
git clone https://github.com/Amirprgrmr/PipeOra.git
cd PipeOra
./run.sh
```

### Arch Linux / Parch Linux (PKGBUILD)

```bash
cd packaging
makepkg -si
```

---

## Architecture Overview

```
PipeOra
├── Core Layer
│   ├── AudioManager        # PipeWire sink & stream management
│   ├── ProfileManager      # Card profile & A2DP/HFP routing engine
│   ├── BluetoothManager    # BlueZ D-Bus interface
│   ├── SystemDetector      # Systemd, PipeWire & tool diagnostics
│   └── ConfigManager       # XDG JSON configuration persistence
├── Services
│   ├── EventWorker         # Background QThread for real-time pactl events
│   └── AutostartService    # XDG desktop autostart configuration
└── UI Layer (PySide6 / Qt 6)
    ├── MainWindow          # Primary frame with sidebar navigation
    ├── DashboardPage       # Hero card, active sinks, and quick toggles
    ├── DevicesPage         # Complete sink cards and per-app stream mixer
    ├── BluetoothPage       # Paired devices, scanning, and connect triggers
    └── SettingsPage        # Preferences, autostart, and system health
```

---

## Author & License

- **Developer**: Amirali Homayoonzadeh ([amirprgrmr.ir](https://amirprgrmr.ir))
- **License**: MIT
