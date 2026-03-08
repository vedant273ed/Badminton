# 🏸 Badminton Shuttle Tracking using TrackNetV3

This project demonstrates how to use **TrackNetV3** — a deep learning model — to automatically detect and track a badminton shuttlecock in match videos. The notebook runs the pre-trained model on any badminton video and produces an annotated output video with the shuttle's position and trajectory drawn on each frame.

---

## 📌 What This Project Does

1. Clones the [TrackNetV3](https://github.com/qaz812345/TrackNetV3) repository and installs dependencies
2. Runs shuttle tracking inference using pre-trained **TrackNet** and **InpaintNet** model weights
3. Outputs a `.csv` file with frame-by-frame shuttle coordinates (X, Y, Visibility)
4. Draws a 🟡 **yellow dot** (shuttle position) and 🟢 **green trail** (last 3 frames) on each video frame
5. Saves the final annotated video as `.mp4`

---

## 📷 Sample Output

> Original frame (left) vs Tracked output with shuttle trajectory (right)

![Shuttle Tracking Output](https://github.com/user-attachments/assets/a1a87c8a-e836-4fae-9be3-62f7eaa328f2)

---


## ⚙️ Requirements

- Python 3.8+
- PyTorch (GPU strongly recommended)
- opencv-python
- pandas
- tqdm
- parse

Install all dependencies by running the cells in the notebook, or manually:

```bash
pip install parse tqdm opencv-python pandas torch torchvision
```

---

## 🚀 How to Run

### ▶️ Option 1 — Google Colab (Recommended)

1. Open the notebook in [Google Colab](https://colab.research.google.com/)
2. Set the runtime to **GPU** → Runtime > Change runtime type > T4 GPU
3. Upload your video to `/content/` or place model weights in your Google Drive
4. Update the **video path** and **model weights path** in the prediction cells
5. Run all cells top to bottom

### 💻 Option 2 — VS Code / Local Machine

1. Clone this repo and open the notebook in VS Code (install the **Jupyter extension**)
2. Clone TrackNetV3 manually:
   ```bash
   git clone https://github.com/qaz812345/TrackNetV3.git
   cd TrackNetV3
   pip install -r requirements.txt
   ```
3. Download the pre-trained weights — `TrackNet_best.pt` and `InpaintNet_best.pt` — from the [TrackNetV3 releases](https://github.com/qaz812345/TrackNetV3) or your own source
4. In the notebook, replace all `/content/` paths with your **local paths**, for example:
   ```python
   VIDEO_INPUT      = "C:/Users/yourname/videos/your_video.mp4"   # Windows
   # or
   VIDEO_INPUT      = "/home/yourname/videos/your_video.mp4"      # Linux/Mac

   TRACKNET_WEIGHTS = "/path/to/TrackNet_best.pt"
   INPAINT_WEIGHTS  = "/path/to/InpaintNet_best.pt"
   ```
5. Skip or comment out the **Google Drive mount cell** (it is Colab-specific)
6. Run all cells

---

## 📂 Model Weights

The notebook requires two pre-trained weight files:

| File | Purpose |
|------|---------|
| `TrackNet_best.pt` | Detects shuttle position in each frame |
| `InpaintNet_best.pt` | Recovers shuttle position in occluded/missing frames |

You can get these weights from the official [TrackNetV3 repository](https://github.com/qaz812345/TrackNetV3).

---

## 📤 Output Files

After running the prediction, the `outputs/` folder will contain:

| File | Description |
|------|-------------|
| `<video_name>_ball.csv` | Shuttle X, Y coordinates and visibility per frame |
| `<video_name>_predict.mp4` | Raw prediction output video |
| `FINAL_TRACKED_VIDEO.mp4` | Final video with dots and trail drawn on frames |

---

## 🛠️ Troubleshooting

**VideoWriter codec error on Linux/Colab (`h264_v4l2m2m`)**  
The notebook includes a patch that automatically switches to the `MJPG` or `mp4v` codec. If you still face issues locally, try changing the codec manually:
```python
fourcc = cv2.VideoWriter_fourcc(*'mp4v')   # works on most systems
# or
fourcc = cv2.VideoWriter_fourcc(*'XVID')   # alternative
```

**`ckpts` folder not found**  
Make sure you pass the correct full path to your weight files in the `--tracknet_file` and `--inpaintnet_file` arguments.

**Slow on CPU**  
TrackNetV3 is significantly faster on GPU. On CPU, inference may take several minutes per video. Use Google Colab free GPU tier if you don't have a local GPU.

---

## 🙏 Credits

- Model & Architecture: [TrackNetV3 by qaz812345](https://github.com/qaz812345/TrackNetV3)
- Notebook & Visualization Pipeline: Adapted for both Colab and local environments

---

## 📄 License

This project is for **educational and research purposes only**.  
Please refer to the [TrackNetV3 license](https://github.com/qaz812345/TrackNetV3/blob/main/LICENSE) for model and code usage terms.
