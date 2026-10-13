'd love your help testing this! Especially if you have:

A different MPC model (MPC One, MPC X, MPC Key 61, Force)

A large or unusual drum library

Non-English filenames

macOS or Linux (to help port the audio playback)

If it works for you, please ⭐ star the repo — it helps other MPC users find it.


# Contributing to MPC Preview Builder Pro

First of all — thank you! 🎉 This project exists to help the MPC community, and every bug report, feature idea, or pull request makes it better for everyone.

## 🐛 Reporting a Bug

Before opening an issue, please:

1. **Search existing issues** — someone may have already reported it
2. **Try the latest version** — pull from `main` before testing

When you open an issue, include:

- **Your OS** (Windows 10, Windows 11, etc.)
- **Your MPC model** (MPC Live, MPC One, MPC X, Force, etc.)
- **Python version** (`python --version`)
- **What you did** — the exact folder structure / files involved if possible
- **What you expected**
- **What actually happened** — copy the activity log text
- **Screenshot** if relevant (especially for UI issues)

Please **redact personal file paths** if you don't want them public.

## 💡 Suggesting a Feature

Open an issue with the `enhancement` label. Describe:

- **The problem** you're trying to solve
- **Your proposed solution**
- **Alternatives** you've considered

## 🔧 Submitting a Pull Request

1. Fork the repo and create a branch:
   ```bash
   git checkout -b feature/your-feature-name


   Make your changes — keep them focused, one feature per PR

Test on your own MPC library if possible

Update the README if you've added user-facing behaviour

Commit with a clear message:

text
feat: add drag-and-drop folder support
fix: correct .xpm.wav extension on Force firmware
Push and open a PR against main

🎨 Code Style
Follow PEP 8 where reasonable

Keep dependencies at zero — this is a core design goal, so users can just run it

Prefer clarity over cleverness

Add comments for anything non-obvious

🧪 Testing Checklist
Since there's no automated test suite yet, please manually verify:

□ App launches on a clean machine (no config file)
□ Browsing to a folder works
□ Scanning a folder with exact-match WAVs works
□ Scanning a folder with NO matches shows a friendly message
□ The resolver dialog opens when fuzzy matches are needed
□ Audio preview plays and stops
□ "Stop Scanning" actually aborts mid-run
□ Re-running on the same folder skips everything (fast second pass)
🗺️ Roadmap / Wanted Help
□ macOS / Linux support (replace winsound with pygame.mixer or simpleaudio)
□ Drag-and-drop folder (via tkinterdnd2)
□ Recursive scanning with a depth limit
□ Batch resolver — resolve many mismatches at once instead of one-by-one
□ Preview file validation — warn if the copied WAV is silent / corrupt
□ Localisation — extract UI strings into a translations file
📜 Code of Conduct
Be kind. This is a hobby project for a niche community. No gatekeeping, no "just Google it", no drama. If you're rude, your contributions will be ignored.

text

---


