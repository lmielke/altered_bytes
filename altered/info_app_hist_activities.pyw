"""
info_app_hist_activities.pyw
"""

import os, sys, time

import ctypes
import psutil
import win32gui
import time
import json
from datetime import datetime
from pynput import mouse, keyboard
from functools import lru_cache
import altered.settings as sts

class UserActivity:

    elevators = {   
                keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.alt_l, 
                keyboard.Key.alt_r, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
                }

    def __init__(self, *args, **kwargs):
        self.mouse_click_count = 0
        self.key_press_count = 0
        self.pressed_keys = set()  # Track currently pressed elevator keys
        self.pressed_elevators = set()  # Track currently pressed elevator keys
        self.keyboard_shortcuts = []  # History of pressed elevator key combinations
        self.combination = ''  # Track whether any elevator key is active
        self.mouse_listener = None
        self.keyboard_listener = None

    @staticmethod
    @lru_cache(maxsize=128)
    def get_str_rep(key) -> str:
        """
        Get the string representation of the key.
        """
        if isinstance(key, keyboard.KeyCode) and key.char:
            if ord(key.char) < 32:  # Detect control characters
                return (f"{chr(ord(key.char) + 64)}".capitalize()
                                                    .replace('_l', '').replace('_r', ''))
            return key.char
        elif isinstance(key, keyboard.Key):
            if key == keyboard.Key.enter:
                return 'enter'
            elif key == keyboard.Key.esc:
                return 'esc'
            elif key == keyboard.Key.space:
                return 'space'
            elif key == keyboard.Key.tab:
                return 'tab'
            elif key == keyboard.Key.backspace:
                return 'backspace'
            return (str(key).replace('Key.', '').capitalize()
                                                .replace('_l', '').replace('_r', ''))
        else:
            return repr(key)


    def on_click(self, x, y, button, pressed):
        """Logs mouse click events and counts clicks."""
        if pressed:
            self.mouse_click_count += 1

    def on_key_press(self, key):
        """
        Logs key presses, including elevator keys and non-elevator keys 
        if an elevator key is pressed.
        """
        self.key_press_count += 1
        # Always run get_str_rep before adding the elevator key
        if key in self.elevators:
            if key not in self.pressed_elevators:
                self.pressed_elevators.add(key)
                self.combination = self.get_str_rep(key)
        # Track non-elevator key presses while any elevator key is pressed
        elif self.pressed_elevators and not key in self.pressed_keys: 
            if self.combination:
                self.combination += f"+{self.get_str_rep(key)}"
            else:
                self.combination = (
                                    f"{self.get_str_rep(list(self.pressed_elevators)[0])}"
                                    f"+{self.get_str_rep(key)}"
                                    )
            self.pressed_keys.add(key)

    def add_keyboard_shortcut(self, shortcut, *args, **kwargs):
        if len(self.keyboard_shortcuts) >= 1:
            if self.keyboard_shortcuts[-1][:-2] == shortcut and '*' in self.keyboard_shortcuts[-1]:
                sc, count = self.keyboard_shortcuts[-1].split('*')
                shortcut = f"{sc}*{int(count) + 1}"
                self.keyboard_shortcuts[-1] = shortcut
            elif self.keyboard_shortcuts[-1] == shortcut:
                self.keyboard_shortcuts[-1] = f"{shortcut}*2"
            else:
                self.keyboard_shortcuts.append(shortcut)
        else:
            self.keyboard_shortcuts.append(shortcut)

    def on_key_release(self, key):
        """Handles key release and checks if all elevator keys are inactive."""
        if key in self.elevators:
            if self.combination:
                self.add_keyboard_shortcut(self.combination)
                self.combination = ""
            self.pressed_elevators.clear()
            self.pressed_keys.clear()
        if key in self.pressed_keys:
            if self.combination:
                self.add_keyboard_shortcut(self.combination)
                self.combination = ""
            self.pressed_keys.remove(key)

    def start_listeners(self, *args, **kwargs):
        """Start listening to mouse clicks and key presses."""
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()
        self.keyboard_listener = keyboard.Listener(
                                                        on_press=self.on_key_press, 
                                                        on_release=self.on_key_release
                                                    )
        self.keyboard_listener.start()

    def stop_listeners(self, *args, **kwargs):
        """Stop listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()


class ActivityHistory:

    def __init__(self, *args, log_name:str="activity_log", user_activity=None, **kwargs):
        self.log_name = f"{log_name}.json"
        self.last_activity = None
        self.last_timestamp = None
        self.user_activity = user_activity if user_activity else UserActivity()
        self._active_window = None
        self.log_counter, self.log_max_len = 200, 200

    def clean_title(self, window_title):
        """
        Remove the bullet dot (•) and any leading/trailing whitespace from the window title.
        """
        return window_title.replace("• ", "").strip()

    def get_active_window_info(self, *args, **kwargs):
        """Get the current active window's application name and title."""
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if hwnd:
            window_title = win32gui.GetWindowText(hwnd)
            # Get process ID
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            try:
                process = psutil.Process(pid.value)
                app_name = process.name()
            except psutil.NoSuchProcess:
                app_name = "Unknown"
            return {
                    "application_name": app_name,
                    "active_window": window_title.strip()
                    }
        return {
                    "application_name": "No active application",
                    "active_window": "No active window"
                }

    def log_window_exit(self, old_window_info, start_time, *args, **kwargs):
        """Log the old window information when you leave it, including the duration."""
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        end_time_str = end_time.strftime(sts.time_strf[:-3])
        window_title = old_window_info["active_window"].replace(sts.project_dir, 
                                                                        f'/sts.project_dir')
        log_entries = {
                        "timestamp_entered": start_time.strftime(sts.time_strf[:-3]),
                        "timestamp_exited": end_time_str,
                        "duration_seconds": duration,
                        "application_name": old_window_info["application_name"],
                        "active_window": window_title,
                        "mouse_click_count": self.user_activity.mouse_click_count,
                        "key_press_count": self.user_activity.key_press_count,
                        "keyboard_shortcuts": self.user_activity.keyboard_shortcuts
                    }
        # add intensity as measure how significant the activity was
        log_entries["intensity"] = self.get_intensity(*args, **log_entries)
        # Reset the counters and history after logging
        self.user_activity.mouse_click_count = 0
        self.user_activity.key_press_count = 0
        self.user_activity.keyboard_shortcuts = []  # Reset elevator keys history
        self.save_log_file(end_time_str, log_entries, *args, **kwargs)

    def get_intensity(self, *args, key_press_count:int, keyboard_shortcuts:list, **kwargs):
        """
        Calculate the activity intensity based on the number, key presses 
        and keyboard shortcuts.
        Intensity can have several levels: little, moderate, significant, and extreme.
        """
        # shortcut might have a counter int appended to the shortcut string like Ctrl+S*2
        was_saved = any([shortcut.startswith('Ctrl+S') for shortcut in keyboard_shortcuts])
        if not was_saved or key_press_count <= 10:
            return 'little'
        elif keyboard_shortcuts and (10 < key_press_count <= 50):
            return 'moderate'
        elif keyboard_shortcuts and (50 < key_press_count <= 100):
            return 'significant'
        elif keyboard_shortcuts and key_press_count > 100:
            return 'extreme'

    def save_log_file(self, end_time_str:str, log_entries:str, *args, **kwargs):
        # due to handling reasons we limit the length of the log file to log_max_len entries
        if self.log_counter >= self.log_max_len:
            self.log_file_name = f"{end_time_str}_{self.log_name}"
            self.log_counter = 0
        # Append the log entry to the log file
        with open(os.path.join(sts.logs_dir, 'activities', self.log_file_name), "a") as f:
            json.dump(log_entries, f)
            f.write("\n")
        self.log_counter += 1

    def monitor_window_changes(self, *args, **kwargs):
        """Continuously monitor for changes in the active window."""
        self.user_activity.start_listeners(*args, **kwargs)
        try:
            while True:
                current_window_info = self.get_active_window_info()
                sanitized_window = self.clean_title(current_window_info["active_window"])
                # Check if the sanitized window title has actually changed
                if sanitized_window != self._active_window:
                    # Log the previous window if it exists
                    if self.last_activity is not None and self.last_timestamp is not None:
                        self.log_window_exit(self.last_activity, self.last_timestamp)
                    # Update to the new window and timestamp
                    self.last_activity = current_window_info
                    self.last_timestamp = datetime.now()
                    self._active_window = sanitized_window
                time.sleep(1)
        except KeyboardInterrupt:
            self.user_activity.stop_listeners()

if __name__ == "__main__":
    # Create an instance of ActivityHistory and UserActivity
    user_activity = UserActivity()
    activity_history = ActivityHistory(user_activity=user_activity)
    print(  f"Monitoring window changes with key, mouse, and elevator key activity. "
            f"Press Ctrl+C to stop.")
    activity_history.monitor_window_changes()
