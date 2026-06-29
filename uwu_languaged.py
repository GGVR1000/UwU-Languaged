import tkinter as tk
from tkinter import messagebox
import keyboard
import os
import ctypes
import threading
from PIL import Image
import pystray
import sys

# Native Windows API Constants for taskbar control
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020

class UwuLanguagedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ UWU Languaged ✨")
        
        try:
            myappid = 'mycompany.uwulanguaged.app.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        def get_resource_path(relative_path):
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)

        self.icon_ico = get_resource_path("app_icon.ico")
        self.icon_png = get_resource_path("app_icon.png")
        self.tray_icon = None
        
        # Keep root completely hidden to avoid ghost artifacts
        self.root.withdraw()
        
        # Create custom frameless window frame
        self.app = tk.Toplevel(self.root)
        self.app.title("✨ UWU Languaged ✨")
        self.app.overrideredirect(True)
        
        if os.path.exists(self.icon_ico):
            self.app.iconbitmap(self.icon_ico)
        
        self.app_width = 460
        self.app_height = 650
        self.is_fullscreen = False
        self.is_active = False
        
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        self.normal_x = (screen_width // 2) - (self.app_width // 2)
        self.normal_y = (screen_height // 2) - (self.app_height // 2)
        self.app.geometry(f"{self.app_width}x{self.app_height}+{self.normal_x}+{self.normal_y}")
        
        self.replacements = {
            "r": "w",
            "R": "W",
            ":)": ">w<",
            ":(": ">m<"
        }
        
        self.input_buffer = ""
        self.max_trigger_len = max(len(k) for k in self.replacements.keys())
        
        self.canvas = tk.Canvas(self.app, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.app.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.app.bind("<Configure>", self.on_resize)
        
        self.drag_x = 0
        self.drag_y = 0
        
        self.create_widgets()
        
        # Apply the explicit taskbar presence and bring the window to view
        self.app.after(10, self.force_taskbar_presence)
        
    def force_taskbar_presence(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.app.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            self.app.withdraw()
            self.app.after(10, self.bring_to_front)
        except Exception:
            self.bring_to_front()

    def bring_to_front(self):
        self.app.deiconify()
        self.app.lift()
        self.app.focus_force()

    def minimize_to_taskbar(self):
        try:
            # Send raw Windows drop message to drop the borderless frame directly to the taskbar row cleanly
            hwnd = ctypes.windll.user32.GetParent(self.app.winfo_id())
            ctypes.windll.user32.PostMessageW(hwnd, WM_SYSCOMMAND, SC_MINIMIZE, 0)
        except Exception:
            self.app.wm_state('iconic')

    def hide_to_tray(self):
        self.app.withdraw()
        
        if not self.tray_icon:
            if os.path.exists(self.icon_ico):
                image = Image.open(self.icon_ico)
            else:
                image = Image.new('RGB', (64, 64), color=(255, 182, 193))
                
            self.tray_icon = pystray.Icon("uwu_languaged", image, "✨ UWU Languaged ✨")
            self.tray_icon.on_activate = self.show_from_tray
            self.update_tray_menu()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            
        self.app.after(10, self.bring_to_front)

    def update_tray_menu(self):
        toggle_label = "Tuwn Off" if self.is_active else "Tuwn On"
        
        menu_structure = pystray.Menu(
            pystray.MenuItem('✨ Open App On Desktop', self.show_from_tray, default=True),
            pystray.MenuItem(f'⚙️ {toggle_label}', self.toggle_system_from_tray),
            pystray.MenuItem('❌ Close App Completely', self.on_closing)
        )
        if self.tray_icon:
            self.tray_icon.menu = menu_structure

    def toggle_system_from_tray(self, icon=None, item=None):
        self.app.after(0, self.toggle_system)

    def draw_background_and_bars(self):
        self.canvas.delete("gradient")
        self.canvas.delete("black_bars")
        
        win_w = self.app.winfo_width()
        win_h = self.app.winfo_height()
        
        app_start_x = (win_w - self.app_width) // 2
        app_end_x = app_start_x + self.app_width
        
        if win_w > self.app_width:
            self.canvas.create_rectangle(0, 0, app_start_x, win_h, fill="#000000", outline="", tags="black_bars")
            self.canvas.create_rectangle(app_end_x, 0, win_w, win_h, fill="#000000", outline="", tags="black_bars")
            
        r1, g1, b1 = 255, 255, 255
        r2, g2, b2 = 255, 192, 203
        
        for i in range(win_h):
            ratio = i / win_h
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(app_start_x, i, app_end_x, i, tags="gradient", fill=color)
        
        self.canvas.tag_lower("black_bars")
        self.canvas.tag_lower("gradient")

    def on_resize(self, event):
        self.draw_background_and_bars()
        center_x = self.app.winfo_width() // 2
        
        self.canvas.coords(self.title_bar_window, center_x, 15)
        self.canvas.coords(self.header_window, center_x, 90)
        self.canvas.coords(self.status_window, center_x, 160)
        self.canvas.coords(self.toggle_window, center_x, 215)
        self.canvas.coords(self.add_window, center_x, 330)
        self.canvas.coords(self.list_window, center_x, 500)
        self.canvas.coords(self.remove_window, center_x, 615)

    def start_window_drag(self, event):
        if not self.is_fullscreen:
            self.drag_x = event.x
            self.drag_y = event.y

    def execute_window_drag(self, event):
        if not self.is_fullscreen:
            x = self.app.winfo_x() + (event.x - self.drag_x)
            y = self.app.winfo_y() + (event.y - self.drag_y)
            self.app.geometry(f"+{x}+{y}")

    def toggle_fullscreen(self):
        if not self.is_fullscreen:
            self.normal_x = self.app.winfo_x()
            self.normal_y = self.app.winfo_y()
            screen_width = self.app.winfo_screenwidth()
            screen_height = self.app.winfo_screenheight()
            self.app.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_fullscreen = True
            self.fullscreen_btn.config(text=" 🗗 ")
        else:
            self.app.geometry(f"{self.app_width}x{self.app_height}+{self.normal_x}+{self.normal_y}")
            self.is_fullscreen = False
            self.fullscreen_btn.config(text=" 🗖 ")
        self.draw_background_and_bars()

    def create_widgets(self):
        title_bar = tk.Frame(self.app, bg="#FFB6C1", height=30)
        self.title_bar_window = self.canvas.create_window(230, 15, window=title_bar, width=self.app_width, height=30)
        
        title_bar.bind("<Button-1>", self.start_window_drag)
        title_bar.bind("<B1-Motion>", self.execute_window_drag)
        
        if os.path.exists(self.icon_png):
            try:
                self.img_data = tk.PhotoImage(file=self.icon_png)
                scale_w = self.img_data.width() // 16
                scale_h = self.img_data.height() // 16
                if scale_w > 0 and scale_h > 0:
                    self.img_data = self.img_data.subsample(scale_w, scale_h)
                
                icon_display = tk.Label(title_bar, image=self.img_data, bg="#FFB6C1")
                icon_display.pack(side="left", padx=(10, 0))
                icon_display.bind("<Button-1>", self.start_window_drag)
                icon_display.bind("<B1-Motion>", self.execute_window_drag)
            except Exception:
                pass
        
        title_text = tk.Label(title_bar, text="✨ UWU Languaged", font=("Arial", 10, "bold"), fg="#FF1493", bg="#FFB6C1")
        title_text.pack(side="left", padx=5)
        title_text.bind("<Button-1>", self.start_window_drag)
        title_text.bind("<B1-Motion>", self.execute_window_drag)
        
        close_btn = tk.Button(
            title_bar, text=" X ", font=("Arial", 9, "bold"), 
            bg="#FFC0CB", fg="#FF1493", activebackground="#FF1493", activeforeground="white",
            bd=0, command=self.on_closing, relief="flat"
        )
        close_btn.pack(side="right", padx=4, pady=2)
        
        self.fullscreen_btn = tk.Button(
            title_bar, text=" 🗖 ", font=("Arial", 9, "bold"), 
            bg="#FFC0CB", fg="#FF1493", activebackground="#FF69B4", activeforeground="white",
            bd=0, command=self.toggle_fullscreen, relief="flat"
        )
        self.fullscreen_btn.pack(side="right", padx=2, pady=2)
        
        minimize_btn = tk.Button(
            title_bar, text=" — ", font=("Arial", 9, "bold"), 
            bg="#FFC0CB", fg="#FF1493", activebackground="#FF69B4", activeforeground="white",
            bd=0, command=self.minimize_to_taskbar, relief="flat"
        )
        minimize_btn.pack(side="right", padx=2, pady=2)

        tray_btn = tk.Button(
            title_bar, text=" 🗗 ", font=("Arial", 9, "bold"),
            bg="#FFC0CB", fg="#FF1493", activebackground="#FF69B4", activeforeground="white",
            bd=0, command=self.hide_to_tray, relief="flat"
        )
        tray_btn.pack(side="right", padx=2, pady=2)

        header_frame = tk.Frame(self.app, bg="#FFB6C1", bd=2, relief="groove")
        self.header_window = self.canvas.create_window(230, 90, window=header_frame, width=420, height=70)
        
        header_label = tk.Label(header_frame, text="✨ UWU Languaged ✨", font=("Arial", 18, "bold"), fg="#FF1493", bg="#FFB6C1")
        header_label.pack(pady=15)
        
        self.status_label = tk.Label(self.app, text="Status: Off", font=("Arial", 12), fg="#666666", bg="#FFFFFF")
        self.status_window = self.canvas.create_window(230, 160, window=self.status_label)
        
        self.toggle_btn = tk.Button(
            self.app, text="Tuwn On >w<", font=("Arial", 13, "bold"), 
            bg="#FF69B4", fg="white", activebackground="#FF1493", activeforeground="white",
            relief="raised", bd=3, command=self.toggle_system
        )
        self.toggle_window = self.canvas.create_window(230, 215, window=self.toggle_btn, width=180, height=45)
        
        add_frame = tk.LabelFrame(
            self.app, text=" ✨ Add Custom Wules ✨ ", font=("Arial", 10, "bold"), 
            bg="#FFF0F5", fg="#FF1493", bd=2, relief="ridge"
        )
        self.add_window = self.canvas.create_window(230, 330, window=add_frame, width=420, height=130)
        
        tk.Label(add_frame, text="Look fow:", bg="#FFF0F5", fg="#333333", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=10)
        self.trigger_entry = tk.Entry(add_frame, width=12, font=("Arial", 11))
        self.trigger_entry.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(add_frame, text="➔", bg="#FFF0F5", fg="#666666").grid(row=0, column=2, padx=5)
        
        tk.Label(add_frame, text="Change to:", bg="#FFF0F5", fg="#333333", font=("Arial", 10)).grid(row=0, column=3, padx=5, pady=10)
        self.replace_entry = tk.Entry(add_frame, width=12, font=("Arial", 11))
        self.replace_entry.grid(row=0, column=4, padx=5, pady=10)
        
        add_btn = tk.Button(
            add_frame, text="Add Wuwe ✨", bg="#FFB6C1", fg="black", activebackground="#FF69B4",
            command=self.add_rule, font=("Arial", 10, "bold")
        )
        add_btn.grid(row=1, column=0, columnspan=5, pady=5)

        list_frame = tk.Frame(self.app, bg="#FFF0F5", bd=1, relief="solid")
        self.list_window = self.canvas.create_window(230, 500, window=list_frame, width=420, height=140)
        
        self.rules_listbox = tk.Listbox(
            list_frame, font=("Arial", 10), bg="#FFFFFF", fg="#333333", 
            selectbackground="#FFB6C1", selectforeground="black", bd=0
        )
        self.rules_listbox.pack(fill="both", expand=True, side="left", padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.rules_listbox.yview)
        scrollbar.pack(fill="y", side="right")
        self.rules_listbox.config(yscrollcommand=scrollbar.set)
        
        remove_btn = tk.Button(
            self.app, text="Wemove Selected Wuwe", font=("Arial", 10, "bold"), 
            bg="#FFA07A", fg="white", command=self.remove_rule
        )
        self.remove_window = self.canvas.create_window(230, 615, window=remove_btn, width=220, height=35)
        
        self.update_listbox()

    def update_listbox(self):
        self.rules_listbox.delete(0, tk.END)
        for trig, rep in self.replacements.items():
            self.rules_listbox.insert(tk.END, f"  {trig}  ➔  {rep}")
        self.max_trigger_len = max([len(k) for k in self.replacements.keys()] + [1])

    def add_rule(self):
        trig = self.trigger_entry.get()
        rep = self.replace_entry.get()
        if trig and rep:
            self.replacements[trig] = rep
            self.update_listbox()
            self.trigger_entry.delete(0, tk.END)
            self.replace_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Ewwow", "Pwease fill in both entwy fields.")

    def remove_rule(self):
        try:
            selected_idx = self.rules_listbox.curselection()[0]
            selected_text = self.rules_listbox.get(selected_idx)
            trig = selected_text.split("➔")[0].strip()
            
            del self.replacements[trig]
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Ewwow", "Pwease select a wuwe fwom the list to wemove.")

    def toggle_system(self):
        if not self.is_active:
            self.is_active = True
            self.status_label.config(text="Status: On", fg="#FF1493", bg="#FFF5F6")
            self.toggle_btn.config(text="Tuwn Off >m<", bg="#4A4A4A")
            keyboard.on_press(self.on_key_press)
        else:
            self.is_active = False
            self.status_label.config(text="Status: Off", fg="#666666", bg="#FFFFFF")
            self.toggle_btn.config(text="Tuwn On >w<", bg="#FF69B4")
            keyboard.unhook_all()
            self.input_buffer = ""
            
        self.update_tray_menu()

    def on_key_press(self, event):
        if len(event.name) == 1:
            char = event.name
            
            if char == 'r':
                keyboard.write('\b' + 'w')
                self.input_buffer += 'w'
            elif char == 'R':
                keyboard.write('\b' + 'W')
                self.input_buffer += 'W'
            else:
                self.input_buffer += char
                
            self.input_buffer = self.input_buffer[-self.max_trigger_len:]
            
            for trigger, replacement in self.replacements.items():
                if len(trigger) > 1 and self.input_buffer.endswith(trigger):
                    backspaces = '\b' * len(trigger)
                    keyboard.write(backspaces + replacement)
                    self.input_buffer = ""
                    break
        elif event.name == 'space':
            self.input_buffer += ' '
        elif event.name == 'backspace':
            self.input_buffer = self.input_buffer[:-1]

    def on_closing(self, icon=None, item=None):
        keyboard.unhook_all()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UwuLanguagedApp(root)
    root.mainloop()