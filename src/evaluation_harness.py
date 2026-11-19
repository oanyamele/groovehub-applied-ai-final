"""
GrooveHUB Automated Evaluation Harness.

Evaluates multiple predefined user profiles using the existing
recommendation engine and reliability evaluation component.
"""

import sys

from .recommender import (
    load_songs,
    recommend_songs,
    evaluate_recommendations,
)


SCORING_MODE = "balanced"
RECOMMENDATION_COUNT = 5
RAG_ENABLED = True


# Predefined profiles used for repeatable evaluation.
TEST_PROFILES = [
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


def run_evaluation_harness() -> int:
    """Evaluate all predefined profiles and return an exit status."""

    print("=" * 55)
    print("GROOVEHUB AUTOMATED EVALUATION HARNESS")
    print("=" * 55)

    songs = load_songs("data/songs.csv")

    print(f"\nSongs loaded: {len(songs)}")
    print(f"Scoring mode: {SCORING_MODE}")
    print(f"RAG enabled: {RAG_ENABLED}")
    print(f"Profiles to evaluate: {len(TEST_PROFILES)}")

    results = []

    for profile_name, user_prefs in TEST_PROFILES:

        print(f"\nEvaluating: {profile_name}")
        print("-" * 40)

        try:
            recommendations = recommend_songs(
                user_prefs,
                songs,
                k=RECOMMENDATION_COUNT,
                mode=SCORING_MODE,
                rag_enabled=RAG_ENABLED,
            )

            evaluation = evaluate_recommendations(
                recommendations,
                mode=SCORING_MODE,
                rag_enabled=RAG_ENABLED,
            )

            correct_count = (
                len(recommendations) == RECOMMENDATION_COUNT
            )

            passed = evaluation.passed and correct_count

            results.append(passed)

            print(
                f"Recommendations generated: "
                f"{len(recommendations)}/{RECOMMENDATION_COUNT}"
            )

            print(
                f"Reliability score: "
                f"{evaluation.reliability_score:.2f}%"
            )

            print(
                f"Checks passed: "
                f"{evaluation.checks_passed}/"
                f"{evaluation.total_checks}"
            )

            print(
                f"Profile result: "
                f"{'PASS' if passed else 'FAIL'}"
            )

            for issue in evaluation.issues:
                print(f"ISSUE: {issue}")

            for warning in evaluation.warnings:
                print(f"WARNING: {warning}")

            if not correct_count:
                print(
                    "ISSUE: Expected exactly "
                    f"{RECOMMENDATION_COUNT} recommendations."
                )

        except Exception as error:
            results.append(False)
            print(f"Profile result: FAIL")
            print(f"ERROR: {error}")

    # Calculate overall evaluation results.
    total = len(results)
    passed_count = sum(results)
    failed_count = total - passed_count

    success_rate = (
        (passed_count / total) * 100
        if total else 0.0
    )

    print("\n" + "=" * 55)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 55)

    print(f"Profiles evaluated: {total}")
    print(f"Profiles passed:    {passed_count}")
    print(f"Profiles failed:    {failed_count}")
    print(f"Overall success:    {success_rate:.2f}%")

    overall_passed = total > 0 and failed_count == 0

    print(
        "\nOVERALL RESULT: "
        f"{'PASS' if overall_passed else 'FAIL'}"
    )

    print("=" * 55)

    return 0 if overall_passed else 1


if __name__ == "__main__":
    sys.exit(run_evaluation_harness())

