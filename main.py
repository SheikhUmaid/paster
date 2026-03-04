import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time
import threading
import platform
import os

# Import pyautogui only on Windows if possible, or try-except for cross-platform safety
try:
    if platform.system() == "Windows":
        import pyautogui
    else:
        pyautogui = None
except ImportError:
    pyautogui = None

class SmallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wajahat")
        self.root.geometry("450x420")
        self.root.resizable(False, False)
        
        # Tracking variables
        self.countdown_active = False
        self.cancel_typing = False
        self.system_os = platform.system()

        # Set a clean background color
        self.root.configure(bg="#f0f2f5")

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure("Main.TFrame", background="#f0f2f5")
        self.style.configure("Footer.TFrame", background="#e1e4e8")
        
        self.style.configure("Header.TLabel", 
                             background="#f0f2f5", 
                             foreground="#1c1e21", 
                             font=("Segoe UI", 12, "bold"))
        
        self.style.configure("TLabel", 
                             background="#f0f2f5", 
                             foreground="#4b4f56", 
                             font=("Segoe UI", 10))
        
        self.style.configure("Status.TLabel", 
                             background="#f0f2f5", 
                             foreground="#d93025", 
                             font=("Segoe UI", 9, "bold"))
        
        self.style.configure("TButton", 
                             font=("Segoe UI", 10), 
                             padding=6)
        
        self.style.map("TButton",
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '!disabled', '#3a5998'), ('active', '#4267b2')])

        self.style.configure("Footer.TLabel", 
                             background="#e1e4e8", 
                             foreground="#606770", 
                             font=("Segoe UI", 8, "italic"))

        self.create_widgets()

    def create_widgets(self):
        # Header Area
        header_frame = ttk.Frame(self.root, style="Main.TFrame", padding=(20, 15, 20, 10))
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Auto Typer Utility", style="Header.TLabel").pack(side="left")

        # Status indicator
        self.status_var = tk.StringVar(value=f"Ready ({self.system_os})")
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side="right")

        # Separator
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=20)

        # Main Content Area
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding="20 20 20 20")
        main_frame.pack(fill="both", expand=True)

        # Row 0: ClipBoard preview
        ttk.Label(main_frame, text="Current Clipboard:").grid(row=0, column=0, sticky="w", pady=8)
        self.readonly_var = tk.StringVar(value="[Click 'View' to see full content]")
        self.readonly_entry = ttk.Entry(main_frame, textvariable=self.readonly_var, state="readonly", width=30)
        self.readonly_entry.grid(row=0, column=1, pady=8, padx=10, sticky="ew")

        # Row 1: Delay configuration
        ttk.Label(main_frame, text="Delay (seconds):").grid(row=1, column=0, sticky="w", pady=8)
        vcmd = (self.root.register(self.validate_integer), '%P')
        self.int_var = tk.StringVar(value="5")
        self.int_entry = ttk.Entry(main_frame, textvariable=self.int_var, validate="key", validatecommand=vcmd, width=30)
        self.int_entry.grid(row=1, column=1, pady=8, padx=10, sticky="ew")

        main_frame.columnconfigure(1, weight=1)

        # OS Specific Note
        engine = "PyAutoGUI" if (self.system_os == "Windows" and pyautogui) else ("xdotool" if self.system_os == "Linux" else "Unknown")
        note_text = f"Using {engine} for typing."
        ttk.Label(main_frame, text=note_text, font=("Segoe UI", 8, "italic"), foreground="#4267b2").grid(row=2, column=0, columnspan=2, pady=5)

        # Buttons Frame
        button_frame = ttk.Frame(main_frame, style="Main.TFrame")
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        # View Clipboard Button
        self.view_btn = ttk.Button(button_frame, text="View Clipboard", command=self.on_view_clipboard)
        self.view_btn.pack(side="top", fill="x", pady=5)

        # Action Buttons row
        action_btn_frame = ttk.Frame(button_frame, style="Main.TFrame")
        action_btn_frame.pack(side="top", fill="x", pady=5)

        self.stop_btn = ttk.Button(action_btn_frame, text="Stop / Cancel", command=self.on_stop)
        self.stop_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.paste_btn = ttk.Button(action_btn_frame, text="Start Typing", command=self.on_paste)
        self.paste_btn.pack(side="left", padx=5, expand=True, fill="x")

        # Footer Area
        footer_frame = ttk.Frame(self.root, style="Footer.TFrame", padding=(10, 5))
        footer_frame.pack(fill="x", side="bottom")
        
        footer_label = ttk.Label(footer_frame, 
                                 text="Created by Sheikh Umaid", 
                                 style="Footer.TLabel")
        footer_label.pack()

    def validate_integer(self, P):
        if P == "" or P.isdigit():
            return True
        return False

    def on_view_clipboard(self):
        try:
            content = self.root.clipboard_get()
            view_window = tk.Toplevel(self.root)
            view_window.title("Clipboard Viewer")
            view_window.geometry("400x300")
            view_window.transient(self.root)
            
            text_area = tk.Text(view_window, wrap="word", font=("Segoe UI", 10))
            text_area.insert("1.0", content)
            text_area.config(state="disabled")
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            
            ttk.Button(view_window, text="Close", command=view_window.destroy).pack(pady=5)
            self.readonly_var.set(content[:50] + ("..." if len(content) > 50 else ""))
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty or could not be read.")

    def on_stop(self):
        if self.countdown_active:
            self.cancel_typing = True
            self.status_var.set("Cancelled")
            messagebox.showinfo("Cancelled", "Typing action has been cancelled.")
        else:
            if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
                self.root.destroy()

    def on_paste(self):
        # Additional safety check for Windows + PyAutoGUI
        if self.system_os == "Windows" and pyautogui is None:
            messagebox.showerror("Dependency Error", "PyAutoGUI is not installed.\nPlease run: pip install pyautogui")
            return

        try:
            clipboard_text = self.root.clipboard_get()
            if not clipboard_text:
                raise tk.TclError
            
            self.readonly_var.set(clipboard_text[:50] + ("..." if len(clipboard_text) > 50 else ""))
            delay_str = self.int_var.get()
            delay = int(delay_str) if delay_str else 0
            
            threading.Thread(target=self.start_typing_sequence, args=(clipboard_text, delay), daemon=True).start()
        except tk.TclError:
            messagebox.showwarning("Warning", "Clipboard is empty or could not be read.")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number for delay.")

    def start_typing_sequence(self, text, delay):
        self.countdown_active = True
        self.cancel_typing = False
        
        for i in range(delay, 0, -1):
            if self.cancel_typing:
                self.countdown_active = False
                return
            self.status_var.set(f"Typing in {i}s...")
            time.sleep(1)
            
        if self.cancel_typing:
            self.countdown_active = False
            return
            
        self.status_var.set("Typing now!")
        try:
            if self.system_os == "Windows":
                # Use PyAutoGUI for better EXE compatibility
                # interval adds a small delay between each key press
                pyautogui.write(text, interval=0.01)
            else:
                # Default to Linux/xdotool
                subprocess.run(['xdotool', 'type', '--clearmodifiers', '--delay', '10', text], check=True)
            
            self.status_var.set("Done!")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to type: {str(e)}"))
            self.status_var.set("Error")
        
        self.countdown_active = False
        time.sleep(2)
        if not self.countdown_active:
            self.status_var.set(f"Ready ({self.system_os})")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmallApp(root)
    root.mainloop()
