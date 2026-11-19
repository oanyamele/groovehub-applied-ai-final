"""
Command line runner for the GrooveHUB Music Recommender.

Loads songs, generates recommendations for multiple user profiles,
displays formatted recommendation tables, evaluates reliability,
and records evaluation results in structured log files.
"""

import textwrap

from .recommender import (
    load_songs,
    recommend_songs,
    evaluate_recommendations,
)

from .evaluation_logger import log_evaluation


SCORING_MODE = "balanced"
RAG_ENABLED = True


def format_recommendations_table(recommendations: list) -> str:
    """Format ranked recommendations as a wrapped ASCII table."""

    headers = ("Rank", "Song", "Artist", "Score", "Reasons")
    widths = (4, 13, 10, 6, 30)

    border = "+" + "+".join(
        "-" * (width + 2) for width in widths
    ) + "+"

    def format_row(values: tuple, is_header: bool = False) -> list[str]:
        wrapped_cells = []

        for column_index, (value, width) in enumerate(
            zip(values, widths)
        ):
            cell_text = str(value).replace("\n", " ")

            if column_index == len(widths) - 1 and not is_header:
                reasons = [
                    reason.strip()
                    for reason in cell_text.split(";")
                ]

                wrapped = [
                    line
                    for reason in reasons
                    for line in (
                        textwrap.wrap(reason, width=width) or [""]
                    )
                ]
            else:
                wrapped = (
                    textwrap.wrap(cell_text, width=width) or [""]
                )

            wrapped_cells.append(wrapped)

        lines = []

        for line_index in range(
            max(len(cell) for cell in wrapped_cells)
        ):
            cells = [
                cell[line_index] if line_index < len(cell) else ""
                for cell in wrapped_cells
            ]

            lines.append(
                "| "
                + " | ".join(
                    cell.ljust(width)
                    for cell, width in zip(cells, widths)
                )
                + " |"
            )

        return lines

    table_lines = [
        border,
        *format_row(headers, is_header=True),
        border,
    ]

    for rank, (song, score, explanation) in enumerate(
        recommendations, start=1
    ):
        table_lines.extend(
            format_row(
                (
                    rank,
                    song["title"],
                    song["artist"],
                    f"{score:.2f}",
                    explanation,
                )
            )
        )

        table_lines.append(border)

    return "\n".join(table_lines)


def display_reliability_evaluation(
    recommendations: list,
    mode: str,
    profile_name: str,
) -> None:
    """
    Evaluate recommendations, display reliability results,
    and save the evaluation to the log.
    """

    evaluation = evaluate_recommendations(
        recommendations,
        mode=mode,
        rag_enabled=RAG_ENABLED,
    )

    print("\nReliability Evaluation:")

    status = "PASS" if evaluation.passed else "FAIL"

    print(f"Status: {status}")

    print(
        f"Reliability Score: {evaluation.reliability_score}%"
    )

    print(
        f"Checks Passed: "
        f"{evaluation.checks_passed}/{evaluation.total_checks}"
    )

    if evaluation.issues:
        print("\nIssues:")

        for issue in evaluation.issues:
            print(f"- {issue}")

    if evaluation.warnings:
        print("\nWarnings:")

        for warning in evaluation.warnings:
            print(f"- {warning}")

    if not evaluation.issues and not evaluation.warnings:
        print("No issues or warnings detected.")

    # Record evaluation results in the structured JSONL log.
    log_evaluation(
        profile_name=profile_name,
        scoring_mode=mode,
        evaluation=evaluation,
        recommendation_count=len(recommendations),
    )

    print(
        "Evaluation results saved to "
        "logs/evaluation_results.jsonl"
    )

    print("-" * 60)


def main() -> None:
    """Run the GrooveHUB recommendation and evaluation workflow."""

    songs = load_songs("data/songs.csv")

    print(f"Loaded {len(songs)} songs.")
    print(f"Scoring mode: {SCORING_MODE}")

    profiles = [
        (
            "High-Energy Pop",
            {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 0.9,
            },
        ),
        (
            "Chill Lofi",
            {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.3,
            },
        ),
        (
            "Intense Rock",
            {
                "favorite_genre": "rock",
                "favorite_mood": "intense",
                "target_energy": 0.95,
            },
        ),
    ]

    for profile_name, user_prefs in profiles:

        # Generate recommendations.
        recommendations = recommend_songs(
            user_prefs,
            songs,
            k=5,
            mode=SCORING_MODE,
            rag_enabled=RAG_ENABLED,
        )

        # Display recommendation results.
        print(f"\n{profile_name} - Top 5 recommendations:")
        print(format_recommendations_table(recommendations))

        # Evaluate and log recommendation reliability.
        display_reliability_evaluation(
            recommendations,
            mode=SCORING_MODE,
            profile_name=profile_name,
        )


if __name__ == "__main__":
    main()
