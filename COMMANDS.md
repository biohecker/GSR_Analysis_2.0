# Command Reference Card

## TL;DR - Copy & Paste Commands

### First Time Setup
```bash
cd /home/ballistic/Documents/gsr_analysis2.0
source .venv/bin/activate
pip install -r requirements.txt
```

### Daily Use

#### GUI Version (Recommended)
```bash
source .venv/bin/activate
python gui_analysis.py
```

#### Terminal: Process Only New Files (Fast!)
```bash
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml
```
- Processes only newly-detected `.mat` files and preserves existing outputs
- Appends new participant rows to `processed_data/summary/comparison_metrics.csv`
- Use `--force` to reprocess everything if required

#### Terminal: Reprocess All Files
```bash
source .venv/bin/activate
python run_analysis.py --config config.yaml
```

#### Terminal: Force Reprocess Everything
```bash
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml --force
```

---

## File Management

### Add a New .mat File
```bash
# From anywhere, copy to workspace:
cp /path/to/file.mat /home/ballistic/Documents/gsr_analysis2.0/
```

### List All .mat Files in Workspace
```bash
ls -lh *.mat
```

### List All Processed Participants
```bash
ls processed_data/
```

### View Comparison Metrics
```bash
cat processed_data/summary/comparison_metrics.csv
```

### View Single Participant Results
```bash
# List what's available
ls processed_data/participant_001/

# View metrics
cat processed_data/participant_001/metrics.json

# View data
head processed_data/participant_001/raw_data.csv
```

---

## Venv Management

### Activate
```bash
source .venv/bin/activate
```

### Deactivate
```bash
deactivate
```

### Check Current Environment
```bash
which python
python --version
```

### Reinstall Dependencies
```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## Configuration

### View Current Config
```bash
cat config.yaml
```

### Edit Config (e.g., change filters)
```bash
nano config.yaml
# or
vim config.yaml
```

### Common Config Changes
```yaml
# Lower = more aggressive filtering
lowpass_hz: 1.0

# Artifact detection threshold (µS/s)
rapid_change_thresh: 5.0

# Valid GSR range (µS)
min_conductance: 0.1
max_conductance: 25.0

# Output directory
output_dir: "/home/ballistic/Documents/gsr_analysis2.0/processed_data"
```

---

## Troubleshooting

### Pipeline Won't Start
```bash
# Check if venv exists
ls -la .venv/bin/activate

# If not, create it
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Missing Dependencies
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Permission Denied
```bash
chmod +x gui_analysis.py run_incremental_analysis.py run_analysis.py
```

### Show Detailed Analysis Output
```bash
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml -v
```

---

## Script Comparison

| Feature | `gui_analysis.py` | `run_incremental_analysis.py` | `run_analysis.py` |
|---------|------------------|-------------------------------|------------------|
| GUI Interface | ✅ | ❌ | ❌ |
| Process New Files Only | ✅ | ✅ | ❌ |
| Reprocess All | ✅ | Optional (--force) | ✅ |
| Auto-Update Metrics | ✅ | ✅ | ✅ |
| Venv Handling | Automatic | Manual | Manual |
| Learning Curve | Easiest | Medium | Easy |
| Speed | Fast | Fastest | Slower |

---

## Output Files Explained

```
processed_data/
├── summary/
│   └── comparison_metrics.csv
│       └─ Columns: participant, tonic_level, tonic_range, 
│          tonic_slope, tonic_variability, scr_count, 
│          scr_frequency, scr_amplitude, artifact_percent, snr
│
├── participant_001/
│   ├── raw_data.csv
│   │   └─ Columns: time_s, conductance_uS
│   ├── tonic_component.csv
│   │   └─ Columns: time_s, tonic_uS
│   ├── phasic_component.csv
│   │   └─ Columns: time_s, phasic_uS
│   ├── metrics.json
│   │   └─ JSON with all quality metrics
│   ├── overview.png
│   │   └─ Plot: raw + filtered + tonic + phasic
│   ├── scr_peaks.png
│   │   └─ Plot: phasic with detected peaks
│   └── quality_report.pdf
│       └─ PDF report with interpretation
│
└── participant_002/
    └── [same as participant_001]
```

---

## Pro Tips

### 1. Batch Processing
```bash
# Add all .mat files to workspace first, then run once:
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml
# Only processes new ones!
```

### 2. Compare Before/After
```bash
# Before modifying config:
cp processed_data/summary/comparison_metrics.csv metrics_backup.csv

# Edit config.yaml...

# Reprocess:
source .venv/bin/activate
python run_incremental_analysis.py --config config.yaml --force

# Compare results
diff metrics_backup.csv processed_data/summary/comparison_metrics.csv
```

### 3. Monitor Progress
```bash
# In another terminal, watch results update
watch -n 2 'ls -lt processed_data/ | head'
```

### 4. Export Results for Analysis
```bash
# Copy all CSVs to analysis folder
mkdir analysis_export
cp processed_data/*/raw_data.csv analysis_export/
cp processed_data/summary/comparison_metrics.csv analysis_export/
```

---

## Emergency Restart

If something goes wrong:
```bash
# Clear and restart
cd /home/ballistic/Documents/gsr_analysis2.0
deactivate 2>/dev/null
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gui_analysis.py
```

---

**Last Updated:** December 5, 2025  
**Questions?** Check `USAGE_GUIDE.md` or `QUICK_START.md`
