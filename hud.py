import ctypes, os, re, subprocess, sys, tkinter as tk
from tkinter import ttk
import pyautogui


VK_F7, VK_F8 = 0x76, 0x77


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text="", bg="#303134", fg="#e8eaed", hover_bg="#3c4043",
                 radius=6, font=("Segoe UI Semibold", 8, "bold"), command=None,
                 width=100, height=26, **kw):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0,
                         width=width, height=height, cursor="hand2", **kw)
        self.text, self.normal_bg, self.current_bg, self.fg = text, bg, bg, fg
        self.hover_bg, self.radius, self.font, self.command = hover_bg, radius, font, command
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", lambda e: [setattr(self, "current_bg", self.hover_bg), self.draw()])
        self.bind("<Leave>", lambda e: [setattr(self, "current_bg", self.normal_bg), self.draw()])
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

    def draw(self, event=None):
        self.delete("all")
        w, h, r = self.winfo_width(), self.winfo_height(), self.radius
        if w <= 1 or h <= 1:
            return
        r = min(r, w // 2, h // 2)
        for (x, y, s) in [(0, 0, 90), (w-2*r, 0, 0), (0, h-2*r, 180), (w-2*r, h-2*r, 270)]:
            self.create_arc((x, y, x+2*r, y+2*r), start=s, extent=90,
                            fill=self.current_bg, outline=self.current_bg)
        self.create_rectangle((r, 0, w-r, h), fill=self.current_bg, outline=self.current_bg)
        self.create_rectangle((0, r, w, h-r), fill=self.current_bg, outline=self.current_bg)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg, font=self.font)

    def update_text_and_color(self, text, bg, fg, hover_bg, command=None):
        self.text, self.normal_bg, self.current_bg, self.fg, self.hover_bg = text, bg, bg, fg, hover_bg
        if command:
            self.command = command
        self.draw()


class CursorHUD:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 1.0)


        self.opacity = 1.0
        self.show_slider = False
        self.expanded = False
        self.manage_missout = False
        self.width = 450
        self.header_h = 24
        self.body_h = 70     # coord row + buttons row
        self.slider_h = 34   # extra height when settings open
        self.log_h = 230     # extra height when log expanded

        screen_w = self.root.winfo_screenwidth()
        self.sx = max(10, screen_w - self.width - 20)
        self.sy = 50
        self.root.geometry(f"{self.width}x{self.header_h + self.body_h}+{self.sx}+{self.sy}")

        self.last_x = self.last_y = 0
        self.tracking_paused = False
        self.key_states = {VK_F7: False, VK_F8: False}
        self.car_hunt_process = None
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asphalt_automation.log")
        self.last_tell = 0
        self.drag_start_x = self.drag_start_y = 0

        self.header_bg   = "#171717"
        self.bg_color    = "#202124"
        self.card_bg     = "#303134"
        self.text_color  = "#e8eaed"
        self.muted_text  = "#9aa0a6"
        self.accent      = "#8ab4f8"
        self.green       = "#81c995"
        self.red         = "#f28b82"
        self.amber       = "#fdd663"

        self.setup_ui()
        self.root.update_idletasks()
        self._apply_rounded()
        self.update_loop()



    def _apply_rounded(self):
        try:
            hwnd = self.root.winfo_id()
            rgn  = ctypes.windll.gdi32.CreateRoundRectRgn(
                0, 0, self.root.winfo_width(), self.root.winfo_height(), 8, 8)
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass


    def _current_height(self):
        h = self.header_h + self.body_h
        if self.show_slider: h += self.slider_h
        if self.expanded:    h += self.log_h
        return h

    def _resize(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.root.geometry(f"{self.width}x{self._current_height()}+{x}+{y}")
        self.root.update_idletasks()
        self._apply_rounded()


    # ── UI setup ───────────────────────────────────────────────────────────
    def setup_ui(self):
        self.root.configure(bg=self.header_bg)

        # Header row (always visible, draggable)
        self.header = tk.Frame(self.root, bg=self.header_bg, height=self.header_h)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.header_label = tk.Label(
            self.header, text="Cursor HUD",
            font=("Segoe UI Semibold", 8, "bold"), bg=self.header_bg, fg=self.accent)
        self.header_label.pack(side="left", padx=(6, 2))

        self.lbl_help = tk.Label(
            self.header, text="F8: Copy (X, Y)  |  F7: Freeze",
            font=("Segoe UI Semibold", 7, "bold"), bg=self.header_bg, fg=self.muted_text)
        self.lbl_help.pack(side="left", padx=(4, 0))

        for text, cmd, norm_fg, hov_bg, hov_fg in [
            ("✕",  self.on_close,            self.text_color, "#ea4335", "#202124"),
            ("▼",  self.toggle_expand,        self.accent,     "#3c4043", self.accent),
            ("⚙",  self.toggle_opacity_slider, self.amber,     "#3c4043", self.amber),
        ]:
            b = tk.Button(self.header, text=text, font=("Segoe UI", 8, "bold"),
                          bg=self.header_bg, fg=norm_fg, bd=0,
                          activebackground=hov_bg, activeforeground=hov_fg,
                          command=cmd, cursor="hand2")
            b.pack(side="right", fill="y", padx=2)
            b.bind("<Enter>", lambda e, btn=b, hb=hov_bg, hf=hov_fg: btn.config(bg=hb, fg=hf))
            b.bind("<Leave>", lambda e, btn=b, nb=self.header_bg, nf=norm_fg: btn.config(bg=nb, fg=nf))
            if text == "▼":  self.expand_btn = b
            if text == "⚙":  self.settings_btn = b

        for w in [self.header, self.header_label, self.lbl_help]:
            w.bind("<Button-1>", self._drag_start)
            w.bind("<B1-Motion>", self._drag_motion)



        # Body frame (always visible below header, expands with window height)
        self.body = tk.Frame(self.root, bg=self.bg_color)
        self.body.pack(fill="both", expand=True, side="top")


        # Scrollbar style
        sty = ttk.Style(); sty.theme_use("clam")
        sty.configure("Vertical.TScrollbar", troughcolor="#171717", background="#3c4043",
                      bordercolor="#171717", arrowcolor="#9aa0a6", relief="flat", borderwidth=0, arrowsize=10)
        sty.map("Vertical.TScrollbar", background=[("active","#5f6368"),("pressed","#80868b")])

        # Coord & Color row
        coord = tk.Frame(self.body, bg=self.bg_color)
        coord.pack(fill="x", padx=10, pady=(4, 2))
        for axis in ("X", "Y"):
            box = tk.Frame(coord, bg=self.card_bg)
            box.pack(side="left", fill="x", expand=True, padx=(0, 2))
            tk.Label(box, text=axis, font=("Segoe UI", 7, "bold"),
                     bg=self.card_bg, fg=self.muted_text).pack(side="left", padx=(5, 2), pady=2)
            lbl = tk.Label(box, text="0", font=("Consolas", 8, "bold"), bg=self.card_bg, fg=self.accent)
            lbl.pack(side="right", padx=(2, 5), pady=2)
            setattr(self, f"lbl_{axis.lower()}", lbl)

        # Color box
        c_box = tk.Frame(coord, bg=self.card_bg)
        c_box.pack(side="left", fill="x", expand=True, padx=(2, 0))
        tk.Label(c_box, text="COLOR", font=("Segoe UI", 7, "bold"),
                 bg=self.card_bg, fg=self.muted_text).pack(side="left", padx=(5, 2), pady=2)
        
        self.color_swatch = tk.Frame(c_box, bg="#FFFFFF", width=9, height=9)
        self.color_swatch.pack(side="left", padx=(2, 2), pady=2)
        self.color_swatch.pack_propagate(False)

        self.lbl_color = tk.Label(c_box, text="#FFFFFF", font=("Consolas", 8, "bold"), bg=self.card_bg, fg=self.text_color)
        self.lbl_color.pack(side="right", padx=(2, 5), pady=2)


        # Buttons row
        btn_row = tk.Frame(self.body, bg=self.bg_color)
        btn_row.pack(fill="x", padx=10, pady=(2, 2))

        self.btn_car_hunt = RoundedButton(
            btn_row, text="Start Hunt", bg="#1b382b", fg=self.green, hover_bg="#234938",
            radius=6, font=("Segoe UI Semibold",8,"bold"), command=self.start_car_hunt, width=1, height=24)
        self.btn_car_hunt.pack(side="left", fill="x", expand=True, padx=(0,2))

        self.btn_continue_hunt = RoundedButton(
            btn_row, text="Cont. Play", bg="#1b3538", fg="#78d9ec", hover_bg="#23454a",
            radius=6, font=("Segoe UI Semibold",8,"bold"), command=self.continue_car_hunt, width=1, height=24)
        self.btn_continue_hunt.pack(side="left", fill="x", expand=True, padx=(2,2))

        self.btn_missout = RoundedButton(
            btn_row, text="Missout: OFF", bg=self.card_bg, fg=self.muted_text, hover_bg="#3c4043",
            radius=6, font=("Segoe UI Semibold",8,"bold"), command=self.toggle_missout, width=1, height=24)
        self.btn_missout.pack(side="left", fill="x", expand=True, padx=(2,0))

        # Settings / opacity row (hidden by default)
        self.opacity_frame = tk.Frame(self.body, bg=self.bg_color)
        self.opacity_slider = tk.Scale(
            self.opacity_frame, from_=20, to=100, orient="horizontal", showvalue=False,
            length=240, bg=self.bg_color, troughcolor="#5f6368", activebackground=self.accent,
            highlightthickness=0, bd=0, sliderrelief="flat", sliderlength=14,
            cursor="hand2", command=self.on_opacity_change)
        self.opacity_slider.set(100)
        self.opacity_slider.pack(side="left", padx=(2,4))
        self.opacity_slider.bind("<Button-1>", self._slider_click)
        self.lbl_opacity = tk.Label(self.opacity_frame, text="100%",
                                    font=("Segoe UI Semibold",8,"bold"),
                                    bg=self.bg_color, fg=self.accent, width=4)
        self.lbl_opacity.pack(side="left", padx=(0,4))
        self.btn_refresh = tk.Button(
            self.opacity_frame, text="↻ Refresh", font=("Segoe UI Semibold",8,"bold"),
            bg=self.card_bg, fg=self.amber, activebackground="#3c4043",
            activeforeground=self.amber, bd=0, padx=8, pady=2, cursor="hand2",
            command=self.refresh_hud)
        self.btn_refresh.pack(side="left", padx=(4,0))
        self.btn_refresh.bind("<Enter>", lambda e: self.btn_refresh.config(bg="#3c4043"))
        self.btn_refresh.bind("<Leave>", lambda e: self.btn_refresh.config(bg=self.card_bg))

        # Log frame (hidden by default)
        self.log_frame = tk.Frame(self.body, bg=self.bg_color)
        self.log_sb = ttk.Scrollbar(self.log_frame, style="Vertical.TScrollbar")
        self.log_sb.pack(side="right", fill="y", pady=5, padx=(0,5))
        self.log_text = tk.Text(
            self.log_frame, bg="#171717", fg=self.text_color, bd=0,
            highlightthickness=1, highlightbackground="#3c4043",
            font=("Consolas",8), state="disabled", wrap="word",
            yscrollcommand=self.log_sb.set)
        self.log_text.pack(side="left", fill="both", expand=True, padx=(5,0), pady=5)
        self.log_sb.config(command=self.log_text.yview)

    # ── drag ───────────────────────────────────────────────────────────────
    def _drag_start(self, event):
        self._drag_offset_x = event.x_root - self.root.winfo_x()
        self._drag_offset_y = event.y_root - self.root.winfo_y()

    def _drag_motion(self, event):
        x = event.x_root - self._drag_offset_x
        y = event.y_root - self._drag_offset_y
        self.root.geometry(f"+{x}+{y}")
        self.root.update_idletasks()





    # ── expand / collapse log ─────────────────────────────────────────────
    def toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.expand_btn.config(text="▲")
            self.log_frame.pack(fill="both", expand=True, pady=(0,4), padx=5)
            self.last_tell = 0
            self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END); self.log_text.config(state="disabled")
            self.update_logs()
        else:
            self.expand_btn.config(text="▼")
            self.log_frame.pack_forget()
        self._resize()

    def update_logs(self):
        import re
        if not self.expanded:
            return

        if os.path.exists(self.log_file):
            try:
                if os.path.getsize(self.log_file) < self.last_tell:
                    self.last_tell = 0
                    self.log_text.config(state="normal"); self.log_text.delete("1.0", tk.END); self.log_text.config(state="disabled")
                with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(self.last_tell); new = f.read(); self.last_tell = f.tell()
                    if new:
                        clean_new = re.sub(r'[\x1b\033]\[[0-9;]*m', '', new)
                        self.log_text.config(state="normal"); self.log_text.insert(tk.END, clean_new)
                        if len(self.log_text.get("1.0", tk.END)) > 10000: self.log_text.delete("1.0", "50.0")
                        self.log_text.see(tk.END); self.log_text.config(state="disabled")

            except Exception as e:
                print(f"Log error: {e}")
        if self.expanded:
            self.root.after(200, self.update_logs)

    def get_pixel_color(self, x: int, y: int) -> tuple:
        try:
            hdc = ctypes.windll.user32.GetDC(0)
            rgb_int = ctypes.windll.gdi32.GetPixel(hdc, x, y)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            if rgb_int != -1:
                r = rgb_int & 0xFF
                g = (rgb_int >> 8) & 0xFF
                b = (rgb_int >> 16) & 0xFF
                return r, g, b
        except Exception: pass
        return 255, 255, 255

    # ── update loop ────────────────────────────────────────────────────────
    def update_loop(self):
        if not self.tracking_paused:
            x, y = pyautogui.position()
            self.last_x, self.last_y = x, y
            self.lbl_x.config(text=str(x))
            self.lbl_y.config(text=str(y))
            r, g, b = self.get_pixel_color(x, y)
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            self.lbl_color.config(text=hex_color)
            self.color_swatch.config(bg=hex_color)
        self.check_hotkeys()
        self.update_hunt_status()
        self.root.after(50, self.update_loop)

    def check_hotkeys(self):
        for vk in [VK_F7, VK_F8]:
            down = bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
            if down and not self.key_states.get(vk):
                self.toggle_freeze() if vk == VK_F7 else self.capture_coordinate()
            self.key_states[vk] = down

    # ── hotkey actions ─────────────────────────────────────────────────────
    def toggle_freeze(self):
        self.tracking_paused = not self.tracking_paused
        if self.tracking_paused:
            self.header_label.config(text="HUD (PAUSED)", fg=self.red)
            self.lbl_help.config(text="F7 to Resume", fg=self.red)
        else:
            self.header_label.config(text="Cursor HUD", fg=self.accent)
            self.lbl_help.config(text="F8: Copy (X, Y, Color)  |  F7: Freeze", fg=self.muted_text)

    def capture_coordinate(self):
        r, g, b = self.get_pixel_color(self.last_x, self.last_y)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        fmt = f"{self.last_x}, {self.last_y}, {hex_color}"
        self.lbl_x.config(fg=self.green); self.lbl_y.config(fg=self.green); self.lbl_color.config(fg=self.green)
        self.root.after(150, lambda: self.lbl_x.config(fg=self.accent))
        self.root.after(150, lambda: self.lbl_y.config(fg=self.accent))
        self.root.after(150, lambda: self.lbl_color.config(fg=self.text_color))
        self.copy_to_clipboard(fmt)
        self.lbl_help.config(text=f"Copied: ({fmt})", fg=self.green)
        self.root.after(1500, self._revert_help)


    def _revert_help(self):
        if self.tracking_paused:
            self.lbl_help.config(text="F7 to Resume", fg=self.red)
        else:
            self.lbl_help.config(text="F8: Copy (X, Y)  |  F7: Freeze", fg=self.muted_text)

    # ── opacity slider ─────────────────────────────────────────────────────
    def toggle_opacity_slider(self):
        self.show_slider = not self.show_slider
        if self.show_slider:
            self.settings_btn.config(fg=self.green)
            if self.expanded and self.log_frame.winfo_manager():
                self.opacity_frame.pack(fill="x", padx=10, pady=(2, 4), before=self.log_frame)
            else:
                self.opacity_frame.pack(fill="x", padx=10, pady=(2, 4))
        else:
            self.settings_btn.config(fg=self.amber)
            self.opacity_frame.pack_forget()
        self._resize()


    def _slider_click(self, event):
        w = self.opacity_slider.winfo_width()
        if w > 0:
            self.opacity_slider.set(int(max(20, min(100, 20 + (event.x / float(w)) * 80))))

    def on_opacity_change(self, val):
        pct = int(float(val))
        self.opacity = pct / 100.0
        self.root.wm_attributes("-alpha", self.opacity)
        self.lbl_opacity.config(text=f"{pct}%")

    # ── refresh ────────────────────────────────────────────────────────────
    def refresh_hud(self):
        """Clean process restart: terminates any background hunt task and re-executes hud.py."""
        try:
            self.stop_car_hunt()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        os.execv(sys.executable, [sys.executable] + sys.argv)


    # ── car hunt ───────────────────────────────────────────────────────────
    def set_hunt_style(self, state: str):
        if state == "start":
            self.btn_car_hunt.update_text_and_color("Start Hunt","#1b382b",self.green,"#234938",self.start_car_hunt)
            self.btn_continue_hunt.update_text_and_color("Cont. Play","#1b3538","#78d9ec","#23454a",self.continue_car_hunt)
        else:
            self.btn_car_hunt.update_text_and_color("Stop Hunt","#3c1e1e",self.red,"#522828",self.stop_car_hunt)
            self.btn_continue_hunt.update_text_and_color("Stop Hunt","#3c1e1e",self.red,"#522828",self.stop_car_hunt)

    def start_car_hunt(self, continue_mode=False):
        try:
            cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "carHunt.py")]
            if self.manage_missout: cmd.append("--manage-missout")
            if continue_mode: cmd.append("--continue-from-play2")
            si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.car_hunt_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW, startupinfo=si)
            self.set_hunt_style("stop")
        except Exception as e:
            print(f"Error starting Car Hunt: {e}")

    def continue_car_hunt(self): self.start_car_hunt(continue_mode=True)

    def stop_car_hunt(self):
        if self.car_hunt_process:
            self.car_hunt_process.terminate()
            try: self.car_hunt_process.wait(timeout=2)
            except subprocess.TimeoutExpired: self.car_hunt_process.kill()
            self.car_hunt_process = None
            self.set_hunt_style("start")

    def update_hunt_status(self):
        if self.car_hunt_process and self.car_hunt_process.poll() is not None:
            self.car_hunt_process = None; self.set_hunt_style("start")

    def toggle_missout(self):
        self.manage_missout = not self.manage_missout
        if self.manage_missout:
            self.btn_missout.update_text_and_color("Missout: ON","#3c2d1d",self.amber,"#4e3b26",self.toggle_missout)
        else:
            self.btn_missout.update_text_and_color("Missout: OFF",self.card_bg,self.muted_text,"#3c4043",self.toggle_missout)

    # ── misc ───────────────────────────────────────────────────────────────
    def copy_to_clipboard(self, text: str):
        try:
            self.root.clipboard_clear(); self.root.clipboard_append(text); self.root.update()
        except Exception as e:
            print(f"Clipboard error: {e}")

    def on_close(self):
        if self.car_hunt_process:
            try: self.car_hunt_process.terminate()
            except Exception: pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CursorHUD(root)
    root.mainloop()
