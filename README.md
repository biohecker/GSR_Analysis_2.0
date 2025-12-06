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