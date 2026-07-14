import sys
import tkinter as tk
from tkinter import ttk
import pyautogui
import ctypes
import os
import subprocess

# WinAPI constants for virtual key codes
VK_F7 = 0x76  # Pause/Resume tracking
VK_F8 = 0x77  # Capture coordinate and copy

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, bg, fg, hover_bg, radius=8, font=("Segoe UI Semibold", 8, "bold"), command=None, height=24):
        self.parent_bg = parent["bg"]
        super().__init__(parent, bg=self.parent_bg, bd=0, highlightthickness=0, cursor="hand2", height=height)
        self.text = text
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.radius = radius
        self.font = font
        self.command = command
        
        # Bind events
        self.bind("<Configure>", self.draw)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def draw(self, event=None, color=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius
        c = color if color else self.bg
        
        # Draw rounded rectangle
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=c, outline=c)
        self.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=c, outline=c)
        self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=c, outline=c)
        self.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=c, outline=c)
        
        self.create_rectangle(r, 0, w-r, h, fill=c, outline=c)
        self.create_rectangle(0, r, w, h-r, fill=c, outline=c)
        
        # Draw text
        self.create_text(w//2, h//2, text=self.text, fill=self.fg, font=self.font, justify="center")

    def on_press(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.draw(color=self.hover_bg)

    def on_leave(self, event):
        self.draw(color=self.bg)

    def update_text_and_color(self, text, bg, fg, hover_bg, command):
        self.text = text
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.command = command
        self.draw()

class CursorHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("HUD")
        
        # Make the window borderless and always-on-top
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        # Collapsed footprint dimensions
        self.width = 200
        self.height = 115
        
        # Position near top-right of screen
        screen_w = self.root.winfo_screenwidth()
        start_x = max(10, screen_w - self.width - 20)
        self.root.geometry(f"{self.width}x{self.height}+{start_x}+50")
        
        # State variables
        self.tracking_paused = False
        self.expanded = False
        self.last_x, self.last_y = 0, 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.car_hunt_process = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(script_dir, "asphalt_automation.log")
        self.last_tell = 0
        
        # Colors (Catppuccin Mocha theme)
        self.bg_color = "#1e1e2e"
        self.header_bg = "#181825"
        self.accent_color = "#a6e3a1"  # Mint Green
        self.accent_warning = "#f38ba8"  # Pink/Red
        self.text_color = "#cdd6f4"
        self.muted_text = "#a6adc8"
        self.list_bg = "#11111b"
        
        # Flush initial key states for GetAsyncKeyState
        for vk in [VK_F7, VK_F8]:
            ctypes.windll.user32.GetAsyncKeyState(vk)
            
        self.key_states = {VK_F7: False, VK_F8: False}
        
        self.setup_ui()
        self.root.update()
        self.apply_rounded_corners()
        self.update_loop()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)
        
        # Configure custom scrollbar style using ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Vertical.TScrollbar",
            troughcolor="#11111b",       # Dark list background
            background="#313244",        # Scrollbar thumb matches border
            bordercolor="#11111b",
            arrowcolor="#a6adc8",        # Arrow matches muted text
            relief="flat",
            borderwidth=0,
            arrowsize=10
        )
        self.style.map(
            "Vertical.TScrollbar",
            background=[("active", "#45475a"), ("pressed", "#585b70")]
        )
        
        # Border frame to give it a sleek outline
        self.border_frame = tk.Frame(self.root, bg="#313244", bd=1)
        self.border_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Inner content frame
        self.content_frame = tk.Frame(self.border_frame, bg=self.bg_color)
        self.content_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Custom header/title bar
        self.header = tk.Frame(self.content_frame, bg=self.header_bg, height=22)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)
        
        self.header_label = tk.Label(
            self.header, 
            text="🎯 Cursor HUD", 
            font=("Segoe UI Semibold", 8, "bold"), 
            bg=self.header_bg, 
            fg=self.accent_color
        )
        self.header_label.pack(side="left", padx=6)
        
        # Close button
        self.close_btn = tk.Button(
            self.header, 
            text="✕", 
            font=("Segoe UI", 8, "bold"), 
            bg=self.header_bg, 
            fg=self.text_color, 
            bd=0, 
            activebackground="#f38ba8", 
            activeforeground="#11111b",
            command=self.root.destroy, 
            cursor="hand2"
        )
        self.close_btn.pack(side="right", fill="y", padx=2)
        self.close_btn.bind("<Enter>", lambda e: self.close_btn.config(bg="#f38ba8", fg="#11111b"))
        self.close_btn.bind("<Leave>", lambda e: self.close_btn.config(bg=self.header_bg, fg=self.text_color))
        
        # Expand toggle button
        self.expand_btn = tk.Button(
            self.header, 
            text="▼", 
            font=("Segoe UI", 8, "bold"), 
            bg=self.header_bg, 
            fg=self.accent_color, 
            bd=0, 
            activebackground="#313244", 
            activeforeground=self.accent_color,
            command=self.toggle_expand, 
            cursor="hand2"
        )
        self.expand_btn.pack(side="right", fill="y", padx=2)
        self.expand_btn.bind("<Enter>", lambda e: self.expand_btn.config(bg="#313244"))
        self.expand_btn.bind("<Leave>", lambda e: self.expand_btn.config(bg=self.header_bg))
        
        # Bind header events for window dragging
        self.header.bind("<Button-1>", self.start_drag)
        self.header.bind("<B1-Motion>", self.drag)
        self.header_label.bind("<Button-1>", self.start_drag)
        self.header_label.bind("<B1-Motion>", self.drag)
        
        # Coordinates Frame
        self.coords_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.coords_frame.pack(fill="x", pady=(5, 4), padx=10)
        
        # Panel X
        self.panel_x = tk.Frame(self.coords_frame, bg="#252538", bd=0)
        self.panel_x.pack(side="left", fill="both", expand=True, padx=(0, 3))
        
        self.lbl_x_tag = tk.Label(self.panel_x, text="X", font=("Segoe UI Semibold", 8, "bold"), bg="#252538", fg="#89b4fa")
        self.lbl_x_tag.pack(side="left", padx=(6, 2), pady=3)
        
        self.lbl_x = tk.Label(self.panel_x, text="0", font=("Consolas", 10, "bold"), bg="#252538", fg=self.text_color)
        self.lbl_x.pack(side="right", padx=(2, 6), pady=3, expand=True, anchor="w")
        
        # Panel Y
        self.panel_y = tk.Frame(self.coords_frame, bg="#252538", bd=0)
        self.panel_y.pack(side="right", fill="both", expand=True, padx=(3, 0))
        
        self.lbl_y_tag = tk.Label(self.panel_y, text="Y", font=("Segoe UI Semibold", 8, "bold"), bg="#252538", fg="#f5c2e7")
        self.lbl_y_tag.pack(side="left", padx=(6, 2), pady=3)
        
        self.lbl_y = tk.Label(self.panel_y, text="0", font=("Consolas", 10, "bold"), bg="#252538", fg=self.text_color)
        self.lbl_y.pack(side="right", padx=(2, 6), pady=3, expand=True, anchor="w")
        
        # Start Car Hunt Button (Custom Rounded Canvas Button)
        self.btn_car_hunt = RoundedButton(
            self.content_frame,
            text="🚗 Start Car Hunt",
            bg="#1e2e24",
            fg=self.accent_color,
            hover_bg="#273d30",
            radius=8,
            font=("Segoe UI Semibold", 8, "bold"),
            command=self.start_car_hunt,
            height=24
        )
        self.btn_car_hunt.pack(fill="x", padx=10, pady=(2, 2))
        self.set_button_style("start")
        
        # Help Hint Text
        self.lbl_help = tk.Label(
            self.content_frame, 
            text="F8: Copy (X, Y)  |  F7: Freeze", 
            font=("Segoe UI Semibold", 7, "bold"), 
            bg=self.bg_color, 
            fg=self.muted_text
        )
        self.lbl_help.pack(fill="x", side="bottom", pady=(0, 4))
        
        # Log frame (hidden by default, packed when expanded)
        self.log_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # Scrollbar for logs
        self.log_scrollbar = ttk.Scrollbar(self.log_frame, style="Vertical.TScrollbar")
        self.log_scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        self.log_text = tk.Text(
            self.log_frame, 
            bg=self.list_bg, 
            fg=self.text_color, 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#313244",
            font=("Consolas", 8),
            state="disabled",
            wrap="word",
            yscrollcommand=self.log_scrollbar.set
        )
        self.log_text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        self.log_scrollbar.config(command=self.log_text.yview)

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        x = self.root.winfo_x() - self.drag_start_x + event.x
        y = self.root.winfo_y() - self.drag_start_y + event.y
        self.root.geometry(f"+{x}+{y}")

    def apply_rounded_corners(self):
        try:
            # Get the true root top-level Win32 window HWND (GA_ROOT = 2)
            # This fixes the bug where winfo_id() (Tk client window) doesn't round the top-left.
            hwnd = ctypes.windll.user32.GetAncestor(self.root.winfo_id(), 2)
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            # Create a rounded rectangle region with 12px corner radius
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, w, h, 12, 12)
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception as e:
            print(f"Error applying rounded corners: {e}")

    def toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.expand_btn.config(text="▲")
            # Resize window geometry to show logs
            self.root.geometry("340x280")
            self.root.update()
            self.apply_rounded_corners()
            self.log_frame.pack(fill="both", expand=True)
            
            # Reset seek pointer and clear log text
            self.last_tell = 0
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", tk.END)
            self.log_text.config(state="disabled")
            
            # Start polling logs
            self.update_logs()
        else:
            self.expand_btn.config(text="▼")
            self.log_frame.pack_forget()
            # Collapse back to footprint size
            self.root.geometry(f"{self.width}x{self.height}")
            self.root.update()
            self.apply_rounded_corners()

    def update_logs(self):
        if not self.expanded:
            return
            
        if os.path.exists(self.log_file):
            try:
                file_size = os.path.getsize(self.log_file)
                if file_size < self.last_tell:
                    # Log file was cleaned/truncated
                    self.last_tell = 0
                    self.log_text.config(state="normal")
                    self.log_text.delete("1.0", tk.END)
                    self.log_text.config(state="disabled")
                    
                with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(self.last_tell)
                    new_data = f.read()
                    self.last_tell = f.tell()
                    
                    if new_data:
                        self.log_text.config(state="normal")
                        self.log_text.insert(tk.END, new_data)
                        
                        # Keep text size bounded to prevent memory build-up
                        content_len = len(self.log_text.get("1.0", tk.END))
                        if content_len > 10000:
                            self.log_text.delete("1.0", "50.0")
                            
                        self.log_text.see(tk.END)
                        self.log_text.config(state="disabled")
            except Exception as e:
                print(f"Error reading log file: {e}")
                
        # Poll the log file every 200ms
        if self.expanded:
            self.root.after(200, self.update_logs)

    def update_loop(self):
        if not self.tracking_paused:
            x, y = pyautogui.position()
            self.last_x, self.last_y = x, y
            self.lbl_x.config(text=f"{x}")
            self.lbl_y.config(text=f"{y}")
        
        self.check_hotkeys()
        self.update_car_hunt_button_status()
        self.root.after(50, self.update_loop)

    def check_hotkeys(self):
        for vk_code in [VK_F7, VK_F8]:
            is_down = bool(ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000)
            was_down = self.key_states.get(vk_code, False)
            self.key_states[vk_code] = is_down
            
            if is_down and not was_down:
                self.handle_hotkey(vk_code)

    def handle_hotkey(self, vk_code):
        if vk_code == VK_F7:
            self.toggle_freeze()
        elif vk_code == VK_F8:
            self.capture_coordinate()

    def toggle_freeze(self):
        self.tracking_paused = not self.tracking_paused
        if self.tracking_paused:
            self.header_label.config(text="🎯 HUD (PAUSED)", fg=self.accent_warning)
            self.lbl_help.config(text="F7 to Resume", fg=self.accent_warning)
        else:
            self.header_label.config(text="🎯 Cursor HUD", fg=self.accent_color)
            self.lbl_help.config(text="F8: Copy (X, Y)  |  F7: Freeze", fg=self.muted_text)

    def capture_coordinate(self):
        x, y = self.last_x, self.last_y
        formatted = f"{x}, {y}"
        
        original_fg = self.text_color
        self.lbl_x.config(fg=self.accent_color)
        self.lbl_y.config(fg=self.accent_color)
        self.root.after(150, lambda: self.lbl_x.config(fg=original_fg))
        self.root.after(150, lambda: self.lbl_y.config(fg=original_fg))
        
        self.copy_to_clipboard(formatted)
        
        self.lbl_help.config(text=f"Copied: ({formatted})", fg=self.accent_color)
        self.root.after(1500, self.revert_help_text)

    def revert_help_text(self):
        if self.tracking_paused:
            self.lbl_help.config(text="F7 to Resume", fg=self.accent_warning)
        else:
            self.lbl_help.config(text="F8: Copy (X, Y)  |  F7: Freeze", fg=self.muted_text)

    def set_button_style(self, state):
        if state == "start":
            bg = "#1e2e24" # Very dark green
            fg = "#a6e3a1" # Pastel mint green
            hover_bg = "#273d30"
            text = "🚗 Start Car Hunt"
            command = self.start_car_hunt
        else: # "stop"
            bg = "#3d1e25" # Very dark red
            fg = "#f38ba8" # Pastel red/pink
            hover_bg = "#522732"
            text = "🛑 Stop Car Hunt"
            command = self.stop_car_hunt

        self.btn_car_hunt.update_text_and_color(text, bg, fg, hover_bg, command)

    def start_car_hunt(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "carHunt.py")
        try:
            # Run in the background (no console window popup)
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.car_hunt_process = subprocess.Popen(
                [sys.executable, script_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo
            )
            # Instantly update button state to Stop
            self.set_button_style("stop")
            print("Car Hunt script started in background.")
        except Exception as e:
            print(f"Error starting Car Hunt script: {e}")

    def stop_car_hunt(self):
        if self.car_hunt_process is not None:
            print("Terminating Car Hunt script...")
            self.car_hunt_process.terminate()
            try:
                self.car_hunt_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.car_hunt_process.kill()
            self.car_hunt_process = None
            
            # Instantly update button state back to Start
            self.set_button_style("start")
            print("Car Hunt script terminated.")

    def update_car_hunt_button_status(self):
        # Only handle automatic status changes when the process terminates on its own
        if self.car_hunt_process is not None and self.car_hunt_process.poll() is not None:
            self.car_hunt_process = None
            self.set_button_style("start")

    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
        except Exception as e:
            print(f"Error copying to clipboard: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CursorHUD(root)
    root.mainloop()
