import math
import csv
import json
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


RAG_DEFAULT_KNOWLEDGE_PATH = "data/music_knowledge.json"
RAG_MAX_BONUS = 0.50


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and convert numeric fields to numbers."""
    songs = []

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["popularity"] = int(row["popularity"])
            row["mood_tags"] = [tag.strip() for tag in row["mood_tags"].split("|") if tag.strip()]

            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])

            songs.append(row)

    return songs


class ScoringStrategy:
    """Shared weighted scoring for a song's core preferences."""
    genre_weight = 1.0
    mood_weight = 1.0
    energy_weight = 2.0

    def score_core(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        if song["genre"] == user_prefs["favorite_genre"]:
            score += self.genre_weight
            reasons.append(f"genre match (+{self.genre_weight:.1f})")

        if song["mood"] == user_prefs["favorite_mood"]:
            score += self.mood_weight
            reasons.append(f"mood match (+{self.mood_weight:.1f})")

        energy_points = self.energy_weight * (
            1.0 - abs(song["energy"] - user_prefs["target_energy"])
        )
        score += energy_points
        reasons.append(f"energy similarity (+{energy_points:.2f})")
        return score, reasons


class BalancedScoringStrategy(ScoringStrategy):
    """Use the project's current genre, mood, and energy weights."""


class GenreFirstScoringStrategy(ScoringStrategy):
    """Give genre matches more weight than mood or energy similarity."""
    genre_weight = 2.0
    mood_weight = 0.5
    energy_weight = 1.0


class EnergyFocusedScoringStrategy(ScoringStrategy):
    """Give energy similarity more weight than genre or mood matches."""
    genre_weight = 0.5
    mood_weight = 0.5
    energy_weight = 3.0


SCORING_STRATEGIES = {
    "balanced": BalancedScoringStrategy(),
    "genre-first": GenreFirstScoringStrategy(),
    "energy-focused": EnergyFocusedScoringStrategy(),
}


def _get_scoring_strategy(mode: str) -> ScoringStrategy:
    strategy_name = mode.strip().lower().replace("_", "-")
    strategy = SCORING_STRATEGIES.get(strategy_name)
    if strategy is None:
        valid_modes = ", ".join(SCORING_STRATEGIES)
        raise ValueError(f"Unknown scoring mode {mode!r}. Choose from: {valid_modes}.")
    return strategy


def _add_advanced_feature_scores(
    user_prefs: Dict,
    song: Dict,
    score: float,
    reasons: List[str],
) -> Tuple[float, List[str]]:
    """Apply the same bounded optional feature bonuses to every mode."""
    feature_weight = 0.25
    popularity = song.get("popularity")
    if popularity is not None:
        popularity_points = feature_weight * max(0.0, min(float(popularity), 100.0)) / 100.0
        score += popularity_points
        reasons.append(f"popularity prior (+{popularity_points:.2f})")

    desired_tags = user_prefs.get("desired_mood_tags") or []
    if isinstance(desired_tags, str):
        desired_tags = [desired_tags]
    song_tags = song.get("mood_tags") or []
    if isinstance(song_tags, str):
        song_tags = song_tags.split("|")
    desired_tags = {tag.strip().lower() for tag in desired_tags if tag.strip()}
    song_tags = {tag.strip().lower() for tag in song_tags if tag.strip()}
    if desired_tags and song.get("mood_tags") is not None:
        matched_tags = desired_tags & song_tags
        tag_points = feature_weight * len(matched_tags) / len(desired_tags)
        score += tag_points
        reasons.append(f"mood tags match ({len(matched_tags)}/{len(desired_tags)}, +{tag_points:.2f})")

    preferred_decade = user_prefs.get("preferred_release_decade")
    if preferred_decade is not None and song.get("release_decade") is not None:
        decade_points = feature_weight if song["release_decade"] == preferred_decade else 0.0
        score += decade_points
        reasons.append(f"release decade match (+{decade_points:.2f})")

    for preference_key, feature_key, reason_label in (
        ("target_acousticness", "acousticness", "acousticness similarity"),
        ("target_danceability", "danceability", "danceability similarity"),
    ):
        target_value = user_prefs.get(preference_key)
        feature_value = song.get(feature_key)
        if target_value is not None and feature_value is not None:
            similarity = max(0.0, 1.0 - abs(float(feature_value) - float(target_value)))
            feature_points = feature_weight * similarity
            score += feature_points
            reasons.append(f"{reason_label} (+{feature_points:.2f})")

    return score, reasons


def score_song(
    user_prefs: Dict,
    song: Dict,
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """Score a song using the selected core strategy and shared feature bonuses."""
    strategy = _get_scoring_strategy(mode)
    score, reasons = strategy.score_core(user_prefs, song)
    return _add_advanced_feature_scores(user_prefs, song, score, reasons)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    rag_enabled: bool = False,
    knowledge_path: str = RAG_DEFAULT_KNOWLEDGE_PATH,
) -> List[Tuple[Dict, float, str]]:
    """Return top-scoring songs with explanations and optional retrieved context."""
    _get_scoring_strategy(mode)

    retrieval = RetrievalResult(documents=[], query_terms=[])
    if rag_enabled:
        try:
            knowledge_documents = load_music_knowledge(knowledge_path)
            retrieval = retrieve_music_context(user_prefs, knowledge_documents, k=3)
        except ValueError:
            retrieval = RetrievalResult(documents=[], query_terms=[])

    remaining = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode=mode)
        if rag_enabled:
            score, reasons = apply_retrieved_context(
                user_prefs,
                song,
                retrieval,
                score,
                reasons,
            )
        remaining.append((song, score, reasons))

    recommendations = []
    selected_artists = set()
    repeat_artist_penalty = 0.25

    while remaining and len(recommendations) < max(k, 0):
        best_index = max(
            range(len(remaining)),
            key=lambda index: remaining[index][1]
            - (repeat_artist_penalty if remaining[index][0]["artist"] in selected_artists else 0.0),
        )
        song, base_score, reasons = remaining.pop(best_index)
        penalty = repeat_artist_penalty if song["artist"] in selected_artists else 0.0
        final_score = base_score - penalty
        if penalty:
            reasons.append(f"repeat artist penalty (-{penalty:.2f})")
        explanation = "; ".join(reasons)
        recommendations.append((song, final_score, explanation))
        selected_artists.add(song["artist"])

    return recommendations

@dataclass
class EvaluationResult:
    """Stores the results of recommendation reliability checks."""
    passed: bool
    reliability_score: float
    issues: List[str]
    warnings: List[str]
    checks_passed: int
    total_checks: int

def evaluate_recommendations(
    recommendations: List[Tuple[Dict, float, str]],
    mode: str = "balanced",
    rag_enabled: bool = False,
) -> EvaluationResult:
    """
    Evaluate recommendation quality using structural and scoring checks.
    """

    strategy = _get_scoring_strategy(mode)

    core_maximum = (
        strategy.genre_weight
        + strategy.mood_weight
        + strategy.energy_weight
    )

    maximum_score = core_maximum + 1.25
    if rag_enabled:
        maximum_score += RAG_MAX_BONUS

    issues = []
    warnings = []

    total_checks = 3
    checks_passed = 0

    # Check 1: Recommendations should not be empty.
    if recommendations:
        checks_passed += 1
    else:
        issues.append("No recommendations were generated.")

    # Check 2: Scores must be valid and within expected bounds.
    valid_scores = True

    for song, score, explanation in recommendations:
        if not isinstance(score, (int, float)):
            valid_scores = False
            issues.append("A recommendation contains a non-numeric score.")
            break

        if not math.isfinite(score):
            valid_scores = False
            issues.append("A recommendation contains an invalid score.")
            break

        if score < 0 or score > maximum_score + 1e-9:
            valid_scores = False
            issues.append(
                f"Score for {song.get('title', 'Unknown song')} "
                "is outside the expected range."
            )
            break

    if valid_scores and recommendations:
        checks_passed += 1

    # Check 3: Every recommendation should have an explanation.
    explanations_valid = all(
        isinstance(explanation, str) and explanation.strip()
        for _, _, explanation in recommendations
    )

    if explanations_valid and recommendations:
        checks_passed += 1
    else:
        issues.append("One or more recommendations lack explanations.")

    # Advisory check: identify repeated artists.
    artists = [
        song.get("artist")
        for song, _, _ in recommendations
    ]

    if len(artists) != len(set(artists)):
        warnings.append(
            "Some artists appear more than once in the recommendations."
        )

    reliability_score = (
        checks_passed / total_checks
    ) * 100

    return EvaluationResult(
        passed=checks_passed == total_checks,
        reliability_score=round(reliability_score, 2),
        issues=issues,
        warnings=warnings,
        checks_passed=checks_passed,
        total_checks=total_checks,
    )


def load_music_knowledge(json_path: str = RAG_DEFAULT_KNOWLEDGE_PATH) -> List[Dict]:
    """Load a custom music knowledge-base JSON list safely."""
    try:
        with open(json_path, "r", encoding="utf-8") as knowledge_file:
            documents = json.load(knowledge_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to load music knowledge base: {error}") from error

    if not isinstance(documents, list):
        raise ValueError("Music knowledge base must contain a JSON list.")

    valid_documents = []
    for document in documents:
        if not isinstance(document, dict):
            continue

        text_fields = ("id", "title", "genre", "mood", "description", "keywords")
        if not any(
            isinstance(document.get(field), str) and document[field].strip()
            for field in text_fields
        ):
            continue

        artists = document.get("artists", [])
        if artists is None:
            document = dict(document)
            document["artists"] = []
        elif not isinstance(artists, list):
            document = dict(document)
            document["artists"] = [str(artists)] if str(artists).strip() else []

        valid_documents.append(document)

    return valid_documents


@dataclass
class RetrievalResult:
    """Documents and matching terms retrieved for a music request."""
    documents: List[Dict]
    query_terms: List[str]


def _query_text(user_request: object) -> str:
    """Convert a request or profile dictionary into searchable text."""
    if isinstance(user_request, str):
        return user_request
    if not isinstance(user_request, dict):
        return ""

    for explicit_key in ("music_request", "query", "similar_to"):
        explicit_value = user_request.get(explicit_key)
        if explicit_value:
            if isinstance(explicit_value, list):
                return " ".join(str(item) for item in explicit_value)
            return str(explicit_value)

    parts = []
    for key in (
        "favorite_genre",
        "favorite_mood",
        "desired_mood_tags",
        "preferred_release_decade",
        "music_request",
        "query",
    ):
        value = user_request.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))

    if user_request.get("similar_to"):
        parts.append(str(user_request["similar_to"]))

    return " ".join(parts)


def retrieve_music_context(
    user_request: object,
    knowledge_documents: List[Dict],
    k: int = 3,
) -> RetrievalResult:
    """Retrieve relevant knowledge using a dependency-free weighted lexical search."""
    query = _query_text(user_request).lower()
    query_terms = [term for term in re.findall(r"[a-z0-9]+", query) if len(term) > 1]

    if not query_terms:
        return RetrievalResult(documents=[], query_terms=[])

    ranked = []
    stop_terms = {"music", "song", "songs", "artist", "artists", "similar", "listen", "play"}

    for document in knowledge_documents:
        searchable = " ".join(
            str(document.get(field, ""))
            for field in ("title", "genre", "artists", "mood", "description", "keywords")
        ).lower()

        score = 0.0
        for term in set(query_terms):
            if term in stop_terms:
                continue
            if term in searchable:
                score += 2.0 if term in re.findall(r"[a-z0-9]+", searchable) else 1.0

        if score > 0:
            ranked.append((score, document))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return RetrievalResult(
        documents=[document for _, document in ranked[:max(k, 0)]],
        query_terms=query_terms,
    )


def apply_retrieved_context(
    user_request: object,
    song: Dict,
    retrieval: RetrievalResult,
    score: float,
    reasons: List[str],
) -> Tuple[float, List[str]]:
    """Use retrieved context to add a bounded bonus and a visible explanation."""
    if not retrieval.documents:
        return score, reasons

    song_genre = str(song.get("genre", "")).lower()
    song_mood = str(song.get("mood", "")).lower()
    song_artist = str(song.get("artist", "")).lower()
    song_tags = {str(tag).lower() for tag in song.get("mood_tags", [])}

    context_matches = set()

    for document in retrieval.documents:
        genres = {str(document.get("genre", "")).lower()}
        moods = {str(document.get("mood", "")).lower()}
        artists = {str(artist).lower() for artist in document.get("artists", [])}
        keywords = set(re.findall(r"[a-z0-9]+", str(document.get("keywords", "")).lower()))

        if song_genre and song_genre in genres:
            context_matches.add("genre")
        if song_mood and song_mood in moods:
            context_matches.add("mood")
        if song_artist and song_artist in artists:
            context_matches.add("artist")
        if song_tags & keywords:
            context_matches.add("mood-tag")

    if not context_matches:
        return score, reasons

    bonus = RAG_MAX_BONUS * len(context_matches) / 4.0
    bonus = round(min(bonus, RAG_MAX_BONUS), 2)
    score += bonus
    matches_text = ", ".join(sorted(context_matches))
    reasons.append(f"retrieved context match ({matches_text}, +{bonus:.2f})")
    return score, reasons