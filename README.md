GSR Analysis 2.0
===============

Quick start
-----------
- Create and activate a virtualenv:

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- Put your `.mat` files into the `data/` folder (project root).

- Run the incremental processor (recommended):

  ```bash
  python run_incremental_analysis.py
  ```

  This will process only new `.mat` files and append/update `processed_data/summary/comparison_metrics.csv`.

- Or run the full pipeline:

  ```bash
  python run_analysis.py
  ```

GUI
---
- Run the lightweight Tkinter GUI with:

  ```bash
  python gui_analysis.py
  ```

- The GUI reads `config.yaml` for `data_dir` and `processed_dir`. By default `data_dir` is `./data`.

Virtual environment notes
-------------------------
- A single virtualenv is sufficient for both plotting and analysis. Activate `.venv` before running any scripts.

What to upload to Git
---------------------
- Commit code, scripts, and documentation only. Recommended tracked files:
  - All `.py` source files in the repo root and `eda_pipeline/`
  - `requirements.txt`, `config.yaml`, and documentation files (`README.md`, `QUICK_START.md`, etc.)

- Do NOT commit large data or generated outputs. The repository includes a `.gitignore` that excludes:
  - `.venv/`, `data/`, and `processed_data/`
  - Generated plots, pickles, and large `.mat` files.

Preparing this repository for Git (local steps)
----------------------------------------------
1. Initialize a local repo (if you haven't already):

   ```bash
   git init
   git add .
   git commit -m "Initial import: analysis pipeline and docs"
   ```

2. If you plan to push to a remote Git hosting service, create the remote and add it:

   ```bash
   git remote add origin <your-remote-url>
   git branch -M main
   git push -u origin main
   ```

3. To avoid accidentally committing data files that are currently tracked, check:

   ```bash
   git status --ignored
   ```

Cleaning up accidental data commits (if needed)
----------------------------------------------
- If you accidentally committed data files, remove them and create a clean commit:

  ```bash
  git rm --cached path/to/large_file.mat
  git commit -m "Remove large data files from history"
  ```

Notes
-----
- Use `run_incremental_analysis.py` for day-to-day additions; it uses sanitized participant labels to avoid reprocessing.
- `gui_analysis.py` is a convenience front-end that copies selected `.mat` files into `data/` and invokes the pipeline.
- If you want help pushing to a remote or creating a GitHub repository, tell me the hosting provider and I'll give exact commands.
