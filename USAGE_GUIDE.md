# Using the Analysis Tools: GUI vs Terminal

## Quick Answer to Your Questions

### ❓ Will it reprocess ALL files every time?

**Current behavior (run_analysis.py):** YES, it re-processes all .mat files every time.
- ✅ Good: Simple, always up-to-date
- ❌ Bad: Slower with many files, overwrites existing results

**Better option (run_incremental_analysis.py):** NO, only NEW files
- ✅ Processes only newly-detected `.mat` files by default and writes outputs for those files only
- ✅ Appends new participants to the comparison CSV rather than overwriting unrelated entries
- ✅ Much faster for large datasets and preserves existing results unless `--force` is used

---

## 🎨 Option 1: Using the GUI (Recommended)

### Setup (First Time Only)

```bash
cd /home/ballistic/Documents/gsr_analysis2.0
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the GUI

```bash
source .venv/bin/activate
python gui_analysis.py
```

**The GUI:**
- ✅ Automatically activates venv
- ✅ Tracks which files are already processed
- ✅ Shows processing progress in real-time
- ✅ Auto-updates comparison metrics
- ✅ Has built-in terminal instructions as fallback
- ✅ Easy file selection

### GUI Workflow

1. **Add Files:**
   - Click "Add .mat File" to select individual files
   - OR Click "Scan Folder" to auto-detect all .mat files in workspace

2. **Run Analysis:**
   - Click "▶ RUN ANALYSIS" button
   - Watch the log for progress
   - Comparison metrics update automatically

3. **View Results:**
   - Click "View Results CSV" to open comparison_metrics.csv
   - Check individual participant folders in `processed_data/`

---

## 💻 Option 2: Terminal (Backup/Advanced)

### One-Time Setup

```bash
cd /home/ballistic/Documents/gsr_analysis2.0
source .venv/bin/activate
pip install -r requirements.txt
```

### Daily Workflow

```bash
# Activate venv (required every new terminal session)
source .venv/bin/activate

# Copy new .mat file to workspace (if not already there)
cp /path/to/newfile.mat .

# Option A: Process ONLY new files (faster) ⭐ RECOMMENDED
python run_incremental_analysis.py --config config.yaml

# Option B: Reprocess ALL files (slower)
python run_analysis.py --config config.yaml

# Option C: Force reprocess all (use with caution)
python run_incremental_analysis.py --config config.yaml --force
```

### Check Results

```bash
# List all processed participants
ls processed_data/

# View comparison metrics (updated automatically)
cat processed_data/summary/comparison_metrics.csv

# View specific participant results
cat processed_data/participant_001/metrics.json

# View plots
ls processed_data/participant_001/*.png
```

### Deactivate venv (when done)

```bash
deactivate
```

---

## 📊 Understanding File Processing

### How It Detects New Files

The incremental script checks if a `.mat` file has a corresponding processed output:

```
.mat file: "05-07-25 001,002 matlab.mat"
      ↓ (processed)
Output folder: "05_07_25_001_002_matlab_p1/"
              + metrics.json ✓ (complete processing)
```

If the output folder AND metrics.json exist → **File is skipped**
If missing → **File is processed**

---

## 🔧 Troubleshooting

### Venv not found
```bash
cd /home/ballistic/Documents/gsr_analysis2.0
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Want to force reprocess all files
```bash
# Terminal
python run_incremental_analysis.py --config config.yaml --force

# GUI
Just click "Run Analysis" and it will detect new files automatically
```

### Need to modify filter settings
Edit `config.yaml`:
```yaml
lowpass_hz: 1.0          # Adjust low-pass filter
rapid_change_thresh: 5.0  # Artifact detection threshold
min_conductance: 0.1      # Min valid GSR value
max_conductance: 25.0     # Max valid GSR value
```

Then re-run analysis (new results will overwrite old ones).

---

## 📈 Comparison Metrics Update

**Automatic:** Both `run_analysis.py` and `run_incremental_analysis.py` automatically:
1. Generate `processed_data/summary/comparison_metrics.csv`
2. Include ALL participants found in `processed_data/`
3. Update on every run

You don't need to manually add metrics—it's automatic!

---

## 🎯 Recommended Workflow

### For First Run
```bash
source .venv/bin/activate
python gui_analysis.py    # Easier than terminal
```

### For Routine Analysis
```bash
source .venv/bin/activate
python gui_analysis.py    # Use GUI if available
# Or if terminal:
python run_incremental_analysis.py --config config.yaml
```

### For Batch Processing
```bash
# Put all .mat files in workspace, then:
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml
# Processes only new ones, very fast
```

---

## 📝 File Structure After Processing

```
processed_data/
├── participant_001/
│   ├── raw_data.csv              # Original GSR data
│   ├── tonic_component.csv        # Tonic (baseline) component
│   ├── phasic_component.csv       # Phasic (response) component
│   ├── metrics.json               # Quality metrics
│   ├── overview.png               # Plot: raw+filtered+components
│   ├── scr_peaks.png              # Plot: SCR peaks
│   └── quality_report.pdf         # Per-participant PDF report
│
├── participant_002/
│   └── [same structure as above]
│
└── summary/
    └── comparison_metrics.csv     # All participants aggregated
```

---

## 🆘 Getting Help

**In GUI:**
- Click "Terminal Instructions" button for quick reference

**In Terminal:**
```bash
python gui_analysis.py --help
python run_incremental_analysis.py --help
python run_analysis.py --help
```

**Check config:**
```bash
cat config.yaml
```

---

**Last Updated:** December 5, 2025
