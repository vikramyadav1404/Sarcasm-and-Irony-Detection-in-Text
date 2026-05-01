# Sarcasm & Irony Detector — Project Summary

This repository contains a fine-tuned DeBERTa-v3 model, a local Flask backend for inference, and a Chrome extension that lets you predict labels for highlighted text on any webpage. Below is a concise summary of the important files, how they fit together, and quick run instructions.

---

## Top-level overview
- `app.py` — Original Streamlit UI for uploading/pasting text and getting probabilities (kept for reference).
- `deberta_model/` — The pre-trained/fine-tuned model folder (tokenizer, config, `model.safetensors`, label mappings and checkpoints). This is the model used by the Flask backend.
- `flask_backend.py` — Local Flask API that loads the model and exposes endpoints:
  - `GET /` health check
  - `POST /predict` single-text prediction
  - `POST /batch-predict` batch predictions
- `chrome_extension/` — Chrome extension source; load this folder unpacked in `chrome://extensions/`.
- `start_backend.bat` / `start_backend.sh` — Platform scripts to install deps (if missing) and start the Flask backend.
- `verify_setup.py` — Small script to validate Python, required packages, model files, and extension files.
- `Untitled31.ipynb` — Training notebook used to fine-tune the DeBERTa model (kept as reference).
- `train.csv` / `test.csv` — Training and test datasets used for training/evaluation.

---

## `chrome_extension/` summary (what to load into Chrome)
- `manifest.json` — Extension configuration (permissions, content scripts, service worker, host permissions). Uses manifest v3.
- `background.js` — Service worker (creates context menu, sends selected text to `http://localhost:5000/predict`, saves results to `chrome.storage.local`, opens popup).
- `content.js` — Content script that detects selected text and can provide a small selection indicator.
- `popup.html`, `popup.js`, `popup.css` — Popup UI to display the last prediction (text, predicted label, confidence, score breakdown). `popup.js` reads `chrome.storage.local` for the last result and renders the UI.
- `icons/` — Small icons used by the extension.
- `README.md` — Extension-specific usage & troubleshooting (also duplicated by repository docs).

---

## `flask_backend.py` (backend inference)
- Loads `deberta_model` (tokenizer, model, `label2id.json`).
- Runs on `http://localhost:5000` by default and accepts JSON requests.
- Uses PyTorch; will move model to GPU if available. Uses softmax to compute per-label probabilities and returns:
  ```json
  {
    "predicted_label": "sarcasm",
    "confidence": 0.8743,
    "scores": {"sarcasm":0.8743, "irony":0.0892, "regular":0.0234, "figurative":0.0131}
  }
  ```
- Includes a `batch-predict` endpoint for arrays of texts (with safety limits).

---

## Model files (`deberta_model/`)
Key model artifacts in the folder used by the backend:
- `config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json`, `spm.model` — tokenizer & model configuration
- `model.safetensors` — model weights (largest file)
- `label2id.json` — mapping from label names to numeric ids used during training and inference.
- `checkpoint-*/` — training checkpoints (kept for reproducibility)

Note: The model was trained with max length 128 and outputs 4 classes: `figurative`, `irony`, `regular`, `sarcasm`.

---

## Training & notebook
- `Untitled31.ipynb` contains the training pipeline (data cleaning, tokenization, Trainer config, metrics and saving). It includes helper functions used during development such as `predict_text_deberta`.

---

## Documentation & helper files (where to read more)
A number of markdown documents were added to help you get started and to explain architecture and usage. Important ones:
- `VISUAL_QUICK_START.md` — 3-minute visual walkthrough.
- `QUICK_REFERENCE.md` — Copyable commands and quick tips.
- `SETUP_INSTRUCTIONS.md` — Step-by-step installation and troubleshooting.
- `EXTENSION_BUILD_COMPLETE.md` — What was built and why (architecture and decisions).
- `BEFORE_AND_AFTER.md` — Comparison between original Streamlit app and the new extension flow.
- `PROJECT_DIRECTORY.md` / `DOCUMENTATION_INDEX.md` / `MASTER_INDEX.md` — Indexes and navigation helpers.
- `GETTING_STARTED.md` / `READme_START_HERE.md` / `FINAL_DELIVERY_SUMMARY.md` — Checklists and final summary.

All docs live at the repository root and inside `chrome_extension/README.md` for extension-specific instructions.

---

## Quick run & debug steps
1. Install dependencies (recommended environment / system-specific):

```powershell
pip install flask flask-cors transformers torch
```

If you need GPU support, install the appropriate PyTorch wheel for your CUDA version.

2. Start backend server (from project root):

```powershell
python flask_backend.py
```

3. Load extension in Chrome:
- Open `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" and select the `chrome_extension/` folder

4. Use it:
- Select/highlight text on any webpage
- Right-click and choose "Predict with Detector"
- Popup will show the predicted label and probabilities

5. Troubleshooting:
- If you see "Failed to get prediction", ensure the backend is running at `http://localhost:5000`.
- Run `python verify_setup.py` to check the environment and model files.
- Check the browser console (F12) for extension errors and the terminal for Flask logs.

---

## Notes & caveats
- The model has moderate accuracy (~57.9% test accuracy). It works best for `regular` and `sarcasm` classes; `figurative` is known to be harder.
- All inference is local — no external data is sent out by the extension or backend.
- If you change the backend port, update `chrome_extension/manifest.json` (host permission) and any `http://localhost:5000` references inside `background.js`.

---

## Where to look next
- If you want to modify the extension UI: edit `chrome_extension/popup.html` / `.css` / `.js`.
- If you want to serve the API remotely: deploy `flask_backend.py` to a server and update the extension host permissions and URLs.
- If you want to retrain or improve the model: open `Untitled31.ipynb` and follow the Training cells.

---

## Contact & next steps
If you'd like, I can:
- Add automated unit tests for the backend endpoints,
- Add a small CI job or requirements file (`requirements.txt`),
- Bundle the extension into a zip for distribution,
- Or change the extension to call a remote server instead of localhost.

Tell me which next step you'd like and I'll implement it.
