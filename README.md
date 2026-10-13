# 🎛️ MPC Preview Builder Pro

> Automatically generate `.xpm.wav` preview files for your Akai MPC Live / Force drum programs — from any messy folder full of `.xpm` and `.wav` files.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078D4.svg)]()
[![Open Source](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🤔 The Problem

If you own an **Akai MPC Live**, **MPC One**, **MPC X**, or **Force**, you know the pain:

When you load a drum program (`.xpm`), the browser shows a **blank preview tile** unless a matching audio preview file exists next to it. Akai expects a file literally named:


Creating those by hand for a 300-file drum library is brutal. Worse, most third-party kits have typos, inconsistent naming, or WAVs that almost — but not quite — match the `.xpm` name.

**This tool solves that in one click.**

---

## ✨ What It Does

Point it at a drum program folder. It will:

1. **Scan** every `.xpm` file in the folder
2. **Look** for a matching `.wav` with the same name (e.g. `Amen Break.xpm` → `Amen Break.wav`)
3. **Fallback** to a substring match (e.g. `Amen Break.xpm` → `Amen Break (clean).wav`)
4. **Fuzzy-match** as a last resort using Python's `difflib` similarity scorer
5. **Ask you** — with audio playback — which candidate is correct when it can't be sure
6. **Copy** the chosen WAV into a `[Previews]` subfolder as `ProgramName.xpm.wav`
7. **Skip** anything that already has a preview, so re-runs are instant

The result: your MPC browser shows beautiful preview waveforms for every kit, forever.

---

## 🚀 Quick Start

### Requirements

- **Windows 10 or 11** (uses `winsound` for audio preview)
- **Python 3.8 or newer** — [download here](https://www.python.org/downloads/)
  - ⚠️ During install, tick **"Add Python to PATH"**

### Installation

```bash
# 1. Clone this repository
git clone https://github.com/YOUR-USERNAME/mpc-preview-builder.git
cd mpc-preview-builder

# 2. (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Run it — no external dependencies needed!
python mpc_preview_builder.py
