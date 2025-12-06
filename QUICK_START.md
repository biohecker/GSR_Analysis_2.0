# ⚡ Quick Start Guide

## 🎯 Your Answer

**Current behavior:** `run_analysis.py` reprocesses ALL `.mat` files every time.  
**Better option:** Use `run_incremental_analysis.py` to process ONLY new files — it now analyzes only newly-detected `.mat` files and preserves existing outputs unless you explicitly force a re-run.

---

## 🚀 Get Started Now (5 minutes)

### Step 1: Open Terminal
```bash
cd /home/ballistic/Documents/gsr_analysis2.0
```

### Step 2: Activate Virtual Environment
```bash
source .venv/bin/activate
```
*(You need this in every new terminal session)*

### Step 3: Choose Your Path

#### **Option A: GUI (Easiest)** ✨
```bash
python gui_analysis.py
```
Then:
1. Click "Scan Folder" to find all `.mat` files
2. Click "▶ RUN ANALYSIS"
3. Watch the log
4. Done! Results auto-update

#### **Option B: Terminal (Fast)** ⚡
```bash
python run_incremental_analysis.py --config config.yaml
```
- Processes only NEW `.mat` files by default and appends their metrics to the summary
- Does NOT re-run processing for previously-processed participants (faster and preserves outputs)
- Use `--force` to reprocess all files if you need a full recompute

#### **Option C: Terminal (Reprocess All)**
```bash
python run_analysis.py --config config.yaml
```
- Reprocesses everything
- Slower but ensures latest results

---

## 📊 What Gets Updated Automatically

After running either script:
- ✅ `processed_data/comparison_metrics.csv` → Updated with new data
- ✅ Individual participant folders → Created/updated
- ✅ All plots and reports → Generated

**No manual steps needed!**

---

## 🔄 Your Workflow (After First Run)

### When you get a new `.mat` file:

```bash
# Option 1: GUI (easiest)
source .venv/bin/activate
python gui_analysis.py
# Add file → Click Run → Done!

# Option 2: Terminal
source .venv/bin/activate
cp /path/to/newfile.mat .
python run_incremental_analysis.py --config config.yaml

# Check results
cat processed_data/summary/comparison_metrics.csv
```

---

## 📁 Where Are My Results?

```
processed_data/
├── summary/
│   └── comparison_metrics.csv    ← All participants aggregated
├── participant_001/
│   ├── raw_data.csv              ← Original GSR signal
│   ├── tonic_component.csv        ← Baseline component
│   ├── phasic_component.csv       ← Response component
│   ├── metrics.json               ← Quality metrics
│   ├── overview.png               ← Plots
│   └── quality_report.pdf         ← PDF report
└── participant_002/
    └── [same structure]
```

---

## ✅ Comparison Metrics AUTO-UPDATE

You DON'T need to:
- ❌ Manually add metrics
- ❌ Run a separate script
- ❌ Edit CSV files

It happens automatically when you run analysis!

---

## 🆘 Quick Troubleshooting

### "ModuleNotFoundError"
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "VirtualenvNotFound"
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### "I want to force reprocess all files"
```bash
python run_incremental_analysis.py --config config.yaml --force
```

### "Show me terminal instructions in the GUI"
Click **"Terminal Instructions"** button in GUI

---

## 📖 Full Documentation

See `USAGE_GUIDE.md` for:
- Detailed explanations
- Advanced options
- Configuration tips
- Troubleshooting guide

---

## 🎓 How It Detects New Files

The incremental script checks:
```
New file? → Look for processed_data/participant_XXX/metrics.json
  ├─ Found → Skip (already processed)
  └─ Not found → Process it!
```

Result: **Only new files get analyzed** → ⚡ Fast!

---

**Ready to go?** Start with Option A (GUI) or Option B (Terminal)!
