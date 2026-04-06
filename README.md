# 🏸 Badminton AI — Computer Vision & 3D Trajectory Analysis

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37726?style=flat&logo=jupyter&logoColor=white)](https://jupyter.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-5C3EE8?style=flat&logo=opencv&logoColor=white)](https://opencv.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)

A comprehensive research project for **real-time badminton shuttle tracking**, **3D trajectory reconstruction**, and **intelligent game annotation**. Built with production-grade ML pipelines, physics simulation, and professional UI tools.

---

## 🎯 Project Overview

This repository contains an **end-to-end framework** for analyzing badminton footage:

1. **📍 Shuttle Detection** — Uses **TrackNetV3** deep learning to locate the shuttlecock in every frame
2. **🎬 3D Reconstruction** — Reconstructs full 3D flight trajectory from monocular video using physics constraints
3. **👥 Player Tracking** — Detects player positions for physics priors and rally context
4. **🏷️ Dataset Annotation** — Professional PyQt5 labeling tool with undo/redo, export, and 8+ design patterns
5. **📊 Trajectory Analysis** — Spatial coordinate analysis, accuracy reports, and visualization

**Research-grade output:** Annotated videos, 3D plots, accuracy metrics, CSV datasets ready for ML training.

---

## 🗂️ Repository Structure

```
Badminton/
│
├── 3DShuttleTracking/          ⭐ 3D trajectory reconstruction (MonoTrack-based)
│   ├── module1_court_calibration.py      [PnP camera calibration]
│   ├── module2_shuttle_detection.py      [TrackNetV3 + post-processing]
│   ├── module3_pose_estimation.py        [Player tracking]
│   ├── module4_trajectory.py             [Physics ODE + L-BFGS optimization]
│   ├── run_pipeline.py                   [Full end-to-end orchestrator]
│   └── README.md                         [Detailed module reference]
│
├── Shuttle_Tracking/           🚀 Quick 2D shuttle tracking (Colab-friendly)
│   ├── Shuttle_Tracking.ipynb            [TrackNetV3 inference notebook]
│   ├── README.md                         [Setup & usage guide]
│   └── [Optimized for Google Colab + local]
│
├── badminton_labeler/          🏷️ Professional annotation tool
│   ├── main.py                           [Entry point]
│   ├── presenters/main_presenter.py      [MVP controller]
│   ├── models/                           [Data models]
│   ├── services/                         [Video, export, session services]
│   ├── state_machine/marker_fsm.py       [2-frame marking FSM]
│   ├── commands/                         [Undo/redo Command pattern]
│   ├── factories/                        [Factory Method pattern]
│   ├── views/                            [Qt5 UI components]
│   └── README.md                         [8-pattern architecture guide]
│
└── z coor/                     🔢 Z-coordinate analysis
    └── [Spatial trajectory analysis notebooks]
```

---

## ✨ Key Features

### 🔬 3D Trajectory Reconstruction
- **MonoTrack algorithm** (Liu & Wang, CVPR 2022) extended with independent `fx/fy` optimization
- **Physics-based ODE solver:** Gravity + quadratic drag with 7-parameter optimization
- **Constraint enforcement:** Initial height, velocity bounds, court boundaries, direction priors
- **Output:** Annotated video, 3D plots, accuracy reports, trajectory coordinates

### 📹 Shuttle Detection & Tracking
- **TrackNetV3** backbone for high-speed shuttlecock detection
- **Gaussian smoothing + gap interpolation** for noisy sequences
- **Detection quality grades** and comprehensive statistics
- **GPU-accelerated** inference (CUDA 11.8+ / CPU fallback)

### 🎯 Player Position Estimation
- **Dual backend support:** RTMPose-m (OpenMMLab) or MediaPipe Pose
- **Back-projection** to court floor plane using calibrated camera matrix
- **Ankle keypoint averaging** for reliable floor position
- **Used as physics priors** in 3D optimization

### 🏷️ Dataset Annotation Tool
**Professional-grade labeling with 8 design patterns:**

| Pattern | Purpose | Benefit |
|---------|---------|---------|
| **Factory Method** | Centralised segment construction | Single source of validation |
| **Singleton** | Global runtime state (`AppState`) | One truth for frame/fps/segments |
| **Facade** | Thin UI layer (`MainWindow`) | Zero business logic in views |
| **Command** | Granular undo/redo | Efficient delta storage |
| **Observer** | Qt Signal/Slot decoupling | Independent widget testing |
| **Strategy** | Swappable export formats | Add formats without refactoring |
| **State Machine** | 2-frame marking FSM | Eliminates `if len(markers)` chains |
| **Composite** | Self-contained segment cards | Reusable UI components |

**Features:**
- ⌨️ Keyboard-driven workflow (SPACE, ENTER, arrow keys)
- 📊 Real-time filtering, statistics dashboard, shot type customization
- 💾 JSON session save/load with auto-restore
- 🎬 Batch MP4 export with structured naming convention
- 📈 CSV dataset generation (ready for ML pipelines)

### 📐 Coordinate System & Output
```
Origin: near-left corner of doubles court
X  →  court width  (0 → 6.7 m)
Y  →  court length (0 → 13.4 m)
Z  ↑  height above floor (0 = floor)
```

**Output files per shot:**
- `trajectory_3d.npy` — (N_frames, 3) world-space coordinates
- `output_annotated.mp4` — Video with X/Y/Z overlay + trajectory trail
- `trajectory_plots.png` — 4-panel: 3D view, bird-eye, Z over time, error profile
- `accuracy_report.txt` — Full numeric metrics and quality grade

---

## 🚀 Quick Start

### Option 1: Shuttle Tracking Only (2D, Colab-Friendly)
```bash
# Clone repo
git clone https://github.com/vedant273ed/Badminton.git
cd Badminton/Shuttle_Tracking

# Open in Google Colab and run Shuttle_Tracking.ipynb
# Or locally:
pip install torch torchvision opencv-python pandas tqdm
jupyter notebook Shuttle_Tracking.ipynb
```

**Output:** `shuttle_2d.csv` with (frame, x, y) per shot

---

### Option 2: Full 3D Reconstruction Pipeline
```bash
cd Badminton/3DShuttleTracking

# 1. Install core dependencies
pip install -r requirements.txt

# 2. Download TrackNetV3 weights
git clone https://github.com/qaz812345/TrackNetV3.git
cp TrackNetV3/tracknet_weights/tracknet_best.pt tracknet_weights/
cp TrackNetV3/tracknet_weights/inpaintnet_best.pt tracknet_weights/

# 3. (Optional) Install pose backend
pip install mmpose  # or `pip install mediapipe`

# 4. Prepare inputs
# - frame.jpg        one clear static broadcast frame
# - clip.mp4         shot video (20–120 fps, any resolution)

# 5. Run end-to-end
python run_pipeline.py \
    --video clip.mp4 \
    --image frame.jpg \
    --hitter near
```

**Output:** 3D trajectory, annotated video, plots, accuracy metrics

---

### Option 3: Professional Annotation Tool
```bash
cd Badminton/badminton_labeler

# Install dependencies
pip install -r requirements.txt
pip install ffmpeg  # system-wide: brew install ffmpeg

# Generate project scaffold
python generate_project.py

# Launch app
python -m badminton_labeler.main
```

**Workflow:**
1. Open video → `File > Open Video`
2. Press `SPACE` to play
3. Press `ENTER` at shot start & end
4. Press `SHIFT+ENTER` to add labels (shot type, player, etc.)
5. Click `Export All` → get MP4 clips + CSV metadata

---

## 📋 Requirements

| Component | Python | GPU | Key Libraries |
|-----------|--------|-----|-----------------|
| Shuttle Tracking | 3.8+ | Optional | PyTorch, OpenCV, pandas, tqdm |
| 3D Reconstruction | 3.10+ | CUDA 11.8+ | PyTorch, scikit-image, scipy, numba |
| Annotation Tool | 3.9+ | None | PyQt5, OpenCV, ffmpeg |

---

## 🔧 Module Deep Dive

### Module 1: Court Calibration
Click 6 court landmarks (corners + net posts) → solves 3×4 projection matrix via PnP with independent `fx/fy` optimization. **Expected error: 2–5 px.**

### Module 2: Shuttle Detection
TrackNetV3 inference + post-processing (Gaussian smoothing + gap interpolation) → `(N_frames, 2)` NumPy array.

### Module 3: Player Pose Estimation
Detects ankle keypoints → back-projects to court floor → provides physics priors for optimization.

### Module 4: Physics Optimization
L-BFGS-B → Levenberg-Marquardt polish. Minimizes:
```
L = σ·Lr + ‖x(0)−xH‖² + ‖x(tR)−xR‖² + dOut²
```
where:
- `Lr` = reprojection error
- `xH, xR` = hitter/receiver priors
- `dOut` = penalty for landing outside court

**Result:** Full 7-parameter trajectory (x₀, v₀, drag coefficient).

---

## 🎨 Visualization & Output

### Trajectory Plots (4-panel)
```
┌─────────────────┬─────────────────┐
│  3D trajectory  │  Bird-eye view  │
│  (X,Y,Z coords) │  (height map)   │
├─────────────────┼─────────────────┤
│  Z over time    │  Reprojection   │
│  (height arc)   │  error profile  │
└─────────────────┴─────────────────┘
```

### Annotated Video
- Original frame + overlay X/Y/Z coordinates
- Projected 2D trajectory (amber trail)
- Court wireframe + court coordinate labels

### Accuracy Report
```
Reprojection error:  2.34 px ✓
Speed estimate:      65 mph
Net clearance:       1.24 m
Landing position:    (3.2, 12.1) m
Quality grade:       ★★★★★ Excellent
```

---

## 👥 Authors & Contributors

## 👥 Authors & Contributors



---

## 📚 References

### Core Papers
```bibtex
@inproceedings{liu2022monotrack,
  title={MonoTrack: Shuttle Trajectory Reconstruction from Monocular Badminton Video},
  author={Liu, Paul and Wang, Jui-Hsien},
  booktitle={CVPR},
  year={2022}
}

@article{huang2019tracknet,
  title={TrackNet: A Deep Learning Network for Tracking High-Speed and Tiny Objects},
  author={Huang et al.},
  journal={arXiv:1907.03698},
  year={2019}
}
```

### Tools & Frameworks
- **OpenCV** — Computer vision pipeline
- **PyTorch** — Deep learning inference (TrackNetV3)
- **SciPy** — Physics ODE solver & optimization
- **MMPose** — Pose estimation backbone
- **PyQt5** — Professional annotation UI
- **FFmpeg** — Video encoding/cutting

---

## 🤝 Contributing

1. **Test locally** — Each module has a standalone README
2. **Follow patterns** — 8 design patterns codified in `badminton_labeler/`
3. **Add unit tests** — FSM, Factory, Command patterns are independently testable
4. **Update docs** — Keep module READMEs in sync

---

## 📄 License

This project is available for **educational and research purposes**. Please respect the licenses of:
- [TrackNetV3](https://github.com/qaz812345/TrackNetV3) — Model weights & inference code
- [MonoTrack](https://openaccess.thecvf.com/content/CVPR2022/) — Physics optimization reference

---

## 📞 Support & Issues

- 🐛 **Bug reports** → Open an issue with minimal reproducible example
- 💡 **Feature requests** → Describe use case + expected output
- 📖 **Documentation** → Check module-specific READMEs first

---

## 🎯 Roadmap

- [ ] Real-time tracking (streaming API)
- [ ] Multi-camera 3D reconstruction
- [ ] Rally segmentation (automatic shot detection)
- [ ] Player action classification (swing types, court position)
- [ ] Web UI for collaborative annotation

---

**Built with 🏸 by the Badminton AI team — April 2026**
