# 🏸 Badminton Dataset Labeler

> **A professional-grade video annotation tool for badminton shot classification — built with 8 software design patterns for scalability, testability, and clean architecture.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-MVP%20%2B%208%20Patterns-red?style=flat-square)]()
<img width="1194" height="773" alt="image" src="https://github.com/user-attachments/assets/3d78ba5f-1e33-40a1-bde8-2fd54de61926" />
<img width="835" height="475" alt="image" src="https://github.com/user-attachments/assets/a46752cf-b991-4312-b9dd-16fbccdece3f" />
<img width="376" height="477" alt="image" src="https://github.com/user-attachments/assets/54e114b6-24a5-414b-803e-41f217589e8f" />

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Design Patterns](#-design-patterns-deep-dive)
- [Architecture Overview](#-architecture-overview)
- [Features](#-features)
- [Keyboard Shortcuts](#-keyboard-shortcuts)
- [Export Formats](#-export-formats)
- [Configuration](#-configuration)
- [Contributing](#-contributing)

---

## 🎯 What It Does

The Badminton Dataset Labeler is a desktop application for **frame-accurate video annotation** of badminton footage. It lets researchers and coaches:

- **Mark** shot segments with frame-level precision
- **Label** each segment with rich metadata (shot type, player, backhand, hit area, rally number)
- **Export** annotated clips as MP4 files with a structured CSV dataset — ready for machine learning pipelines

It was built for real research workflows, which means it handles autosave, session restore, undo/redo, filtering, previewing, and batch export — all inside a dark-themed, keyboard-driven UI.

---

## ⚡ Quick Start

### 1. Prerequisites

```bash
# Python 3.9 or higher
python --version

# ffmpeg must be installed system-wide (for MP4 export)
# Windows:  winget install ffmpeg
# macOS:    brew install ffmpeg
# Linux:    sudo apt install ffmpeg
```

### 2. Install & Generate

```bash
# Clone or download the repo, then:
pip install -r requirements.txt

# Run the scaffold generator (creates all project files):
python generate_project.py

# Launch the app (run from the folder CONTAINING badminton_labeler/):
python -m badminton_labeler.main
```

### 3. Basic Workflow

```
1. Click "Open Video"  →  load your .mp4 / .avi / .mov file
2. Press SPACE         →  play / pause
3. Press ENTER         →  mark start frame of a shot
4. Navigate forward    →  find end of shot
5. Press ENTER again   →  mark end frame (segment created)
6. Press SHIFT+ENTER   →  open label dialog, fill in shot info
7. Repeat for all shots
8. Click "Export All"  →  choose output folder → get MP4 clips + CSV
```

---

## 📁 Project Structure

```
badminton_labeler/
│
├── main.py                          # Entry point — wires View + Presenter
├── constants.py                     # Shot types, colors, timing config
├── app_state.py                     # ★ Singleton: global runtime state
│
├── models/
│   ├── segment.py                   # Segment dataclass (pure data, no UI)
│   └── session.py                   # Session dataclass (serialisable snapshot)
│
├── commands/
│   ├── base_command.py              # Abstract Command interface
│   └── segment_commands.py         # ★ Add / Edit / Delete + CommandHistory
│
├── state_machine/
│   └── marker_fsm.py               # ★ Marker FSM (State pattern)
│
├── services/
│   ├── video_service.py            # OpenCV wrapper (seek, read, sequential)
│   ├── session_service.py          # JSON save / load
│   └── export_strategy.py         # ★ Strategy: CSV / JSON / MP4 exporters
│
├── factories/
│   ├── segment_factory.py          # ★ Factory Method: Segment construction
│   └── widget_factory.py           # ★ Factory Method: Qt widget creation
│
├── views/
│   ├── main_window.py              # ★ Facade: thin UI shell (zero logic)
│   ├── widgets/
│   │   ├── segment_card.py         # ★ Composite: self-contained card widget
│   │   ├── timeline_widget.py      # Visual scrub bar with segment overlay
│   │   └── stats_panel.py          # Painted bar chart of shot distribution
│   └── dialogs/
│       ├── label_dialog.py         # Shot metadata form
│       ├── hit_area_dialog.py      # 4×4 court grid selector
│       ├── mini_player_dialog.py   # Looping clip preview
│       └── shortcuts_dialog.py     # Keyboard reference
│
└── presenters/
    └── main_presenter.py           # ★ MVP brain — ALL business logic
```

★ = design pattern hotspot

---

## 🏗️ Design Patterns Deep Dive

This project applies **8 classical software design patterns**. Here's exactly where each one lives and why it was chosen:

---

### 1. 🏭 Factory Method — Centralised Construction

**Files:** `factories/segment_factory.py`, `factories/widget_factory.py`

```python
# Before (scattered direct construction):
self.segments.append({"start": start, "end": end, "shot_type": "", "labeled": False})

# After (Factory Method — one place, validated):
seg = SegmentFactory.create(start=100, end=250)
seg = SegmentFactory.from_label_data(start, end, label_dialog_output)
```

**Why:** Segment construction happened in 4 different places in the original code, each with slightly different defaults. The factory centralises validation (too-short / too-long checks) and guarantees consistent objects.

---

### 2. 🔒 Singleton — One Source of Truth

**File:** `app_state.py`

```python
# Anywhere in the codebase:
state = AppState.instance()
state.session.segments   # always the same list
state.current_frame      # always the real current frame
state.fps                # always the loaded video's FPS
```

**Why:** The original `BadmintonLabeler` class stored `self.segments`, `self.fps`, `self.markers` etc. — all scattered across a 700-line class. `AppState` is the single shared runtime object that all layers (Presenter, Services, Commands) read and write through.

---

### 3. 🎭 Facade — Thin UI Layer

**File:** `views/main_window.py`

```python
# MainWindow only does two things:
# 1. Build widgets
# 2. Call presenter methods / expose update methods

class MainWindow(QMainWindow):
    def display_frame(self, rgb_array): ...      # presenter calls this
    def set_status(self, text): ...              # presenter calls this
    def refresh_segments(self, segments): ...    # presenter calls this
    # NO business logic. NO service calls. NO state reads.
```

**Why:** In the original code, `BadmintonLabeler` was simultaneously the window, the controller, the video player, the export engine, and the session manager. The Facade pattern makes `MainWindow` purely a display surface — impossible to have logic bugs in UI code.

---

### 4. ↩️ Command — Granular Undo/Redo

**File:** `commands/segment_commands.py`

```python
# Each user action is a discrete, reversible object:
cmd = AddSegmentCommand(segment)
cmd = DeleteSegmentCommand(index)
cmd = EditSegmentCommand(index, new_data)

# CommandHistory manages the stacks:
history.execute(cmd)   # do + push to undo stack
history.undo()         # pop + reverse
history.redo()         # pop + re-execute
```

**Why:** The original undo/redo used `copy.deepcopy()` of the entire segments list on every action — expensive and coarse. The Command pattern stores only the delta (what changed), making undo/redo O(1) per action instead of O(n).

---

### 5. 📡 Observer — Decoupled UI Updates

**Pattern:** Qt Signals & Slots, used formally throughout

```python
# TimelineWidget emits — it doesn't know who's listening:
self.seek_requested = pyqtSignal(int)

# SegmentCard emits — doesn't know the parent:
self.preview_requested = pyqtSignal(int)
self.edit_requested    = pyqtSignal(int)
self.delete_requested  = pyqtSignal(int)

# Presenter listens and responds:
timeline.seek_requested.connect(presenter.seek)
card.edit_requested.connect(presenter.edit_segment)
```

**Why:** In the original, child widgets called parent methods directly (tight coupling). With Observer, widgets emit events and the Presenter decides what to do — widgets become independently reusable.

---

### 6. 🔀 Strategy — Swappable Export Formats

**File:** `services/export_strategy.py`

```python
# All strategies share the same interface:
class ExportStrategy(ABC):
    def export(self, segments, output_dir, match_id, fps, video_path) -> int: ...

# Swap at runtime — no caller changes needed:
context = ExportContext(strategy=CSVExportStrategy())
context.set_strategy(MP4ExportStrategy())   # switch to MP4
context.set_strategy(JSONExportStrategy())  # switch to JSON

# Export both CSV and MP4 in one click:
csv_count = ExportContext(CSVExportStrategy()).export(...)
mp4_count = ExportContext(MP4ExportStrategy()).export(...)
```

**Why:** The original export was a 60-line monolithic method that always ran ffmpeg + CSV together. Strategy lets you add a new format (e.g. COCO JSON, YOLO annotations) without touching existing code.

---

### 7. 🚦 State — Marker Finite State Machine

**File:** `state_machine/marker_fsm.py`

```python
# Before (brittle if/elif chains scattered in mark_frame()):
if len(self.markers) == 1:
    self.marker_status.setText(...)
elif len(self.markers) >= 2:
    start, end = sorted(self.markers[:2])
    self.markers = []
    ...

# After (explicit FSM — states are self-documenting):
class MarkerState(Enum):
    IDLE       = auto()   # no pending markers
    MARK_START = auto()   # start marked, waiting for end

fsm.mark(frame)    # transitions IDLE → MARK_START → IDLE+segment
fsm.cancel()       # transitions MARK_START → IDLE
```

**Why:** The original had `if len(markers) == 1 / >= 2` spread across 3 methods. The FSM makes the two-step marking workflow an explicit, testable state machine with clear transitions and callbacks.

---

### 8. 🧩 Composite — Reusable Segment Cards

**File:** `views/widgets/segment_card.py`

```python
# Each SegmentCard is a complete, self-contained UI component:
card = SegmentCard(segment, index)
card.preview_requested.connect(...)  # just wire signals
card.edit_requested.connect(...)
card.delete_requested.connect(...)

# The parent panel treats ALL cards identically:
for idx, seg in enumerate(segments):
    card = SegmentCard(seg, idx)
    self.seg_inner_layout.addWidget(card)  # uniform treatment
```

**Why:** The original built segment cards inline with 30+ lines of widget construction repeated for every refresh. `SegmentCard` is a self-rendering composite that owns its title, subtitle, and action buttons — add a new button in one place, not every refresh loop.

---

### Pattern Summary Table

| # | Pattern | File | Benefit |
|---|---------|------|---------|
| 1 | **Factory Method** | `factories/segment_factory.py` | Centralised, validated construction |
| 2 | **Singleton** | `app_state.py` | One source of truth for runtime state |
| 3 | **Facade** | `views/main_window.py` | Zero logic in UI — pure display shell |
| 4 | **Command** | `commands/segment_commands.py` | Efficient, granular undo/redo history |
| 5 | **Observer** | Qt Signals throughout | Decoupled, independently testable widgets |
| 6 | **Strategy** | `services/export_strategy.py` | Add new export formats without rewriting |
| 7 | **State** | `state_machine/marker_fsm.py` | Eliminates `if len(markers)` chains |
| 8 | **Composite** | `views/widgets/segment_card.py` | Reusable, self-contained UI components |

---

## 🏛️ Architecture Overview

```
<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/e77bf7d2-eff0-4553-afa7-0f5f02847a06" />

```

**Data flow :**
1. User presses a key → `MainWindow` catches it → calls `Presenter.mark_frame()`
2. Presenter tells `MarkerFSM.mark(current_frame)`
3. FSM transitions state; on second mark, fires `on_segment_ready(start, end)`
4. Presenter runs `SegmentFactory.create(start, end)` → wraps in `AddSegmentCommand` → executes via `CommandHistory`
5. Command pushes segment into `AppState.session.segments`
6. Presenter calls `MainWindow.refresh_segments(segments)` → MainWindow rebuilds `SegmentCard` composites

---

## ✨ Features

### Video Playback
- Frame-accurate scrubbing with timeline overlay
- Variable speed: 0.25x, 0.5x, 1x, 2x
- Keyboard-driven step (1 frame / 30 frames)
- Precise timer (`Qt.PreciseTimer`) for smooth playback

### Annotation
- Two-click mark-start / mark-end workflow (via FSM)
- Short segment warning (< 5 frames) and long segment warning (> 300 frames)
- Label dialog: rally number, player ID, shot type, backhand, around-head, hit area
- 4×4 court grid selector for spatial hit location
- Segment preview in looping mini-player

### Session Management
- JSON session save / load
- Auto-save every 5 minutes to `<video>_autosave.json`
- Auto-restore last session on launch
- Full undo / redo with granular Command history

### Filtering & Statistics
- Filter segments by shot type in real time
- Rally breakdown tab (shots per rally)
- Stats tab: painted bar chart of shot type distribution

### Export
- MP4 clips via `ffmpeg` with structured filename convention:
  `{match_id}_R{rally}_S{shot}_{player}_{type}_BH{0/1}_AH{0/1}_{area}.mp4`
- CSV metadata file with all label fields
- JSON segment dump (all segments including unlabeled)

### Shot Types (customisable)
```
Short Serve  Long Serve  Toss    Lift      Dribble
Smash        Jump Smash  Tab     Block     Drive
Low Drop     High Drop   Netkill
```
Add or remove shot types at runtime via **"+ Shot Types"** button.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `→` / `←` | Step 1 frame |
| `Shift+→` / `Shift+←` | Step 30 frames |
| `Enter` | Mark start / end frame |
| `Shift+Enter` | Label last unlabeled segment |
| `Delete` | Cancel pending marker |
| `[` | Jump to previous segment |
| `]` | Jump to next segment |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo |
| `Ctrl+S` | Export all clips |
| `?` | Show shortcuts dialog |

---

## 📤 Export Formats

### MP4 Clips
Each labeled segment is cut using `ffmpeg`:
```
M01_R001_S01_P1_Smash_BH0_AH0_7.mp4
 │    │    │   │   │    │   │  └── hit area (1-16)
 │    │    │   │   │    │   └───── around head (0/1)
 │    │    │   │   │    └───────── backhand (0/1)
 │    │    │   │   └────────────── shot type
 │    │    │   └────────────────── player ID
 │    │    └────────────────────── shot number in rally
 │    └─────────────────────────── rally number
 └──────────────────────────────── match ID
```

### CSV Dataset
```csv
filename,match_id,rally_number,shot_number,player_id,shot_type,backhand,around_head,hit_area,frame_start,frame_end
M01_R001_S01_P1_Smash_BH0_AH0_7.mp4,M01,1,1,P1,Smash,0,0,7,450,523
```

---

## ⚙️ Configuration

All tunable constants live in `constants.py`:

```python
SHORT_SEGMENT_FRAMES  = 5        # warn if segment shorter than this
LONG_SEGMENT_FRAMES   = 300      # warn if segment longer than this
AUTOSAVE_INTERVAL_MS  = 300000   # autosave every 5 minutes
DEFAULT_FPS           = 30.0     # fallback if video FPS undetectable
DEFAULT_MATCH_ID      = "M01"

SHOT_TYPES = [
    "Short Serve", "Long Serve", "Toss", ...
]

SHOT_COLORS = {
    "Smash": "#e74c3c",
    "Drive": "#27ae60",
    ...
}
```

---

## 🧪 Testing Tips

Because of the pattern-based architecture, individual layers are independently testable:

```python
# Test the FSM without any UI:
from badminton_labeler.state_machine.marker_fsm import MarkerFSM

segments_created = []
fsm = MarkerFSM(
    on_segment_ready=lambda s, e: segments_created.append((s, e)),
    on_status_change=lambda msg: None,
)
fsm.mark(100)
fsm.mark(250)
assert segments_created == [(100, 250)]

# Test SegmentFactory:
from badminton_labeler.factories.segment_factory import SegmentFactory, SegmentValidationError
seg = SegmentFactory.create(100, 250)
assert seg.length == 150

# Test CommandHistory:
from badminton_labeler.commands.segment_commands import AddSegmentCommand, CommandHistory
from badminton_labeler.app_state import AppState

AppState.reset()
history = CommandHistory()
seg = SegmentFactory.create(10, 50)
history.execute(AddSegmentCommand(seg))
assert len(AppState.instance().session.segments) == 1
history.undo()
assert len(AppState.instance().session.segments) == 0
```

---

## 🤝 Contributing

### Adding a New Export Format

Create a new Strategy in `services/export_strategy.py`:



### Adding a New Shot Type at Runtime

Click **"+ Shot Types"** in the toolbar — no code change needed.

To add permanently, edit `SHOT_TYPES` in `constants.py`.

### Adding a New Undoable Action

```python
class MyNewCommand(BaseCommand):
    def execute(self): ...
    def undo(self):   ...
  
# In presenter:
self._history.execute(MyNewCommand(...))
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `PyQt5` | ≥ 5.15 | UI framework |
| `opencv-python` | ≥ 4.5 | Video decoding |
| `ffmpeg` | any (system) | MP4 clip cutting |

```bash
pip install PyQt5 opencv-python
```

---

*8 design patterns export-ready*

</div>x
