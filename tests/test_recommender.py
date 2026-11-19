import re
from pathlib import Path
import pytest

from src.main import format_recommendations_table
from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    evaluate_recommendations,
    load_music_knowledge,
    retrieve_music_context,
    load_songs,
    recommend_songs,
    score_song,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_songs_penalizes_repeat_artists_when_alternatives_exist():
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    songs = [
        {"title": "Top", "artist": "Artist A", "genre": "pop", "mood": "happy", "energy": 0.8},
        {"title": "Near Top", "artist": "Artist A", "genre": "pop", "mood": "happy", "energy": 0.75},
        {"title": "Alternative", "artist": "Artist B", "genre": "pop", "mood": "happy", "energy": 0.72},
    ]

    results = recommend_songs(user_prefs, songs, k=3)

    assert len(results) == 3
    assert [song["title"] for song, _, _ in results] == ["Top", "Alternative", "Near Top"]
    assert results[0][1] == 4.0
    assert "genre match (+1.0)" in results[0][2]
    assert "mood match (+1.0)" in results[0][2]
    assert abs(results[2][1] - 3.65) < 1e-9
    assert "repeat artist penalty (-0.25)" in results[2][2]


def test_csv_advanced_features_are_valid_for_all_songs():
    csv_path = Path(__file__).parents[1] / "data" / "songs.csv"
    songs = load_songs(str(csv_path))

    assert len(songs) == 18
    for song in songs:
        assert 0 <= song["popularity"] <= 100
        assert re.fullmatch(r"\d{4}s", song["release_decade"])
        assert song["mood_tags"]
        assert 0.0 <= song["acousticness"] <= 1.0
        assert 0.0 <= song["danceability"] <= 1.0


def test_score_song_optional_advanced_preferences_are_bounded_and_explained():
    song = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "popularity": 80,
        "release_decade": "2020s",
        "mood_tags": ["euphoric", "uplifting"],
        "acousticness": 0.7,
        "danceability": 0.6,
    }
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "desired_mood_tags": ["euphoric", "relaxed"],
        "preferred_release_decade": "2020s",
        "target_acousticness": 0.7,
        "target_danceability": 0.9,
    }

    score, reasons = score_song(prefs, song)

    assert abs(score - 5.0) < 1e-9
    assert any("popularity prior (+0.20)" in reason for reason in reasons)
    assert any("mood tags match (1/2, +0.12)" in reason for reason in reasons)
    assert any("release decade match (+0.25)" in reason for reason in reasons)
    assert any("acousticness similarity (+0.25)" in reason for reason in reasons)
    assert any("danceability similarity (+0.17)" in reason for reason in reasons)


def test_score_song_works_when_optional_preferences_and_features_are_omitted():
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    song = {"genre": "pop", "mood": "happy", "energy": 0.8}

    score, reasons = score_song(prefs, song)

    assert score == 4.0
    assert len(reasons) == 3


def test_scoring_modes_use_distinct_core_weights_and_share_advanced_bonuses():
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
    }
    song = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.7,
        "popularity": 80,
        "release_decade": "2020s",
        "mood_tags": ["uplifting"],
        "acousticness": 0.4,
        "danceability": 0.8,
    }
    prefs.update(
        desired_mood_tags=["uplifting"],
        preferred_release_decade="2020s",
        target_acousticness=0.4,
        target_danceability=0.8,
    )

    balanced_score, balanced_reasons = score_song(prefs, song)
    genre_score, genre_reasons = score_song(prefs, song, mode="genre-first")
    energy_score, energy_reasons = score_song(prefs, song, mode="energy-focused")

    assert score_song(prefs, song, mode="balanced") == (balanced_score, balanced_reasons)
    assert "genre match (+2.0)" in genre_reasons
    assert "mood match (+0.5)" in genre_reasons
    assert "energy similarity (+0.80)" in genre_reasons
    assert "genre match (+0.5)" in energy_reasons
    assert "mood match (+0.5)" in energy_reasons
    assert "energy similarity (+2.40)" in energy_reasons
    assert energy_score != balanced_score
    for reason in (
        "popularity prior",
        "mood tags match",
        "release decade match",
        "acousticness similarity",
        "danceability similarity",
    ):
        assert any(reason in item for item in genre_reasons)
        assert any(reason in item for item in energy_reasons)


def test_recommend_songs_rejects_unknown_mode():
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    with pytest.raises(ValueError, match="Unknown scoring mode"):
        recommend_songs(user_prefs, [], mode="experimental")


def test_diversity_penalty_applies_in_every_scoring_mode():
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }
    songs = [
        {"title": "First", "artist": "Artist A", "genre": "pop", "mood": "happy", "energy": 0.8},
        {"title": "Repeat", "artist": "Artist A", "genre": "pop", "mood": "happy", "energy": 0.75},
        {"title": "Alternative", "artist": "Artist B", "genre": "pop", "mood": "happy", "energy": 0.72},
    ]

    for mode in ("balanced", "genre-first", "energy-focused"):
        results = recommend_songs(prefs, songs, k=3, mode=mode)
        assert results[1][0]["artist"] == "Artist B"
        repeated_result = next(result for result in results if result[0]["title"] == "Repeat")
        assert "repeat artist penalty (-0.25)" in repeated_result[2]


def test_recommendation_table_wraps_long_text_and_keeps_all_reasons():
    recommendations = [
        (
            {
                "title": "A Very Long Imaginary Song Title That Needs Wrapping",
                "artist": "An Artist Name That Is Also Quite Long",
            },
            4.27,
            "genre match (+1.0); mood match (+1.0); energy similarity (+1.84); "
            "popularity prior (+0.20); repeat artist penalty (-0.25)",
        )
    ]

    table = format_recommendations_table(recommendations)
    rows = table.splitlines()

    assert "Rank" in table and "Song" in table and "Artist" in table
    assert "Score" in table and "Reasons" in table
    assert all(len(row) < 80 for row in rows)
    assert "Very" in table and "Imaginary" in table
    assert "genre match (+1.0)" in table
    assert "mood match (+1.0)" in table
    assert "energy similarity (+1.84)" in table
    assert "popularity prior (+0.20)" in table
    assert "repeat artist penalty (-0.25)" in table
    assert "4.27" in table


def test_evaluation_passes_for_valid_recommendations():
    """Valid recommendations should pass all reliability checks."""

    recommendations = [
        (
            {
                "title": "Sunrise City",
                "artist": "Neon Echo",
            },
            4.04,
            "genre match; mood match; energy similarity",
        )
    ]

    result = evaluate_recommendations(recommendations)

    assert result.passed is True
    assert result.reliability_score == 100.0
    assert result.checks_passed == 3


def test_evaluation_fails_for_empty_recommendations():
    """An empty recommendation list should fail evaluation."""

    result = evaluate_recommendations([])

    assert result.passed is False
    assert result.reliability_score == 0.0
    assert "No recommendations were generated." in result.issues


def test_evaluation_fails_for_invalid_scores():
    """Scores outside the expected range should fail evaluation."""

    recommendations = [
        (
            {
                "title": "Test Song",
                "artist": "Test Artist",
            },
            100.0,
            "Test explanation",
        )
    ]

    result = evaluate_recommendations(recommendations)

    assert result.passed is False
    assert result.reliability_score < 100.0
    assert any(
        "outside the expected range" in issue
        for issue in result.issues
    )


def test_evaluation_fails_for_missing_explanations():
    """Recommendations must include meaningful explanations."""

    recommendations = [
        (
            {
                "title": "Test Song",
                "artist": "Test Artist",
            },
            3.0,
            "",
        )
    ]

    result = evaluate_recommendations(recommendations)

    assert result.passed is False
    assert any(
        "lack explanations" in issue
        for issue in result.issues
    )


def test_evaluation_warns_about_repeated_artists():
    """Repeated artists should generate an advisory warning."""

    recommendations = [
        (
            {"title": "Song One", "artist": "Artist A"},
            4.0,
            "Good energy match",
        ),
        (
            {"title": "Song Two", "artist": "Artist A"},
            3.0,
            "Good mood match",
        ),
    ]

    result = evaluate_recommendations(recommendations)

    assert result.passed is True
    assert any(
        "artists appear more than once" in warning
        for warning in result.warnings
    )


def test_rag_retrieves_pop_knowledge_from_user_request():
    documents = load_music_knowledge()
    retrieval = retrieve_music_context("uplifting pop for a happy workout", documents, k=3)

    assert retrieval.documents
    assert any(document["genre"] == "pop" for document in retrieval.documents)


def test_rag_retrieves_different_genres_and_artists():
    documents = load_music_knowledge()

    rock = retrieve_music_context("aggressive rock with Voltline", documents, k=3)
    jazz = retrieve_music_context("warm relaxed jazz", documents, k=3)

    assert any(document["genre"] == "rock" for document in rock.documents)
    assert any(document["genre"] == "jazz" for document in jazz.documents)
    assert any("Voltline" in document["artists"] for document in rock.documents)


def test_rag_returns_no_context_for_unmatched_request():
    documents = load_music_knowledge()
    retrieval = retrieve_music_context("polka underwater bagpipes", documents, k=3)

    assert retrieval.documents == []


def test_rag_context_increases_matching_song_score_and_explanation():
    documents = load_music_knowledge()
    songs = [
        {
            "title": "Sunrise City",
            "artist": "Neon Echo",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.82,
            "popularity": 82,
            "release_decade": "2020s",
            "mood_tags": ["uplifting", "euphoric", "bright"],
            "acousticness": 0.18,
            "danceability": 0.79,
        }
    ]
    profile = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "music_request": "uplifting pop for a happy workout",
    }

    baseline = recommend_songs(profile, songs, k=1, rag_enabled=False)
    rag = recommend_songs(profile, songs, k=1, rag_enabled=True)

    assert rag[0][1] > baseline[0][1]
    assert "retrieved context match" in rag[0][2]


def test_rag_no_context_falls_back_to_existing_scoring():
    songs = load_music_knowledge
    profile = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "music_request": "polka underwater bagpipes",
    }
    catalog = [
        {
            "title": "Sunrise City",
            "artist": "Neon Echo",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.82,
            "popularity": 82,
        }
    ]

    baseline = recommend_songs(profile, catalog, k=1, rag_enabled=False)
    rag = recommend_songs(profile, catalog, k=1, rag_enabled=True)

    assert rag[0][1] == baseline[0][1]


def test_rag_missing_knowledge_file_falls_back_to_baseline(tmp_path):
    profile = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.82,
        "music_request": "uplifting pop",
    }
    catalog = [{
        "title": "Sunrise City",
        "artist": "Neon Echo",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.82,
        "popularity": 82,
    }]

    baseline = recommend_songs(profile, catalog, k=1, rag_enabled=False)
    rag = recommend_songs(
        profile,
        catalog,
        k=1,
        rag_enabled=True,
        knowledge_path=str(tmp_path / "missing.json"),
    )

    assert rag == baseline


def test_rag_invalid_json_raises_value_error(tmp_path):
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError, match="Unable to load music knowledge base"):
        load_music_knowledge(str(invalid_file))


def test_rag_incorrect_json_structure_raises_value_error(tmp_path):
    incorrect_file = tmp_path / "incorrect.json"
    incorrect_file.write_text('{"documents": []}', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON list"):
        load_music_knowledge(str(incorrect_file))


def test_rag_empty_knowledge_base_retrieves_nothing(tmp_path):
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("[]", encoding="utf-8")

    documents = load_music_knowledge(str(empty_file))
    retrieval = retrieve_music_context("uplifting pop", documents)

    assert documents == []
    assert retrieval.documents == []


def test_rag_malformed_entries_are_filtered(tmp_path):
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text(
        '[null, 42, {}, {"genre":"pop","artists":"Neon Echo","keywords":"pop happy"}]',
        encoding="utf-8",
    )

    documents = load_music_knowledge(str(malformed_file))

    assert len(documents) == 1
    assert documents[0]["artists"] == ["Neon Echo"]


def test_rag_empty_and_invalid_queries_return_no_context():
    documents = load_music_knowledge()

    assert retrieve_music_context("", documents).documents == []
    assert retrieve_music_context(" - ", documents).documents == []
    assert retrieve_music_context(None, documents).documents == []
    assert retrieve_music_context(12345, documents).documents == []
    assert retrieve_music_context(["pop"], documents).documents == []
