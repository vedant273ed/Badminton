# 🏸 **Badminton Court Homography Engine**  
**From chaotic camera angles to perfect top-down court views** ✨

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org)
[![Ultralytics YOLOv8](https://img.shields.io/badge/YOLOv8-Pose-orange.svg)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10-red.svg)](https://opencv.org)
[![Roboflow](https://img.shields.io/badge/Dataset-Roboflow-00C853.svg)](https://roboflow.com)

---

### 🎯 **One-click transformation**  
Detect court keypoints → Compute homography → Project players onto a **meter-accurate top-down court** with shadows, labels, and net lines.

**Before** (real broadcast angle) → **After** (perfect overhead view)

![Demo](https://github.com/user-attachments/assets/homography-demo.png)
*(Camera view with detected players → Clean top-down court with projected positions)*

---

## ✨ **Key Features**

- **8-Keypoint Court Detection** (4 corners + 4 net points) using YOLOv8-pose
- **Professional Homography Engine** with real-world badminton dimensions (6.1m × 13.4m)
- **Player Foot Projection** with realistic shadows + auto-labeling (P1, P2…)
- **Built-in Debug Tools** — keypoint order checker, off-court warnings
- **Robust Data Pipeline** — cleaned 5,553-image dataset + 5× augmentation
- **Ready-to-Use Visualization** — matplotlib court board with meter ticks

---

