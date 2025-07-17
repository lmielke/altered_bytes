#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
"""
info_bg_runner.pyw
Background runner/controller for a monitored Python module (Windows‑only).

Highlights
----------
* **Singleton** via atomic PID file.
* Spawns module in background with unique *instance id*.
* Optional tray icon (pystray+Pillow) to stop/show info.
* CLI: `start | stop | info`.
* All lines ≤ 95 chars; descriptive class names.
"""

from __future__ import annotations

import argparse
import atexit
import ctypes
import logging
import os
import re
import subprocess as sp
import sys
import threading as th
from datetime import datetime as dt
from pathlib import Path
from typing import Callable, List, Optional, Pattern

print(sys.executable)
import psutil

# ---------------------------------------------------------------------------
# optional tray dependencies
# ---------------------------------------------------------------------------
try:
    from PIL import Image  # type: ignore
    PIL_OK = True
except ImportError:  # pragma: no cover – tray disabled
    Image = None  # type: ignore
    PIL_OK = False
try:
    from pystray import Icon as TrayIcon, Menu, MenuItem  # type: ignore
    TRAY_OK = True
except ImportError:  # pragma: no cover
    TrayIcon, Menu, MenuItem = None, None, None  # type: ignore
    TRAY_OK = False

# ---------------------------------------------------------------------------
# logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
LOG = logging.getLogger(__name__)
# ---------------------------------------------------------------------------
# configuration holder
# ---------------------------------------------------------------------------
class AppConfig:
    """Collect immutable paths & settings once and share them across the app."""
    APP_NAME = Path(sys.argv[0]).stem
    DEFAULT_MODULE = "altered.info_app_hist_activities"
    _ROOT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    RESOURCES = _ROOT_DIR / "resources"
    _PREFERRED_EXE = (
        "~/.virtualenvs/altered_bytes-uZ3fI-DB/Scripts/pythonw.exe"  # user‑specific
    )
    _CACHED_EXE: Optional[str] = None


    def __init__(self, module: Optional[str] = None, *, no_gui: bool = False) -> None:
        self.module = module or self.DEFAULT_MODULE
        self.no_gui = no_gui
        # resolve interpreter once per process
        if AppConfig._CACHED_EXE is None:
            AppConfig._CACHED_EXE = self._select_python_exe()
        self.python_exe = AppConfig._CACHED_EXE
        # machine‑specific paths
        self.log_id = self.module.split(".")[-1].split("_")[-1]
        self.logs_dir = self.RESOURCES / "logs" / self.log_id
        self.pid_file = self.logs_dir / f"{self.log_id}.pid"
        self.icon_path = self._locate_icon()
        self.instance_prefix = "bg_run"
        self.instance_re: Pattern[str] = re.compile(
            rf"{self.instance_prefix}:{re.escape(self.module)}:" r"\d{4}-\d{2}-\d{2}_\d{6}"
        )

    # ------------------------------------------------------------------
    def _select_python_exe(self) -> str:
        pref = Path(self._PREFERRED_EXE).expanduser()
        if pref.is_file():
            LOG.info(f"Using preferred interpreter: {pref}")
            return str(pref)
        cur = Path(sys.executable)
        if cur.name.lower() == "python.exe":
            pyw = cur.with_name("pythonw.exe")
            if pyw.is_file():
                LOG.info(f"Using sibling pythonw.exe: {pyw}")
                return str(pyw)
        LOG.info(f"Using current interpreter: {sys.executable}")
        return sys.executable

    def _locate_icon(self) -> Path:
        primary = self.RESOURCES / "images" / f"{self.module}.png"
        if primary.exists():
            return primary
        fallback = self.RESOURCES / "images" / f"{self.APP_NAME}.png"
        if fallback.exists():
            return fallback
        LOG.warning(f"No icon found for {self.module}. Using placeholder.")
        return primary  # non‑existing triggers solid‑colour fallback


# ---------------------------------------------------------------------------
# process helpers
# ---------------------------------------------------------------------------
class ProcessManager:
    """Start/stop/query child module instances using *psutil*."""


    def __init__(self, cfg: AppConfig):
        self.cfg = cfg

    def terminate_pid(self, pid: int, label: str = "process") -> bool:
        if pid <= 0:
            return False
        LOG.info(f"Stopping {label} (PID {pid})…")
        try:
            proc = psutil.Process(pid)
            proc.terminate(); proc.wait(timeout=2)
            LOG.info(f"{label.capitalize()} (PID {pid}) terminated.")
            return True
        except psutil.TimeoutExpired:
            LOG.warning(f"{label.capitalize()} (PID {pid}) force‑kill.")
            proc.kill(); proc.wait(timeout=1) # type: ignore[possibly-undefined]
            return True
        except psutil.NoSuchProcess:
            LOG.info(f"{label.capitalize()} (PID {pid}) already exited.")
            return True
        except Exception as exc:  # pragma: no cover
            LOG.error(f"{label.capitalize()} (PID {pid}) stop error: {exc}")
            return False

    def stop_module_children(self) -> int:
        stopped = 0
        for proc in self._iter_procs():
            cmdline_list = proc.info.get("cmdline") # Safely get 'cmdline'
            cmd = "" # Default to empty string if not found or not usable
            if cmdline_list is not None:
                cmd = " ".join(cmdline_list)
            else:
                LOG.debug(  f"Skipping process PID {proc.pid} for stop_module_children, "
                            f"no cmdline info.")
                # continue # Or let it try to match empty cmd if that's desired (likely not)
            if cmd and self.cfg.instance_re.search(cmd): # Check if cmd is not empty
                if self.terminate_pid(proc.pid, "child"):
                    stopped += 1
        LOG.info(f"Stopped {stopped} child processes.")
        return stopped

    def list_module_children(self) -> List[str]:
        lines: List[str] = []
        for proc in self._iter_procs():
            cmdline_list = proc.info.get("cmdline") # Safely get 'cmdline'
            cmd = "" # Ensure cmd is initialized
            if cmdline_list is None:
                LOG.debug(f"Skipping process PID {proc.pid} for list_module_children, "
                            f"no cmdline info.")
                continue
            else:
                cmd = " ".join(cmdline_list)
            # Proceed with regex search only if cmd is meaningfully populated
            if cmd and self.cfg.instance_re.search(cmd): # Check if cmd is not empty
                short = (cmd[:80] + "…") if len(cmd) > 80 else cmd
                lines.append(f"  • PID {proc.pid}: {short}")
        return lines

    @staticmethod
    def _iter_procs():
        return psutil.process_iter(attrs=["pid", "cmdline", "status"], ad_value=None)


# ---------------------------------------------------------------------------
# PID file manager
# ---------------------------------------------------------------------------
class PidFileManager:
    """Atomically acquire/release a PID file to prevent multiple runners."""


    def __init__(self, path: Path, is_same_runner: Callable[[int], bool]):
        self.path = path
        self._is_same = is_same_runner
        self._owns = False

    def acquire(self) -> bool:
        if self.active(): # This now handles stale/corrupt cleanup
            LOG.warning(f"Runner determined to be already active for: {self.path.stem}")
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Attempt atomic creation
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as fh:
                fh.write(str(os.getpid()))
            self._owns = True; atexit.register(self.release)
            LOG.info(f"PID {os.getpid()} written to {self.path}")
            return True
        except FileExistsError: # Should be less common if active() cleans up
            LOG.warning(f"PID file {self.path} existed unexpectedly after active() check. "
                        f"Possible race or lock error.")
            # Re-check if another process just created it and is valid
            if self._is_pid_file_valid_and_active():
                return False
            else: # Still stale or invalid, attempt forceful overwrite as last resort
                LOG.warning(f"Forcefully overwriting questionable PID file: {self.path}")
                try:
                    with open(self.path, 'w') as fh: # Non-atomic overwrite
                        fh.write(str(os.getpid()))
                    self._owns = True; atexit.register(self.release)
                    LOG.info(f"PID {os.getpid()} force-written to {self.path}")
                    return True
                except OSError as err_overwrite:
                    LOG.error(f"Forceful PID file overwrite failed: {err_overwrite}")
                    return False
        except OSError as err:
            LOG.error(f"PID file write error: {err}")
            return False

    def release(self):
        if self._owns and self.path.exists():
            try:
                self.path.unlink(); LOG.info(f"Removed PID file {self.path}")
            except OSError as err: # pragma: no cover
                LOG.warning(f"PID cleanup failed: {err}")
            self._owns = False

    def _is_pid_file_valid_and_active(self) -> bool:
        """Helper to read PID from file and check if it's a valid, active runner."""
        if not self.path.exists():
            return False
        try:
            pid = int(self.path.read_text().strip())
            if self._is_same(pid):
                return True
        except Exception: # Includes ValueError, IOError
            pass # Considered invalid
        return False

    def active(self) -> bool:
        if not self.path.exists():
            return False
        try:
            pid = int(self.path.read_text().strip())
        except Exception as exc: # Catches ValueError from int(), IOError from read_text, etc.
            LOG.warning(f"Corrupt PID file: {self.path} ({exc}). Attempting cleanup.")
            try:
                self.path.unlink(missing_ok=True)  # MODIFIED: Directly unlink corrupt file
            except OSError as e_unlink: # pragma: no cover
                LOG.warning(f"Failed to clean up corrupt PID file {self.path}: {e_unlink}")
            return False  # Not active
        if self._is_same(pid):  # Check if the PID belongs to a live, matching runner
            LOG.info(f"Runner (PID {pid}) confirmed active for module "
                        f"'{self.path.stem.split('.')[0]}'.")
            return True
        # If not the same (stale or different process type)
        LOG.warning(f"Stale or mismatched PID {pid} in file {self.path}. Attempting cleanup.")
        try:
            self.path.unlink(missing_ok=True)  # MODIFIED: Directly unlink stale file
        except OSError as e_unlink: # pragma: no cover
            LOG.warning(f"Failed to clean up stale PID file {self.path}: {e_unlink}")
        return False  # Not active (stale and attempted cleanup)


# ---------------------------------------------------------------------------
# tray interface
# ---------------------------------------------------------------------------
class TrayInterface:
    """Tiny pystray wrapper with *Info* and *Stop* menus."""

    def __init__(
        self, cfg: AppConfig, *, on_stop: Callable[[], None], on_info: Callable[[], None]
    ) -> None:
        self.cfg = cfg; self.on_stop = on_stop; self.on_info = on_info
        self.icon: Optional[TrayIcon] = None
        self.enabled = TRAY_OK and PIL_OK
        if not self.enabled: # pragma: no cover
            LOG.warning("Tray disabled (pystray or Pillow missing).")

    def _threaded_on_info(self): # MODIFIED: New method for threaded info callback
        """Ensures self.on_info runs in a new thread to avoid blocking the tray."""
        LOG.debug("Creating dedicated thread for tray 'Info' action.")
        info_thread = th.Thread(target=self.on_info, name="TrayShowInfoThread", daemon=True)
        info_thread.start()

    def run(self) -> None:
        if not self.enabled: # pragma: no cover
            return
        self.icon = TrayIcon(
            name=f"{self.cfg.APP_NAME}_{self.cfg.module}",
            title=f"{self.cfg.APP_NAME} – {self.cfg.module}",
            icon=self._create_image(),
            menu=Menu(
                MenuItem("Info", lambda *_: self._threaded_on_info()), # MODIFIED
                MenuItem("Stop", lambda *_: self.on_stop()),
            ),
        ); LOG.info("Tray loop starting…"); self.icon.run()

    def stop(self) -> None: # pragma: no cover
        if self.icon is not None:
            self.icon.stop()

    def _create_image(self): # pragma: no cover
        if not PIL_OK:
            return None
        try:
            if self.cfg.icon_path.exists():
                return Image.open(self.cfg.icon_path)  # type: ignore[arg-type]
        except Exception as exc:
            LOG.warning(f"Icon load failed: {exc}")
        return Image.new("RGB", (64, 64), "maroon")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# application runner
# ---------------------------------------------------------------------------
class ApplicationRunner:
    """Coordinates config, PID lock, child process launch, tray and CLI actions."""

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.proc_mgr = ProcessManager(cfg)
        self.pid_mgr = PidFileManager(cfg.pid_file, self._is_same_runner)
        self.tray: Optional[TrayInterface] = None
        self._stop_evt = th.Event()
        self.instance_id: Optional[str] = None

    # ------------------------------------------------------------------
    def _is_same_runner(self, pid: int) -> bool:
        try:
            proc = psutil.Process(pid)
            # Check process name, creation time (less reliable), and command line
            # Ensure it's a python process running *this* script file.
            if not proc.is_running(): return False # Must be running
            cl = proc.cmdline() or []
            # Check if second element of cmdline (often script path) matches script's stem
            # This is a heuristic; sys.argv[0] might be a full path or just the name.
            # It's important that Path(sys.argv[0]).stem is consistent for the runner.
            if len(cl) > 1 and Path(cl[1]).stem == Path(sys.argv[0]).stem:
                return True
            # Fallback or alternative check: if the executable name itself is our script
            # (e.g. if frozen or run directly and `sys.argv[0]` is just script name)
            if Path(proc.name()).stem == Path(sys.argv[0]).stem:
                return True
            return False
        except psutil.Error: # Catches NoSuchProcess, AccessDenied etc.
            return False

    def _msg_box(self, msg: str, title: str, level: str = "info") -> None:
        if self.cfg.no_gui or sys.platform != "win32": # pragma: no cover
            print(f"[{title} – {level.upper()}]\n{msg}"); return
        icons = {"info": 64, "warning": 48, "error": 16} # MB_ICON...
        try: # pragma: no cover
            ctypes.windll.user32.MessageBoxW( # type: ignore[attr-defined]
                0, msg, title, icons.get(level, 0)
            )
        except Exception as e_msgbox:
            LOG.error(f"Failed to display Windows message box: {e_msgbox}")
            print(f"[{title} – {level.upper()} _MSG_BOX_ERROR_]:\n{msg}")


    def _launch_child(self) -> None:
        ts = dt.now().strftime("%Y-%m-%d_%H%M%S")
        self.instance_id = f"{self.cfg.instance_prefix}:{self.cfg.module}:{ts}"
        cmd = [self.cfg.python_exe, "-m", self.cfg.module, "-id", self.instance_id]
        LOG.info(f"Launching child: {' '.join(cmd)}")
        # Correctly use getattr for platform-specific flags
        flags = 0
        if sys.platform == "win32": # pragma: no cover
            flags = getattr(sp, "DETACHED_PROCESS", 0) | \
                    getattr(sp, "CREATE_NEW_PROCESS_GROUP", 0)
        try:
            sp.Popen(cmd, stdin=sp.DEVNULL, stdout=sp.DEVNULL, stderr=sp.DEVNULL, 
                        creationflags=flags)
        except FileNotFoundError: # pragma: no cover
            LOG.error(f"Python executable for child not found: {self.cfg.python_exe}")
            self._msg_box(f"Error: Executable not found:\n{self.cfg.python_exe}",
                          f"{self.cfg.APP_NAME} Error", "error")
            raise # Re-raise to be caught by start()
        except Exception as e_popen: # pragma: no cover
            LOG.error(f"Failed to launch child process: {e_popen}", exc_info=True)
            self._msg_box(f"Error launching child:\n{e_popen}",
                          f"{self.cfg.APP_NAME} Error", "error")
            raise # Re-raise

    # ------------------------------------------------------------------
    def start(self) -> None:
        if not self.pid_mgr.acquire():
            self._msg_box("Runner already active for this module.",
                          f"{self.cfg.APP_NAME} - Already running", "warning"); return
        try:
            self._launch_child()
            self.tray = TrayInterface(self.cfg, on_stop=self.request_graceful_stop, 
                                        on_info=self.show_info)
            if self.tray.enabled: # pragma: no cover
                self.tray.run() # This blocks until tray.stop() or icon is quit
            else: # Headless mode
                LOG.info("Running headlessly (no tray). Waiting for stop signal.")
                while not self._stop_evt.wait(1.0): # Corrected headless loop
                    pass # Wait for event or timeout
                LOG.info("Headless runner stop signal received.")
        except Exception as e_start: # Catch errors from _launch_child or tray init
            LOG.error(f"Critical error during start sequence: {e_start}", exc_info=True)
            # pid_mgr.release() will be called by atexit if acquire was successful
            # If acquire failed, _owns is false, release does nothing.
            # If acquire succeeded but then error, atexit will handle it.
            # No explicit release here unless acquire state needs careful reset.
        finally:
            # This ensures that if tray.run() exits (e.g., user closes tray),
            # or if headless loop finishes, a full stop is triggered.
            LOG.debug("Start method's main loop/try block finished. Ensuring stop.")
            self.request_graceful_stop() # Ensure full cleanup

    def request_graceful_stop(self) -> None: # Renamed from 'stop' to be more specific
        """Initiates a graceful shutdown of the runner and its children."""
        if self._stop_evt.is_set(): # Already stopping
            return
        LOG.info(f"Graceful stop requested for runner of module: {self.cfg.module}")
        self._stop_evt.set() # Signal all loops to terminate
        # Stop children first
        self.proc_mgr.stop_module_children()
        # Stop tray (this unblocks tray.run() if it was running)
        if self.tray and self.tray.enabled: # pragma: no cover
            self.tray.stop()
        # Release PID, typically handled by atexit if this instance acquired it.
        # However, calling it here ensures it's released if atexit doesn't run
        # (e.g. abnormal termination before atexit).
        # self.pid_mgr.release() # atexit handles this if _owns is True.
        LOG.info(f"Runner for module '{self.cfg.module}' has processed stop request.")


    def show_info(self) -> None: # This is now called in a separate thread by TrayInterface
        LOG.debug("Preparing to show info.")
        status_lines = [
            f"Runner PID: {os.getpid()}",
            f"Monitoring Module: {self.cfg.module}",
            f"Instance ID (curr child): {self.instance_id or 'N/A (not launched or error)'}",
            f"PID File: {self.cfg.pid_file}",
        ]
        child_procs = self.proc_mgr.list_module_children()
        if child_procs:
            status_lines.append("Active Monitored Child Processes:")
            status_lines.extend(child_procs)
        else:
            status_lines.append("No active child processes found for this module.")
        info_text = "\n".join(status_lines)
        self._msg_box(info_text, f"{self.cfg.APP_NAME} Info")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Background runner for Python modules.")
    p.add_argument("cmd", choices=["start", "stop", "info"], help="command to execute")
    p.add_argument("-m", "--module", help="module to launch/manage", dest="module")
    p.add_argument("--no-gui", action="store_true", help="suppress message boxes")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None: # pragma: no cover
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    cfg = AppConfig(args.module, no_gui=args.no_gui)
    # Logging starts after config is available for module-specific context if needed
    LOG.info(f"Runner CMD: {args.cmd}, Module: {cfg.module}, NoGUI: {cfg.no_gui}")

    if args.cmd == "start":
        app = ApplicationRunner(cfg)
        app.start()
    elif args.cmd == "stop":
        # This 'stop' is external: stops children of the target module,
        # then tries to stop the runner identified by that module's PID file.
        proc_mgr_ext = ProcessManager(cfg) # Use current config for target module
        LOG.info(f"External stop initiated for module: {cfg.module}")
        proc_mgr_ext.stop_module_children()
        
        pid_to_stop: Optional[int] = None
        if cfg.pid_file.exists():
            try:
                pid_to_stop = int(cfg.pid_file.read_text().strip())
            except ValueError:
                LOG.warning(f"Corrupt PID value in {cfg.pid_file}")
            except Exception as e_read:
                LOG.error(f"Error reading PID file {cfg.pid_file}: {e_read}")

        if pid_to_stop:
            if proc_mgr_ext.terminate_pid(pid_to_stop, f"runner for '{cfg.module}'"):
                LOG.info(f"External runner (PID {pid_to_stop}) for module '{cfg.module}' "
                            f"terminated.")
        else:
            LOG.info(f"No active runner PID found in {cfg.pid_file} to stop externally.")
        
        # Clean up the PID file for the module being stopped.
        try:
            cfg.pid_file.unlink(missing_ok=True)
            LOG.info(f"PID file {cfg.pid_file} unlinked by external stop command.")
        except OSError as e_unlink:
            LOG.warning(f"Failed to unlink PID file {cfg.pid_file} "
                        f"during external stop: {e_unlink}")

    elif args.cmd == "info":
        # For CLI 'info', we don't start a full ApplicationRunner instance.
        # We just want to query based on the config.
        # This means we can't easily get the "Runner PID" if it's a different instance.
        # The info shown will be about children of the specified module.
        proc_mgr_info = ProcessManager(cfg)
        status_lines = [
            f"Information for Module: {cfg.module}",
            f"Associated PID File: {cfg.pid_file}",
        ]
        
        runner_pid_from_file: Optional[int] = None
        if cfg.pid_file.exists():
            try:
                runner_pid_from_file = int(cfg.pid_file.read_text().strip())
                # Check if this PID is actually a live runner for this app_name
                # requires a way to check without a full AppRunner instance's _is_same_runner
                # For simplicity, just report PID found. A more advanced check could be added.
                # temp_is_same = ApplicationRunner(cfg)._is_same_runner # hacky
                # For now, just state PID in file:
                status_lines.append(f"PID found in file: {runner_pid_from_file}")

            except ValueError:
                status_lines.append("PID file contains non-integer value.")
            except Exception:
                status_lines.append("Could not read PID from file.")


        child_procs = proc_mgr_info.list_module_children()
        if child_procs:
            status_lines.append("Active Monitored Child Processes:")
            status_lines.extend(child_procs)
        else:
            status_lines.append("No active child processes found for this module.")
        
        info_text = "\n".join(status_lines)
        
        # Use the message box utility (respects --no-gui and platform)
        # Need an AppConfig instance for _msg_box, cfg is already it.
        # To call _msg_box, we'd need an ApplicationRunner, or factor _msg_box out.
        # For simplicity, just print for CLI 'info', respecting no_gui only for Message Box.
        if cfg.no_gui or sys.platform != "win32" or not sys.stdout.isatty():
            print(info_text)
        else:
            try:
                ctypes.windll.user32.MessageBoxW(0, info_text, f"{cfg.APP_NAME} Info", 64)
            except Exception as e_msg:
                LOG.error(f"CLI Info: Failed to display message box: {e_msg}")
                print(info_text) # Fallback to print

if __name__ == "__main__": # pragma: no cover
    try:
        main()
    except Exception as e_global:
        LOG.critical(f"Global unhandled exception: {e_global}", exc_info=True)
        # Attempt to show a message box if possible for critical failures
        try:
            if sys.platform == "win32" and not any(arg == "--no-gui" for arg in sys.argv):
                ctypes.windll.user32.MessageBoxW(
                    0, f"Fatal Script Error:\n{e_global}",
                    f"{AppConfig.APP_NAME} CRITICAL ERROR", 16 # MB_ICONERROR
                )
        except Exception: # nested try for message box itself
            pass # If even message box fails, we've logged.
        sys.exit(1)