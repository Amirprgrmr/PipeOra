# Seamless Headset Profile & Mic Auto-Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the Bluetooth headset profile bounce issue when switching to A2DP (High Fidelity Music) and automate microphone input switching (to system mic on A2DP, and to headset mic on HFP) without requiring manual adjustments in KDE Plasma settings.

**Architecture:** 
1. Enhance `ProfileManager` with intelligent routing orchestration:
   - When switching to **A2DP (Music Mode)**: Locate non-Bluetooth fallback microphone (`alsa_input.*`), switch default source to it, migrate active recording streams (`source-outputs`), and then apply the `a2dp-sink` profile. This prevents WirePlumber from rejecting or immediately reverting the profile change due to active capture streams or default source binding.
   - When switching to **HFP (Call Mode)**: Switch profile to `headset-head-unit`, detect the newly spawned `bluez_input.<MAC>` source, set it as the system default source, and migrate active recording streams to it.
2. Maintain strict adherence to the application's core output-focused design: No microphone volume sliders or recording controls are added to the UI; this is handled transparently as an underlying profile and device routing service.

**Tech Stack:** Python 3, PySide6, PipeWire 1.6+, WirePlumber, pactl CLI/JSON, BlueZ.

**Spec:** User bug report: Switching to A2DP reverts back to HFP unless the microphone in KDE Plasma Input Devices is manually switched to the internal mic; switching to HFP does not automatically select the headset microphone in settings.

## Global Constraints
- Target OS: Parch Linux / Arch Linux (KDE Plasma on Wayland).
- Zero fake, simulated, or mocked production logic (all operations must affect real PipeWire/WirePlumber state).
- No microphone sliders, recording controls, or input tabs exposed in the UI.
- All commands executed with argument lists (no `shell=True`) and structured JSON parsing where applicable.
- Full test coverage with automated unit tests (`pytest`).

## Review Focus
1. **Fallback mic detection:** What if the laptop has multiple input sources or no built-in mic? Ensure robust fallback selection (prefer `alsa_input.*`, fallback to any non-bluez, non-monitor source).
2. **Active capture stream migration:** If an app (e.g. browser, meeting app, Antigravity) is recording when switching modes, ensure streams move smoothly without audio server crashes or stream disconnection.
3. **Race conditions during HFP source creation:** PipeWire takes 50-150ms to spawn `bluez_input` after `set-card-profile`. Implement retry polling (up to 1.5s with 50ms intervals) so setting default source never fails.
4. **WirePlumber autoswitching coexistence:** Ensure WirePlumber doesn't fight the profile switch by pre-emptively moving sources before A2DP transition.
5. **UI responsiveness:** Profile switching with stream migration must run asynchronously or with minimal latency so the GUI remains silky smooth.

---

### Task 1: Add Audio Source & Stream Migration Utilities to `AudioManager`

**Files:**
- Modify: `app/core/audio_manager.py:160-230`
- Test: `tests/test_audio_manager.py`

- [ ] **Step 1: Write failing test in `tests/test_audio_manager.py`**
  - Test `get_input_sources(exclude_monitors=True, exclude_bluetooth=True)` returns only hardware fallback microphones.
  - Test `set_default_source(source_name)` invokes `pactl set-default-source`.
  - Test `move_active_recording_streams(target_source_name)` retrieves source outputs and invokes `pactl move-source-output`.
- [ ] **Step 2: Run test to confirm failure**
  - Run: `.venv/bin/python -m pytest tests/test_audio_manager.py -k "source"`
- [ ] **Step 3: Implement methods in `app/core/audio_manager.py`**
  - Add `get_hardware_fallback_source() -> Optional[str]`
  - Add `set_default_source(source_name: str) -> bool`
  - Add `move_recording_streams(target_source: str, from_source: Optional[str] = None) -> int`
- [ ] **Step 4: Run tests to verify pass**
  - Run: `.venv/bin/python -m pytest tests/test_audio_manager.py`
- [ ] **Step 5: Commit changes**
  - `git commit -m "feat(audio): add fallback source detection and stream migration in AudioManager"`

---

### Task 2: Implement Pre-Switch and Post-Switch Routing in `ProfileManager`

**Files:**
- Modify: `app/core/profile_manager.py:150-195`
- Test: `tests/test_profile_manager.py`

- [ ] **Step 1: Write failing test in `tests/test_profile_manager.py`**
  - Test `set_headset_mode(card_id, "a2dp")` moves streams and switches default source to internal mic before switching profile.
  - Test `set_headset_mode(card_id, "hfp")` switches profile, waits for `bluez_input`, sets it as default source, and migrates streams.
- [ ] **Step 2: Run test to confirm failure**
  - Run: `.venv/bin/python -m pytest tests/test_profile_manager.py -k "test_headset_mode_switching"`
- [ ] **Step 3: Implement seamless routing logic in `ProfileManager`**
  - Inject or instantiate `AudioManager` to manage sources/streams during headset profile transitions.
  - In `_switch_to_a2dp_seamless(card_id)`:
    1. Query fallback hardware source (internal mic).
    2. Set default source to fallback mic.
    3. Move any active `source-outputs` away from the Bluetooth mic to fallback mic.
    4. Call `set_card_profile(card_id, a2dp_profile_name)`.
  - In `_switch_to_hfp_seamless(card_id)`:
    1. Call `set_card_profile(card_id, hfp_profile_name)`.
    2. Poll for `bluez_input.<MAC>` (up to 1.5s with 50ms intervals).
    3. Set default source to `bluez_input.<MAC>`.
    4. Move active `source-outputs` to `bluez_input.<MAC>`.
- [ ] **Step 4: Run tests to verify pass**
  - Run: `.venv/bin/python -m pytest tests/test_profile_manager.py`
- [ ] **Step 5: Commit changes**
  - `git commit -m "feat(profile): implement seamless A2DP/HFP profile switching with automatic source routing"`

---

### Task 3: UI Feedback and Integration Verification in `HeadsetModeCard`

**Files:**
- Modify: `app/ui/components/headset_mode_card.py`
- Test: `tests/test_components.py`

- [ ] **Step 1: Update `HeadsetModeCard` to reflect automated mic routing**
  - Update notice labels to inform user:
    - In A2DP mode: "میکروفن به میکروفن داخلی سیستم منتقل شد تا کیفیت پخش استریوی AAC حفظ شود."
    - In HFP mode: "میکروفن هدفون برای مکالمه فعال و به عنوان ورودی اصلی سیستم تنظیم شد."
  - Ensure button state shows transient loading/switching text if needed.
- [ ] **Step 2: Verify `HeadsetModeCard` unit tests pass**
  - Run: `.venv/bin/python -m pytest tests/test_components.py`
- [ ] **Step 3: Commit changes**
  - `git commit -m "feat(ui): update HeadsetModeCard feedback for automated mic routing"`

---

### Task 4: Full System & Live Hardware Integration Verification

**Files:**
- Test: `tests/run_all_tests.py`

- [ ] **Step 1: Execute test suite across all 26+ tests**
  - Run: `.venv/bin/python -m pytest tests/`
- [ ] **Step 2: Execute live hardware test with QCY T13 ANC2**
  - Run: `.venv/bin/python tests/run_all_tests.py`
  - Verify switching from GUI and CLI:
    1. Switching to A2DP maintains A2DP without bouncing back to HFP.
    2. `pactl get-default-source` points to `alsa_input.pci-0000_00_1f.3.analog-stereo`.
    3. Switching to HFP sets `pactl get-default-source` to `bluez_input.84:AC:60:C9:02:74`.
- [ ] **Step 3: Update documentation and walkthrough artifact**
  - Update `docs/superpowers/plans/` and artifact `walkthrough.md`.
