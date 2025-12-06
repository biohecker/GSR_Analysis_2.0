# 📖 Documentation Index

Welcome! Here's everything you need to use your new analysis tools.

## 🚀 Start Here

### **New to the system?**
→ Read: [`QUICK_START.md`](QUICK_START.md) (5 minutes)

### **Want detailed guidance?**
→ Read: [`USAGE_GUIDE.md`](USAGE_GUIDE.md) (15 minutes)

### **Need command reference?**
→ Read: [`COMMANDS.md`](COMMANDS.md) (1 minute)

### **Curious what was built?**
→ Read: [`WHAT_I_BUILT.md`](WHAT_I_BUILT.md) (5 minutes)

---

## 📊 Quick Comparison

### Three Ways to Run Analysis

#### **1. GUI Application** ✨ (Easiest)
```bash
source .venv/bin/activate && python gui_analysis.py
```
- Visual interface, no terminal needed
- Auto-detects new files
- Shows processing log in real-time
- Best for: Beginners, visual learners

#### **2. Incremental Script** ⚡ (Fastest)
```bash
source .venv/bin/activate && python run_incremental_analysis.py --config config.yaml
```
- Processes only newly-detected `.mat` files by default (does not re-run existing participants)
- Much faster with many files
- Terminal-based, minimal overhead
- Best for: Power users, batch processing

#### **3. Original Script** (Simple)
```bash
source .venv/bin/activate && python run_analysis.py --config config.yaml
```
- Reprocesses all files
- Simplest workflow
- Slower but always updated
- Best for: First-time users

---

## ❓ Common Questions

### "Will it reprocess all files every time?"
**GUI & Incremental:** NO - only new files  
**Original:** YES - reprocesses all

See: [`USAGE_GUIDE.md` #1](USAGE_GUIDE.md)

### "Do I need venv every time?"
**YES** - but just one line: `source .venv/bin/activate`

See: [`QUICK_START.md`](QUICK_START.md)

### "Does comparison_metrics update automatically?"
**YES** - happens with every run, no manual steps

See: [`USAGE_GUIDE.md` #2](USAGE_GUIDE.md)

### "Do I need separate venv for plot_gsr?"
**NO** - one venv handles everything

See: [`USAGE_GUIDE.md` #3](USAGE_GUIDE.md)

### "What's the best workflow?"
**Recommended:**
1. GUI for interactive work
2. Incremental script for batch processing
3. Original script if you want simplicity

See: [`USAGE_GUIDE.md` #Workflow](USAGE_GUIDE.md)

---

## 📁 File Structure

```
/home/user/Documents/gsr_analysis2.0/

📄 Documentation (NEW)
├── README.md                      ← Pipeline technical details
├── QUICK_START.md                 ← Start here! (5 min)
├── USAGE_GUIDE.md                 ← Complete guide (15 min)
├── COMMANDS.md                    ← Cheat sheet
├── WHAT_I_BUILT.md                ← What's new
└── INDEX.md                       ← This file

⚙️ Scripts
├── gui_analysis.py                ← GUI app (NEW)
├── run_incremental_analysis.py     ← Smart script (NEW)
├── run_analysis.py                ← Original script
└── config.yaml                    ← Configuration

📦 Pipeline Code
└── eda_pipeline/
    ├── pipeline.py
    ├── filtering.py
    ├── decomposition.py
    ├── metrics.py
    ├── plotting.py
    ├── reporting.py
    └── ... (other modules)

💾 Data
├── *.mat                          ← Your MATLAB files
└── processed_data/
    ├── summary/
    │   └── comparison_metrics.csv  ← ALL results aggregated
    ├── participant_001/
    │   ├── raw_data.csv
    │   ├── tonic_component.csv
    │   ├── phasic_component.csv
    │   ├── metrics.json
    │   ├── overview.png
    │   ├── scr_peaks.png
    │   └── quality_report.pdf
    └── ... (more participants)
```

---

## 🎯 Your Workflow

### When you have a new .mat file:

**Option A: Use GUI** (Easiest)
```bash
source .venv/bin/activate
python gui_analysis.py
# Click buttons, watch it work!
```

**Option B: Use Terminal** (Fastest)
```bash
source .venv/bin/activate
cp /path/to/newfile.mat .
python run_incremental_analysis.py --config config.yaml
```

**Either way:**
- ✅ Only new files are analyzed
- ✅ Results are automatically added to comparison_metrics.csv
- ✅ PDFs and plots are generated
- ✅ No manual work needed

---

## 📚 Documentation Guide

| Document | Length | Best For |
|----------|--------|----------|
| **QUICK_START.md** | 5 min | Getting running immediately |
| **USAGE_GUIDE.md** | 15 min | Understanding the system |
| **COMMANDS.md** | Reference | Copy-paste commands |
| **WHAT_I_BUILT.md** | 5 min | Understanding what's new |
| **README.md** | 10 min | Pipeline technical details |

---

## ✨ Key Features

### All Tools Automatically:
- ✅ Detect .mat files
- ✅ Process them with your config settings
- ✅ Generate tonic/phasic decomposition
- ✅ Calculate quality metrics
- ✅ Create visualizations (plots + PDF)
- ✅ Update comparison_metrics.csv

### Smart Features (GUI & Incremental):
- ✅ Skip already-processed files (fast!)
- ✅ Show what will be processed
- ✅ Preserve existing results
- ✅ Option to force reprocess if needed

---

## 🆘 Troubleshooting

### GUI won't open
See: [`COMMANDS.md` #Troubleshooting](COMMANDS.md)

### Incremental script errors
See: [`USAGE_GUIDE.md` #Troubleshooting](USAGE_GUIDE.md)

### Venv issues
See: [`COMMANDS.md` #Venv Management](COMMANDS.md)

### Need to modify filters
See: [`COMMANDS.md` #Configuration](COMMANDS.md)

---

## 🚀 Quick Command Reference

```bash
# One-time setup
cd /home/ballistic/Documents/gsr_analysis2.0
source .venv/bin/activate
pip install -r requirements.txt

# Run GUI
python gui_analysis.py

# Run incremental (terminal)
python run_incremental_analysis.py --config config.yaml

# Check results
cat processed_data/summary/comparison_metrics.csv

# View specific participant
ls processed_data/participant_001/
cat processed_data/participant_001/metrics.json
```

---

## 📊 Output Files Explained

After analysis, you'll find:

**Per-participant folder** (`processed_data/participant_XXX/`):
- `raw_data.csv` - Original GSR signal (time_s, conductance_uS)
- `tonic_component.csv` - Baseline (time_s, tonic_uS)
- `phasic_component.csv` - Response (time_s, phasic_uS)
- `metrics.json` - Quality metrics
- `overview.png` - Raw + filtered + tonic + phasic plot
- `scr_peaks.png` - Phasic with peaks plot
- `quality_report.pdf` - PDF report with interpretation

**Summary file** (`processed_data/summary/comparison_metrics.csv`):
- One row per participant
- Columns: participant, tonic_level, tonic_range, tonic_slope, tonic_variability, scr_count, scr_frequency, scr_amplitude, artifact_percent, snr

---

## ✅ Everything's Ready

All tools are:
- ✅ Syntax validated
- ✅ Ready to use
- ✅ Fully documented
- ✅ No extra installation needed

**Next step:** Pick a document above and start!

---

## 💡 Recommended Reading Order

1. **First time?** → `QUICK_START.md`
2. **Want details?** → `USAGE_GUIDE.md`
3. **Just need commands?** → `COMMANDS.md`
4. **Curious about new stuff?** → `WHAT_I_BUILT.md`
5. **Need technical details?** → `README.md`

---

**Created:** December 5, 2025  
**Status:** ✅ Ready to Use
