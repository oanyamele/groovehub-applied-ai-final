
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Create logs directory automatically
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Evaluation results stored as JSON Lines
EVALUATION_FILE = LOG_DIR / "evaluation_results.jsonl"

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "application.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def log_evaluation(
    profile_name: str,
    scoring_mode: str,
    evaluation: Any,
    recommendation_count: int,
) -> Dict:
    """
    Record a recommendation evaluation result.

    Each evaluation is stored as a separate JSON line.
    """

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profile": profile_name,
        "scoring_mode": scoring_mode,
        "recommendation_count": recommendation_count,
        "passed": evaluation.passed,
        "reliability_score": evaluation.reliability_score,
        "checks_passed": evaluation.checks_passed,
        "total_checks": evaluation.total_checks,
        "issues": evaluation.issues,
        "warnings": evaluation.warnings,
    }

    try:
        with open(EVALUATION_FILE, "a", encoding="utf-8") as file:
            file.write(json.dumps(result) + "\n")

        logger.info(
            "Evaluation recorded for %s: %.2f%% reliability",
            profile_name,
            evaluation.reliability_score,
        )

    except OSError:
        logger.exception("Failed to save evaluation result")
        raise

    return result

