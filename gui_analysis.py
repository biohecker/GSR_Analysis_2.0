#!/usr/bin/env python3
"""
GUI for EDA/GSR Analysis Pipeline
- Detects new .mat files
- Runs analysis only on new files (skips already processed)
- Updates comparison metrics
- Shows results and logs
"""

import json
import os
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Button, Text, Scrollbar, Listbox,
    filedialog, messagebox, scrolledtext, VERTICAL, BOTH, END, X, Y,
    DISABLED, NORMAL, LEFT, RIGHT, TOP, BOTTOM
)
from typing import List, Set

from eda_pipeline.config import EDAConfig

import pandas as pd


class EDAGUIApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("EDA/GSR Analysis Pipeline GUI")
        self.root.geometry("1000x700")
        
        self.workspace_dir = Path(__file__).parent
        # Load configuration if available so GUI follows same data/output dirs
        cfg_path = self.workspace_dir / "config.yaml"
        if cfg_path.exists():
            try:
                cfg = EDAConfig.from_yaml(cfg_path)
            except Exception:
                cfg = None
        else:
            cfg = None

        self.config = cfg
        self.data_dir = cfg.data_dir if cfg is not None else self.workspace_dir
        self.processed_dir = cfg.output_dir if cfg is not None else (self.workspace_dir / "processed_data")
        
        self.venv_path = self.workspace_dir / ".venv" / "bin" / "activate"
        self.is_processing = False
        
        self._create_ui()
        self._load_processed_files()
        
    def _create_ui(self):
        """Build UI layout"""
        # Header
        header = Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=X)
        
        title = Label(header, text="EDA/GSR Analysis Pipeline", 
                     font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=10)
        
        # Main content area
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left panel: File management
        left_panel = Frame(main_frame)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        Label(left_panel, text="Step 1: Select .mat Files", font=("Arial", 12, "bold")).pack(anchor="w")
        
        btn_frame = Frame(left_panel)
        btn_frame.pack(fill=X, pady=5)
        
        Button(btn_frame, text="Add .mat File", command=self._add_file, 
               bg="#3498db", fg="white", width=15).pack(side=LEFT, padx=2)
        Button(btn_frame, text="Scan Folder", command=self._scan_folder,
               bg="#27ae60", fg="white", width=15).pack(side=LEFT, padx=2)
        Button(btn_frame, text="Clear List", command=self._clear_list,
               bg="#e74c3c", fg="white", width=15).pack(side=LEFT, padx=2)
        
        Label(left_panel, text="Selected files:", font=("Arial", 10)).pack(anchor="w", pady=(10, 2))
        
        # Listbox for files
        listbox_frame = Frame(left_panel)
        listbox_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = Scrollbar(listbox_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.file_listbox = Listbox(listbox_frame, yscrollcommand=scrollbar.set, height=12)
        self.file_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Info box
        info_frame = Frame(left_panel)
        info_frame.pack(fill=X, pady=10)
        
        Label(info_frame, text="Processing Status:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.status_text = Label(info_frame, text="Ready", fg="#27ae60", font=("Arial", 9))
        self.status_text.pack(anchor="w")
        
        # Right panel: Controls & Results
        right_panel = Frame(main_frame)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        Label(right_panel, text="Step 2: Run Analysis", font=("Arial", 12, "bold")).pack(anchor="w")
        
        Button(right_panel, text="▶ RUN ANALYSIS", command=self._run_analysis,
               bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), 
               height=3).pack(fill=X, pady=10)
        
        Label(right_panel, text="Processing Log:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 2))
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(right_panel, height=18, width=45, 
                                                   bg="#ecf0f1", font=("Courier", 9))
        self.log_text.pack(fill=BOTH, expand=True)
        
        # Footer
        footer = Frame(self.root, bg="#ecf0f1", height=40)
        footer.pack(fill=X, side=BOTTOM)
        
        footer_btn_frame = Frame(footer, bg="#ecf0f1")
        footer_btn_frame.pack(fill=X, padx=10, pady=8)
        
        Button(footer_btn_frame, text="View Results CSV", command=self._view_results,
               bg="#3498db", fg="white").pack(side=LEFT, padx=2)
        Button(footer_btn_frame, text="Terminal Instructions", command=self._show_terminal_help,
               bg="#9b59b6", fg="white").pack(side=LEFT, padx=2)
        Button(footer_btn_frame, text="Refresh Status", command=self._load_processed_files,
               bg="#95a5a6", fg="white").pack(side=LEFT, padx=2)
        Button(footer_btn_frame, text="Exit", command=self.root.quit,
               bg="#34495e", fg="white").pack(side=RIGHT, padx=2)
        
    def _log(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {level}: {message}\n"
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, log_msg)
        self.log_text.see(END)
        self.log_text.config(state=NORMAL)
        self.root.update()
        
    def _load_processed_files(self):
        """Load list of already processed participants"""
        self.processed_files: Set[str] = set()
        if self.processed_dir.exists():
            for item in self.processed_dir.iterdir():
                if item.is_dir() and item.name != "summary":
                    self.processed_files.add(item.name)
        self._log(f"Loaded {len(self.processed_files)} previously processed participants", "OK")
        
    def _add_file(self):
        """Add single .mat file"""
        file = filedialog.askopenfilename(
            initialdir=str(self.data_dir),
            filetypes=[("MATLAB files", "*.mat"), ("All files", "*.*")]
        )
        if file:
            self.file_listbox.insert(END, Path(file).name)
            
    def _scan_folder(self):
        """Scan for all .mat files in workspace"""
        pattern = self.config.file_glob if getattr(self, "config", None) else "*.mat"
        mat_files = sorted(Path(self.data_dir).glob(pattern))

        # If nothing found in configured data_dir, try common fallbacks (project/data, cwd/data)
        if not mat_files:
            fallback_dirs = [self.workspace_dir / "data", Path.cwd() / "data"]
            found = []
            for fd in fallback_dirs:
                if fd.exists():
                    found = sorted(fd.glob(pattern))
                    if found:
                        self._log(f"No files in configured data_dir; using fallback {fd}", "INFO")
                        mat_files = found
                        # update data_dir so file operations copy here
                        self.data_dir = fd
                        break

        if not mat_files:
            messagebox.showwarning("No Files", f"No .mat files found in {self.data_dir}")
            return
        self.file_listbox.delete(0, END)
        for f in mat_files:
            self.file_listbox.insert(END, f.name)
        self._log(f"Found {len(mat_files)} .mat files", "OK")
        
    def _clear_list(self):
        """Clear file list"""
        self.file_listbox.delete(0, END)
        self._log("File list cleared", "INFO")
        
    def _run_analysis(self):
        """Run analysis on selected files"""
        files = [self.file_listbox.get(i) for i in range(self.file_listbox.size())]
        
        if not files:
            messagebox.showwarning("No Files", "Please add .mat files first")
            return
        
        if self.is_processing:
            messagebox.showwarning("Processing", "Analysis already running")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._process_files, args=(files,))
        thread.daemon = True
        thread.start()
        
    def _process_files(self, files: List[str]):
        """Process files in background"""
        self.is_processing = True
        self.log_text.delete(1.0, END)
        self._log("Starting analysis...", "INFO")
        
        try:
            # Check venv
            if not self.venv_path.exists():
                self._log("ERROR: Virtual environment not found at .venv", "ERROR")
                self._log("Please run: python -m venv .venv && source .venv/bin/activate", "ERROR")
                self.is_processing = False
                return
            
            # Copy files to workspace (if from outside)
            for fname in files:
                src = self.data_dir / fname
                if not src.exists():
                    # Try to find it elsewhere
                    search_result = list(Path.cwd().rglob(fname))
                    if search_result:
                        src = search_result[0]
                    else:
                        self._log(f"File not found: {fname}", "WARNING")
                        continue
                
                # Ensure destination is data_dir
                dest = Path(self.data_dir) / fname
                if src != dest:
                    self._log(f"Copying {fname} to data folder...", "INFO")
                    import shutil
                    shutil.copy2(src, dest)
            
            self._log(f"Processing {len(files)} file(s)...", "INFO")
            
            # Run analysis via subprocess
            cmd = f"source {self.venv_path} && python run_analysis.py --config config.yaml"
            result = subprocess.run(
                cmd, shell=True, cwd=str(self.workspace_dir),
                capture_output=True, text=True, executable="/bin/bash"
            )
            
            if result.returncode == 0:
                self._log("Analysis completed successfully!", "OK")
                self._log("Generating comparison metrics...", "INFO")
                self._load_processed_files()
                self._log(f"Total participants processed: {len(self.processed_files)}", "OK")
            else:
                self._log("Error during analysis:", "ERROR")
                self._log(result.stderr, "ERROR")
                
        except Exception as e:
            self._log(f"Exception: {str(e)}", "ERROR")
        finally:
            self.is_processing = False
            self.status_text.config(text="Ready", fg="#27ae60")
            
    def _view_results(self):
        """View comparison metrics CSV"""
        csv_path = self.processed_dir / "summary" / "comparison_metrics.csv"
        if not csv_path.exists():
            messagebox.showwarning("No Results", "No comparison_metrics.csv found")
            return
        
        try:
            df = pd.read_csv(csv_path)

            # --- FIX VS CODE ENVIRONMENT ISSUES HERE ---
            env = os.environ.copy()
            env["DISPLAY"] = env.get("DISPLAY", ":0")
            env["XDG_RUNTIME_DIR"] = env.get(
                "XDG_RUNTIME_DIR",
                f"/run/user/{os.getuid()}"
            )
            env["DBUS_SESSION_BUS_ADDRESS"] = env.get(
                "DBUS_SESSION_BUS_ADDRESS",
                f"unix:path=/run/user/{os.getuid()}/bus"
            )

            # Ensure LibreOffice gets a normal working directory
            cwd = os.path.expanduser("~")

            # --- LAUNCH LIBREOFFICE SAFE FOR TKINTER + VS CODE ---
            subprocess.Popen(
                ['localc', '--norestore', '--nolockcheck', str(csv_path)],
                cwd=cwd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            self._log(f"Opened results: {csv_path.name}", "INFO")

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            
    def _show_terminal_help(self):
        """Show terminal instructions"""
        help_text = """
╔═══════════════════════════════════════════════════════════════╗
║          TERMINAL INSTRUCTIONS (Backup)                       ║
╚═══════════════════════════════════════════════════════════════╝

1️⃣  FIRST TIME SETUP (one time only):
   cd /home/ballistic/Documents/gsr_analysis2.0
   source .venv/bin/activate
   pip install -r requirements.txt

2️⃣  ADD NEW .MAT FILE:
   cp /path/to/newfile.mat /home/ballistic/Documents/gsr_analysis2.0/

3️⃣  RUN ANALYSIS (processes ALL .mat files, overwrites existing):
   source .venv/bin/activate
   python run_analysis.py --config config.yaml

4️⃣  CHECK RESULTS:
   # View all participants
   ls processed_data/

   # View comparison metrics
   cat processed_data/summary/comparison_metrics.csv

   # View specific participant results
   ls processed_data/participant_001/
   cat processed_data/participant_001/metrics.json

5️⃣  IF YOU WANT INCREMENTAL PROCESSING (skip already processed):
   Use the GUI! It tracks processed files automatically.
   Or manually edit the pipeline.py to check for existing outputs.

═══════════════════════════════════════════════════════════════

QUICK REFERENCE:
├─ Activate venv:
│  source .venv/bin/activate
├─ Deactivate venv:
│  deactivate
├─ Run full analysis:
│  python run_analysis.py --config config.yaml
├─ View config:
│  cat config.yaml
└─ Edit filter settings in config.yaml before running

═══════════════════════════════════════════════════════════════
"""
        # Create help window
        help_win = Tk()
        help_win.title("Terminal Instructions")
        help_win.geometry("700x600")
        
        text_widget = scrolledtext.ScrolledText(help_win, font=("Courier", 9), bg="#2c3e50", fg="#ecf0f1")
        text_widget.pack(fill=BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, help_text)
        text_widget.config(state=DISABLED)
        
        Button(help_win, text="Close", command=help_win.destroy, bg="#e74c3c", fg="white").pack(pady=5)


def main():
    root = Tk()
    app = EDAGUIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
