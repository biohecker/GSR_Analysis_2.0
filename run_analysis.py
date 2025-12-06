import argparse
from pathlib import Path

from eda_pipeline.config import EDAConfig
from eda_pipeline.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Process EDA MAT files into tonic/phasic components with quality reports.")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"), help="Path to YAML config.")
    args = parser.parse_args()

    cfg = EDAConfig.from_yaml(args.config)
    run_pipeline(cfg)


if __name__ == "__main__":
    main()




