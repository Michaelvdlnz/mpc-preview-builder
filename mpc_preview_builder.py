import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
import difflib
import winsound

CONFIG_FILE = Path(__file__).parent / "mpc_config.txt"

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN TOKENS  (edit these to re-theme the entire app in one place)
# ─────────────────────────────────────────────────────────────────────────────
BG          = "#16181D"   # app background
SURFACE     = "#1E2128"   # cards / panels
SURFACE_2   = "#262A33"   # inputs, hovered rows
BORDER      = "#2E333D"   # subtle 1px borders
TEXT        = "#E6E8EC"   # primary text
TEXT_MUTED  = "#8B93A1"   # secondary text
ACCENT      = "#4C8DFF"   # primary action (blue)
ACCENT_HOV  = "#3D7AE6"
DANGER      = "#E5484D"   # destructive / stop
DANGER_HOV  = "#C93B40"
SUCCESS     = "#4ADE80"
WARNING     = "#F5A524"
LOG_BG      = "#11131A"
LOG_TEXT    = "#C8CDD6"

FONT_UI     = ("Segoe UI", 10)
FONT_UI_B   = ("Segoe UI", 10, "bold")
FONT_TITLE  = ("Segoe UI Semibold", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


# ─────────────────────────────────────────────────────────────────────────────
#  ROUNDED BUTTON  (canvas-drawn, since tkinter has no native rounded buttons)
# ─────────────────────────────────────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, *, width=200, height=38,
                 bg=ACCENT, hover=ACCENT_HOV, fg="#FFFFFF",
                 font=FONT_UI_B, radius=8, icon=""):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"], highlightthickness=0, bd=0)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover
        self.fg = fg
        self.font = font
        self.radius = radius
        self._enabled = True
        self._label = f"{icon}  {text}".strip() if icon else text

        self._draw(self.bg_color)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self, fill):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        r = self.radius
        # rounded rectangle
        self.create_oval(0, 0, r*2, r*2, fill=fill, outline=fill)
        self.create_oval(w-r*2, 0, w, r*2, fill=fill, outline=fill)
        self.create_oval(0, h-r*2, r*2, h, fill=fill, outline=fill)
        self.create_oval(w-r*2, h-r*2, w, h, fill=fill, outline=fill)
        self.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill)
        self.create_rectangle(0, r, w, h-r, fill=fill, outline=fill)
        self.create_text(w/2, h/2, text=self._label, fill=self.fg, font=self.font)

    def _on_enter(self, _):
        if self._enabled:
            self._draw(self.hover_color)

    def _on_leave(self, _):
        if self._enabled:
            self._draw(self.bg_color)

    def _on_click(self, _):
        if self._enabled and self.command:
            self.command()

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self._draw(self.bg_color)
            self.configure(cursor="hand2")
        else:
            self._draw("#2A2E36")
            self.itemconfigure("all", fill="#5A6170")
            self.configure(cursor="")

    def set_text(self, text):
        self._label = text
        self._draw(self.bg_color if self._enabled else "#2A2E36")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
class MPCPreviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MPC Preview Builder Pro")
        self.root.geometry("720x600")
        self.root.minsize(640, 520)
        self.root.configure(bg=BG)

        self.cancel_requested = False

        # ── Header ──────────────────────────────────────────────────────────
        header = tk.Frame(root, bg=BG, height=70)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=BG)
        title_box.pack(side="left", fill="y")

        tk.Label(title_box, text="MPC Preview Builder",
                 bg=BG, fg=TEXT, font=("Segoe UI Semibold", 16)).pack(anchor="w")
        tk.Label(title_box, text="Generate .xpm.wav previews from your sample library",
                 bg=BG, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w", pady=(2, 0))

        # status pill
        self.status_pill = tk.Label(header, text="●  READY", bg=SURFACE, fg=SUCCESS,
                                    font=("Segoe UI", 9, "bold"), padx=12, pady=6)
        self.status_pill.pack(side="right")

        # ── Folder selector card ────────────────────────────────────────────
        pick_card = tk.Frame(root, bg=SURFACE, highlightthickness=1,
                             highlightbackground=BORDER)
        pick_card.pack(fill="x", padx=24, pady=(18, 0))

        inner = tk.Frame(pick_card, bg=SURFACE)
        inner.pack(fill="x", padx=16, pady=14)

        tk.Label(inner, text="TARGET FOLDER", bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")

        row = tk.Frame(inner, bg=SURFACE)
        row.pack(fill="x", pady=(6, 0))

        entry_wrap = tk.Frame(row, bg=SURFACE_2, highlightthickness=1,
                              highlightbackground=BORDER)
        entry_wrap.pack(side="left", fill="x", expand=True)

        self.path_entry = tk.Entry(entry_wrap, bg=SURFACE_2, fg=TEXT,
                                   insertbackground=ACCENT, relief="flat",
                                   font=FONT_UI, bd=0)
        self.path_entry.pack(fill="x", padx=12, pady=9)

        browse_btn = RoundedButton(row, "Browse", icon="📁",
                                   command=self.browse_folder,
                                   width=120, height=38,
                                   bg=SURFACE_2, hover="#333844",
                                   fg=TEXT, font=FONT_UI)
        browse_btn.pack(side="left", padx=(10, 0))

        # ── Primary action ──────────────────────────────────────────────────
        self.scan_btn = RoundedButton(root, "Scan & Build Previews", icon="▶",
                                      command=self.process_folder,
                                      width=672, height=48,
                                      bg=ACCENT, hover=ACCENT_HOV,
                                      fg="#FFFFFF", font=FONT_UI_B)
        self.scan_btn.pack(padx=24, pady=(14, 0))
        self.scan_btn.set_enabled(False)

        # ── Log card ────────────────────────────────────────────────────────
        log_card = tk.Frame(root, bg=SURFACE, highlightthickness=1,
                            highlightbackground=BORDER)
        log_card.pack(fill="both", expand=True, padx=24, pady=(18, 24))

        log_header = tk.Frame(log_card, bg=SURFACE)
        log_header.pack(fill="x", padx=16, pady=(12, 8))

        tk.Label(log_header, text="ACTIVITY LOG", bg=SURFACE, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left")

        clear_btn = tk.Label(log_header, text="Clear", bg=SURFACE,
                             fg=TEXT_MUTED, font=FONT_SMALL, cursor="hand2")
        clear_btn.pack(side="right")
        clear_btn.bind("<Button-1>", lambda e: self.clear_log())

        sep = tk.Frame(log_card, bg=BORDER, height=1)
        sep.pack(fill="x")

        log_wrap = tk.Frame(log_card, bg=LOG_BG)
        log_wrap.pack(fill="both", expand=True, padx=1, pady=(0, 1))

        self.log_text = tk.Text(log_wrap, wrap="word", font=FONT_MONO,
                                state="disabled", bg=LOG_BG, fg=LOG_TEXT,
                                insertbackground=ACCENT, relief="flat",
                                bd=0, padx=14, pady=12)
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_wrap, command=self.log_text.yview,
                                 bg=LOG_BG, troughcolor=LOG_BG,
                                 activebackground=SURFACE_2, relief="flat",
                                 bd=0, width=10)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # colour tags for log lines
        self.log_text.tag_configure("info",    foreground=LOG_TEXT)
        self.log_text.tag_configure("muted",   foreground=TEXT_MUTED)
        self.log_text.tag_configure("success", foreground=SUCCESS)
        self.log_text.tag_configure("warning", foreground=WARNING)
        self.log_text.tag_configure("error",   foreground=DANGER)
        self.log_text.tag_configure("accent",  foreground=ACCENT)
        self.log_text.tag_configure("head",    foreground=TEXT, font=("Consolas", 10, "bold"))

        # ── Boot ────────────────────────────────────────────────────────────
        self.log("MPC Preview Builder ready.", tag="head")
        self.load_saved_folder()

    # ──────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────────────────────────────────
    def _set_status(self, text, color):
        self.status_pill.configure(text=f"●  {text}", fg=color)

    def log(self, message, tag="info"):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update()

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def load_saved_folder(self):
        if CONFIG_FILE.exists():
            try:
                saved = CONFIG_FILE.read_text(encoding="utf-8").strip()
                if os.path.exists(saved):
                    self.path_entry.insert(0, saved)
                    self.scan_btn.set_enabled(True)
                    self.log(f"Restored last folder:  {saved}", tag="muted")
                    self.log("Press  ▶ Scan & Build Previews  to begin.", tag="muted")
                    return
            except Exception:
                pass
        self.log("Select a folder to get started.", tag="muted")

    def save_folder_history(self, folder_path):
        try:
            CONFIG_FILE.write_text(folder_path, encoding="utf-8")
        except Exception:
            pass

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if not selected:
            return
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, selected)
        self.scan_btn.set_enabled(True)
        self.save_folder_history(selected)

        self.clear_log()
        self.log(f"Linked folder:  {selected}", tag="accent")
        self.log("Ready.  Press  ▶ Scan & Build Previews  to begin.", tag="muted")

    # ──────────────────────────────────────────────────────────────────────
    #  MATCH DIALOG  (redesigned)
    # ──────────────────────────────────────────────────────────────────────
    def ask_user_to_match(self, program_name, wav_options, folder_path):
        dialog = tk.Toplevel(self.root)
        dialog.title("Resolve Mismatch")
        dialog.geometry("560x460")
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # ── header
        head = tk.Frame(dialog, bg=BG)
        head.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(head, text="Resolve File Mismatch", bg=BG, fg=TEXT,
                 font=("Segoe UI Semibold", 14)).pack(anchor="w")
        tk.Label(head,
                 text=f"No exact match found for  '{program_name}.xpm'.\nPick the correct audio source below.",
                 bg=BG, fg=TEXT_MUTED, font=FONT_SMALL,
                 justify="left").pack(anchor="w", pady=(4, 0))

        # ── list card
        list_card = tk.Frame(dialog, bg=SURFACE, highlightthickness=1,
                             highlightbackground=BORDER)
        list_card.pack(fill="both", expand=True, padx=24, pady=(16, 0))

        list_wrap = tk.Frame(list_card, bg=SURFACE)
        list_wrap.pack(fill="both", expand=True, padx=1, pady=1)

        listbox = tk.Listbox(list_wrap, font=FONT_UI, bg=SURFACE, fg=TEXT,
                             selectbackground=ACCENT, selectforeground="#FFFFFF",
                             relief="flat", bd=0, highlightthickness=0,
                             activestyle="none", selectborderwidth=0)
        listbox.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        sb = tk.Scrollbar(list_wrap, command=listbox.yview, bg=SURFACE,
                          troughcolor=SURFACE, relief="flat", bd=0, width=10)
        sb.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=sb.set)

        for i, opt in enumerate(wav_options):
            listbox.insert(tk.END, f"  {opt}")
        listbox.select_set(0)

        # ── audio row
        audio_row = tk.Frame(dialog, bg=BG)
        audio_row.pack(fill="x", padx=24, pady=(14, 0))

        def play_selected_audio():
            sel = listbox.curselection()
            if sel:
                chosen = wav_options[sel[0]]
                full = os.path.join(folder_path, chosen)
                try:
                    winsound.PlaySound(full, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception:
                    messagebox.showerror("Audio Error",
                                         "Playback error. Confirm sound driver format settings.")

        RoundedButton(audio_row, "Play Preview", icon="▶",
                      command=play_selected_audio,
                      width=140, height=34,
                      bg=SURFACE_2, hover="#333844",
                      fg=TEXT, font=FONT_UI).pack(side="left")

        RoundedButton(audio_row, "Stop", icon="■",
                      command=lambda: winsound.PlaySound(None, winsound.SND_PURGE),
                      width=90, height=34,
                      bg=SURFACE_2, hover="#333844",
                      fg=TEXT, font=FONT_UI).pack(side="left", padx=(8, 0))

        # ── action row
        selected_wav = [None]

        def close_dialog():
            winsound.PlaySound(None, winsound.SND_PURGE)
            dialog.destroy()

        def on_confirm():
            sel = listbox.curselection()
            if sel:
                selected_wav[0] = wav_options[sel[0]]
            close_dialog()

        def on_skip():
            selected_wav[0] = None
            close_dialog()

        def abort_entire_process():
            self.cancel_requested = True
            close_dialog()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        actions = tk.Frame(dialog, bg=BG)
        actions.pack(fill="x", padx=24, pady=(18, 22))

        RoundedButton(actions, "Stop Scanning", icon="✕",
                      command=abort_entire_process,
                      width=150, height=40,
                      bg=DANGER, hover=DANGER_HOV,
                      fg="#FFFFFF", font=FONT_UI).pack(side="left")

        RoundedButton(actions, "Confirm Match", icon="✓",
                      command=on_confirm,
                      width=170, height=40,
                      bg=ACCENT, hover=ACCENT_HOV,
                      fg="#FFFFFF", font=FONT_UI_B).pack(side="right")

        RoundedButton(actions, "Skip", icon="→",
                      command=on_skip,
                      width=100, height=40,
                      bg=SURFACE_2, hover="#333844",
                      fg=TEXT, font=FONT_UI).pack(side="right", padx=(0, 8))

        self.root.wait_window(dialog)
        return selected_wav[0]

    # ──────────────────────────────────────────────────────────────────────
    #  MAIN PIPELINE
    # ──────────────────────────────────────────────────────────────────────
    def process_folder(self):
        target_dir = self.path_entry.get().strip()
        path = Path(target_dir)

        if not path.exists():
            messagebox.showerror("Error", "The folder path does not exist.")
            return

        self.scan_btn.set_enabled(False)
        self._set_status("WORKING", ACCENT)
        self.cancel_requested = False
        self.log("─── Build started ───", tag="head")

        preview_dir = path / "[Previews]"
        preview_dir.mkdir(exist_ok=True)

        xpm_files = list(path.glob("*.xpm"))
        wav_files = list(path.glob("*.wav"))

        if not xpm_files:
            self.log("No .xpm files found in this folder.", tag="error")
            self._set_status("READY", SUCCESS)
            self.scan_btn.set_enabled(True)
            return

        wav_names = [f.name for f in wav_files]
        processed = 0
        skipped = 0

        for xpm in xpm_files:
            if self.cancel_requested:
                self.log("Process cancelled by user.", tag="warning")
                break

            program_name = xpm.stem
            preview_filename = f"{program_name}.xpm.wav"
            dest = preview_dir / preview_filename

            if dest.exists():
                self.log(f"· skip  {program_name}  (preview exists)", tag="muted")
                skipped += 1
                continue

            self.log(f"→ match  {xpm.name}", tag="accent")
            match_path = None
            exact = f"{program_name}.wav"

            if exact in wav_names:
                match_path = path / exact
                self.log(f"    exact match:  {exact}", tag="success")
            else:
                fuzzy = [w for w in wav_names if program_name.lower() in w.lower()]
                if fuzzy:
                    match_path = path / fuzzy[0]
                    self.log(f"    substring match:  {fuzzy[0]}", tag="success")
                else:
                    close = difflib.get_close_matches(exact, wav_names, n=4, cutoff=0.3)
                    if close:
                        self.log("    no direct match — opening resolver...", tag="warning")
                        chosen = self.ask_user_to_match(program_name, close, str(path))

                        if self.cancel_requested:
                            self.log("Process cancelled by user.", tag="warning")
                            break

                        if chosen:
                            match_path = path / chosen
                            self.log(f"    user-selected:  {chosen}", tag="success")
                        else:
                            self.log("    skipped by user.", tag="muted")
                            continue
                    else:
                        self.log("    no candidate files found — skipped.", tag="error")
                        continue

            if match_path:
                try:
                    if match_path.resolve() == dest.resolve():
                        self.log("    skipped (source == destination).", tag="warning")
                        continue
                    shutil.copy2(match_path, dest)
                    self.log(f"    written:  {preview_filename}", tag="success")
                    processed += 1
                except Exception as e:
                    self.log(f"    IO error:  {e}", tag="error")

        self.log("─── Build complete ───", tag="head")
        self.log(f"New previews:   {processed}", tag="success")
        self.log(f"Already present: {skipped}", tag="muted")

        self._set_status("READY", SUCCESS)
        self.scan_btn.set_enabled(True)

        messagebox.showinfo(
            "Build Complete",
            f"Preview build finished.\n\n"
            f"New previews generated:  {processed}\n"
            f"Already present:         {skipped}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MPCPreviewApp(root)
    root.mainloop()