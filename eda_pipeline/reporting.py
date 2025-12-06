from pathlib import Path
from typing import Dict

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


def save_quality_report(metrics: Dict, plots: Dict[Path, str], out_path: Path, interpretation: str, recommendations: str) -> None:
    """Persist a lightweight PDF report combining metrics and interpretation."""

    with PdfPages(out_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        lines = ["EDA Quality Report", ""]
        for k, v in metrics.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        lines.append("Interpretation:")
        lines.append(interpretation)
        lines.append("")
        lines.append("Recommendations:")
        lines.append(recommendations)
        ax.text(0.05, 0.95, "\n".join(lines), va="top", ha="left", wrap=True)
        pdf.savefig(fig)
        plt.close(fig)

        for path, title in plots.items():
            img = plt.imread(path)
            fig, ax = plt.subplots(figsize=(11, 4))
            ax.imshow(img)
            ax.axis("off")
            ax.set_title(title)
            pdf.savefig(fig)
            plt.close(fig)




