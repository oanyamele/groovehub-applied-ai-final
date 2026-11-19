# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

GrooveHUB ranks songs using a user's preferred genre, mood, and target energy, with optional preferences for mood tags, release decade, acousticness, and danceability. It supports three scoring strategies, popularity and feature bonuses, a repeat-artist penalty, and optional lexical retrieval from a custom music knowledge base. The scoring remains deterministic and each recommendation explains its score.

---

## How The System Works

Current music recommendation systems like Spotify, use information like listening history, likes, skips, playlists, and song characteristics to suggest music that users may enjoy. Some systems also use listening patterns from other users with similar tastes. 

Initial Algorithm Recipe (historical core-only version):
My recommender will compare each song with the user's preferences and calculate a relevance score. It will award 2.0 points for an exact genre match, 1.0 point for an exact mood match, and up to 1.0 point for energy similarity. Energy similarity is calculated by subtracting the absolute difference between the song's energy and the user's target energy from 1. The system will record reasons for each score, rank songs from highest to lowest, and return the top five recommendations.

Potential Bias:
Genre receives more points than mood, so songs in the preferred genre may rank higher even when other songs better match the user's mood and energy. The dataset is small and has an uneven distribution of genres, which may limit recommendation variety. The system also does not explicitly promote diversity in its results.

Current Scoring and Ranking:
The balanced strategy awards 1.0 point for an exact genre match, 1.0 point for an exact mood match, and up to 2.0 points for energy similarity: 2 × (1 − |song energy − target energy|). A popularity prior can add up to 0.25 points. Supplied preferences can add bounded bonuses for mood tags, release decade, acousticness, and danceability. Genre-First and Energy-Focused strategies change the core weights. Optional RAG retrieves up to three documents using lexical keyword matching and can add up to 0.50 points for matching genre, mood, artist, or mood tags. The ranker applies a 0.25-point repeat-artist penalty as recommendations are selected. Missing or invalid knowledge-base data falls back to baseline scoring.

Current Limitations:
Energy can contribute as much as the genre and mood matches combined, so songs with similar energy can rank highly even when their genre or mood is different. The dataset contains only 18 songs, and most genres appear only once, which limits variety. The repeat-artist penalty encourages diversity but does not guarantee it, and the scorer does not penalize genre or mood mismatches. These limitations could lead to recommendations that do not fully reflect a user's preferences.

Each Song in my simulation will use the following features from the dataset:
- ID: A unique identifier for each song.
- Title: The name of the song.
- Artist: The artist who performs the song.
- Genre: The music category, such as pop, rock, lofi, or jazz.
- Mood: The song's mood, such as happy, chill, intense, or relaxed.
- Energy: A numerical value from 0.0 to 1.0 representing the song's energy.
- Tempo (BPM): The song's speed in beats per minute.
- Valence: A numerical feature representing how positive or happy the music sounds.
- Danceability: A numerical feature representing how suitable the music is for dancing.
- Acousticness: A numerical feature representing how acoustic the music sounds.
- Popularity: An illustrative score from 0 to 100.
- Release decade: An illustrative decade label, such as `1990s` or `2020s`.
- Mood tags: Multiple descriptive tags separated by `|` in the CSV.

The popularity, release-decade, mood-tag, acousticness, and danceability values in this small dataset are simulated for this project. They are not real-world measured or verified values.

The UserProfile will contain:
- Favorite genre: The user's preferred music genre.
- Favorite mood: The mood the user wants to listen to.
- Target energy: The user's preferred energy level, from 0.0 to 1.0.
- Optional preferences: `desired_mood_tags`, `preferred_release_decade`, `target_acousticness`, and `target_danceability` can further customize matches.



Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

---

## Getting Started

### Setup

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main
   ```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

The following terminal output is a historical snapshot from earlier core-only scoring runs. Current scores and rankings may differ because the implementation now includes advanced bonuses, artist diversity, selectable scoring modes, and optional RAG.

```
Initial Terminal Output:
python -m src.main
Loaded 18 songs.

Top 5 recommendations:

1. Sunrise City - Neon Echo
   Score: 3.98
   Why: genre match (+2.0); mood match(+1.0); energy similarity (+0.98)

2. Gym Hero - Max Pulse
   Score: 2.87
   Why: genre match (+2.0); energy similarity (+0.87)

3. Rooftop Lights - Indigo Parade
   Score: 1.96
   Why: mood match (+1.0); energy similarity (+0.96)

4. Saturday Static - The Brass Comets
   Score: 0.99
   Why: energy similarity (+0.99)

5. Paper Moon Fiesta - Luna Mar Azul
   Score: 0.97
   Why: energy similarity (+0.97)

Updated Terminal Output:
python -m src.main
Loaded 18 songs.

High-Energy Pop - Top 5 recommendations:

1. Sunrise City - Neon Echo
   Score: 3.84
   Why: genre match (+1.0); mood match (+1.0); energy similarity (+1.84)

2. Gym Hero - Max Pulse
   Score: 2.94
   Why: genre match (+1.0); energy similarity (+1.94)

3. Rooftop Lights - Indigo Parade
   Score: 2.72
   Why: mood match (+1.0); energy similarity (+1.72)

4. Storm Runner - Voltline
   Score: 1.98
   Why: energy similarity (+1.98)

5. Iron Orchard - Blackglass Harbor
   Score: 1.90
   Why: energy similarity (+1.90)

Chill Lofi - Top 5 recommendations:

1. Library Rain - Paper Lanterns
   Score: 3.90
   Why: genre match (+1.0); mood match (+1.0); energy similarity (+1.90)

2. Midnight Coding - LoRoom
   Score: 3.76
   Why: genre match (+1.0); mood match (+1.0); energy similarity (+1.76)

3. Spacewalk Thoughts - Orbit Bloom
   Score: 2.96
   Why: mood match (+1.0); energy similarity (+1.96)

4. Focus Flow - LoRoom
   Score: 2.80
   Why: genre match (+1.0); energy similarity (+1.80)

5. Field of Lanterns - Rowan Bell
   Score: 1.94
   Why: energy similarity (+1.94)

Intense Rock - Top 5 recommendations:

1. Storm Runner - Voltline
   Score: 3.92
   Why: genre match (+1.0); mood match (+1.0); energy similarity (+1.92)

2. Gym Hero - Max Pulse
   Score: 2.96
   Why: mood match (+1.0); energy similarity (+1.96)

3. Iron Orchard - Blackglass Harbor
   Score: 2.00
   Why: energy similarity (+2.00)

4. Sunrise City - Neon Echo
   Score: 1.74
   Why: energy similarity (+1.74)

5. Saturday Static - The Brass Comets
   Score: 1.72
   Why: energy similarity (+1.72)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

Historical Profile Evaluation (core-only terminal output):
python -m src.main
Loaded 18 songs.

High-Energy Pop - Top 5 recommendations:

1. Sunrise City - Neon Echo
   Score: 3.92
   Why: genre match (+2.0); mood match (+1.0); energy similarity (+0.92)

2. Gym Hero - Max Pulse
   Score: 2.97
   Why: genre match (+2.0); energy similarity (+0.97)

3. Rooftop Lights - Indigo Parade
   Score: 1.86
   Why: mood match (+1.0); energy similarity (+0.86)

4. Storm Runner - Voltline
   Score: 0.99
   Why: energy similarity (+0.99)

5. Iron Orchard - Blackglass Harbor
   Score: 0.95
   Why: energy similarity (+0.95)

Chill Lofi - Top 5 recommendations:

1. Library Rain - Paper Lanterns
   Score: 3.95
   Why: genre match (+2.0); mood match (+1.0); energy similarity (+0.95)

2. Midnight Coding - LoRoom
   Score: 3.88
   Why: genre match (+2.0); mood match (+1.0); energy similarity (+0.88)

3. Focus Flow - LoRoom
   Score: 2.90
   Why: genre match (+2.0); energy similarity (+0.90)

4. Spacewalk Thoughts - Orbit Bloom
   Score: 1.98
   Why: mood match (+1.0); energy similarity (+0.98)

5. Field of Lanterns - Rowan Bell
   Score: 0.97
   Why: energy similarity (+0.97)

Intense Rock - Top 5 recommendations:

1. Storm Runner - Voltline
   Score: 3.96
   Why: genre match (+2.0); mood match (+1.0); energy similarity (+0.96)

2. Gym Hero - Max Pulse
   Score: 1.98
   Why: mood match (+1.0); energy similarity (+0.98)

3. Iron Orchard - Blackglass Harbor
   Score: 1.00
   Why: energy similarity (+1.00)

4. Sunrise City - Neon Echo
   Score: 0.87
   Why: energy similarity (+0.87)

5. Saturday Static - The Brass Comets
   Score: 0.86
   Why: energy similarity (+0.86)


Initial Profile Evaluation:

I tested three profiles: High-Energy Pop, Chill Lofi, and Intense Rock. The results generally matched my expectations. High-Energy Pop ranked "Sunrise City" first, Chill Lofi ranked "Library Rain" first, and Intense Rock ranked "Storm Runner" first. The High-Energy Pop profile also ranked "Gym Hero" highly, even though its mood is intense rather than happy. This happens because genre is worth 2 points and energy similarity can contribute nearly another point. For Chill Lofi, "Library Rain" ranked above "Midnight Coding" because both songs match genre and mood, but "Library Rain" has energy closer to the target of 0.3. For Intense Rock, "Storm Runner" ranked first because it matches both genre and mood while having energy close to 0.95. These results show that the recommender responds to changes in user preferences, but a song can still rank highly without matching every preference. The algorithm uses fixed weights and does not explicitly promote variety.

Updated:
I changed the genre weight from 2 points to 1 point and doubled the energy similarity weight so that it could contribute up to 2 points. The mood weight remained at 1 point. I reran the recommender for High-Energy Pop, Chill Lofi, and Intense Rock. The top recommendation for each profile stayed the same: Sunrise City for High-Energy Pop, Library Rain for Chill Lofi, and Storm Runner for Intense Rock. However, the Chill Lofi ranking changed slightly. For the original weights, Focus Flow ranked third, and Spacewalk Thoughts ranked fourth. For the updated weights, Spacewalk Thoughts ranked third, and Focus Flow ranked fourth. Spacewalk Thoughts matches the preferred mood and has energy close to the target. Focus Flow matches the preferred genre but not the mood. Doubling the energy weight made Spacewalk Thoughts score higher. The experiment showed that changing the importance of different features can change rankings even when the song catalog stays the same. The updated results are consistent with the new scoring formula, but I cannot conclude that they are more accurate without comparing them with listeners' preferences.




---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

GrooveHUB uses a small catalog of only 18 songs, so it cannot represent the full range of musical tastes. It scores songs using genre, mood, and energy but does not use tempo, valence, danceability, or acousticness. Because the algorithm does not penalize mismatches, a song can rank highly even when it does not match the user's preferred mood or genre. Energy similarity can contribute up to two points, which may cause high-energy songs to appear in multiple profiles' recommendations. The system also lacks a diversity rule, so recommendations may become repetitive. These limitations mean that a high score does not necessarily guarantee that a listener will enjoy a song.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Working on GrooveHUB taught me that recommendation systems use scoring rules to rank items based on user preferences. I learned that changing the weights assigned to genre, mood, and energy can change the rankings even when the song catalog stays the same. I was surprised that songs such as Gym Hero could rank highly for different profiles because the algorithm rewards matching features without knocking mismatches. I also learned that a high recommendation score does not necessarily mean a listener will enjoy a song. A small dataset, unused musical features, and a lack of diversity rules can limit the quality of recommendations. Testing different profiles helped me understand why it is important to evaluate both the scoring formula and the actual results rather than assuming that an algorithm is accurate simply because it produces reasonable-looking rankings.


---

### Final Project Updated Music Recommender

This section documents the final implementation and additional features
developed after the initial project version.

---

Additional Features and Improvements

Since completing the initial recommendation algorithm, I have extended GrooveHUB with additional scoring strategies, advanced recommendation features, artist diversity controls, and recommendation reliability evaluation.

1. Advanced Scoring Features

The recommendation algorithm now considers additional song characteristics and user preferences beyond genre, mood, and energy.

The following optional features have been introduced:

- Popularity: Adds a small bonus based on a song's popularity score.
- Mood Tags: Rewards songs that share descriptive mood tags with the user's preferences.
- Release Decade: Adds a bonus when a song matches the user's preferred release decade.
- Acousticness: Measures similarity between the song's acousticness and the user's preferred acousticness.
- Danceability: Measures similarity between the song's danceability and the user's preferred danceability.

Each optional feature can contribute up to 0.25 points to a song's score. These bonuses are bounded to prevent optional preferences from overwhelming the core recommendation criteria.

These features are illustrative and use simulated dataset values rather than verified listening or streaming data.

2. Multiple Scoring Strategies

I introduced three different scoring strategies to experiment with how different weight combinations influence recommendation results.

Scoring Strategy	Genre Weight	Mood Weight	Energy Weight
Balanced	1.0	1.0	2.0
Genre-First	2.0	0.5	1.0
Energy-Focused	0.5	0.5	3.0

All three strategies use the same optional feature bonuses, allowing the core scoring weights to be compared independently.

The scoring strategy can be selected using the mode parameter when calling recommend_songs().

For example:

python
recommendations = recommend_songs(
    user_prefs,
    songs,
    k=5,
    mode="genre-first"
)


The available modes are:

- balanced
- genre-first
- energy-focused

The system also validates the selected mode and raises a ValueError if an unsupported strategy is provided.

3. Recommendation Diversity

I introduced a repeat-artist penalty to encourage greater variety in the recommendations.

When a song by an artist has already been selected, subsequent songs by that same artist receive a 0.25-point penalty.

This encourages the recommender to consider songs from different artists when suitable alternatives are available.

The penalty is applied consistently across all three scoring strategies.

However, the system does not completely prevent repeated artists. If an artist's songs continue to score highly, they may still appear more than once.

4. Recommendation Reliability Evaluation

I added an evaluation component to assess the reliability of the generated recommendations.

The evaluation checks three areas:

Recommendation availability: Checks that recommendations have been generated.
Score validity: Checks that recommendation scores are numeric, finite, and within the expected scoring range.
Explanation availability: Checks that every recommendation includes a non-empty explanation.

Each successful check contributes to the overall reliability score.

The reliability percentage is calculated as:

python
reliability_score = (
    checks_passed / total_checks
) * 100


The evaluation also identifies repeated artists and reports them as warnings rather than automatically treating them as failures.

This provides an additional way to assess recommendation quality beyond simply checking whether the algorithm produces a ranked list.


Automated Evaluation Harness

I extended GrooveHUB with an automated evaluation harness that tests the recommendation system against multiple predefined user profiles.

The harness evaluates three different profiles:

High-Energy Pop
Chill Lofi
Intense Rock

For each profile, it generates five recommendations and evaluates recommendation availability, score validity, and explanation availability.

The harness calculates an overall success percentage based on the evaluation results and reports whether each profile passes or fails.

Run the evaluation harness:

bash
python -m src.evaluation_harness


Sample evaluation output:

text
GROOVEHUB AUTOMATED EVALUATION HARNESS

Songs loaded: 18
Scoring mode: balanced
Profiles to evaluate: 3

Evaluating: High-Energy Pop
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS

Evaluating: Chill Lofi
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS

Evaluating: Intense Rock
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS

FINAL EVALUATION SUMMARY

Profiles evaluated: 3
Profiles passed:    3
Profiles failed:    0
Overall success:    100.00%

OVERALL RESULT: PASS


The harness makes it possible to evaluate recommendation reliability across multiple user profiles rather than relying on a single successful application run.

The results demonstrate that the current implementation passes its predefined structural and scoring checks. They do not independently establish that users will consider the recommendations relevant or enjoyable.

5. Evaluation Logging

I introduced an evaluation logging component in src/evaluation_logger.py to record the results of recommendation evaluations.

The system records information including:

- Timestamp of the evaluation.
- User profile being evaluated.
- Selected scoring strategy.
- Number of recommendations generated.
- Whether the evaluation passed.
- Overall reliability percentage.
- Number of successful checks.
- Any identified issues or warnings.

Evaluation results are saved in:

logs/evaluation_results.jsonl – Stores structured evaluation results in JSON Lines format.
logs/application.log – Stores application activity and evaluation messages.

This provides a record of previous evaluation runs and makes it easier to review the system's performance over time.

6. Automated Testing

I expanded the project's automated test coverage to verify the recommendation algorithm, advanced features, scoring strategies, diversity controls, and reliability evaluation.

The test suite now contains 26 tests covering:

- Recommendation ranking and score ordering.
- Recommendation explanations.
- Repeat-artist penalties.
- CSV advanced feature loading.
- Optional preference scoring.
- Scoring strategy comparisons.
- Invalid scoring mode handling.
- Recommendation reliability evaluation.
- Empty recommendation handling.
- Invalid score detection.
- Missing explanation detection.
- Repeated-artist warnings.
- Recommendation table formatting.
- RAG retrieval for pop, rock, jazz, and artist queries.
- RAG context influence on scores and explanations.
- No-match and empty-query fallback behavior.
- Missing knowledge-base files, invalid JSON, incorrect structures, empty databases, and malformed entries.

Tests are executed using:

bash
python -m pytest -v


Latest test results:

text
============================= test session starts ==============================
collected 26 items

tests/test_recommender.py ...                                                  [100%]

============================== 26 passed ========================================


All 26 automated tests passed successfully.

End-to-End Application Demonstration

GrooveHUB provides a complete recommendation workflow that loads the song dataset, processes different user preference profiles, generates personalized recommendations, evaluates recommendation reliability, and records evaluation results.

The application currently demonstrates three different user profiles:

High-Energy Pop: Prioritizes pop music, a happy mood, and high energy.
Chill Lofi: Prioritizes lofi music, a chill mood, and low energy.
Intense Rock: Prioritizes rock music, an intense mood, and high energy.
Running the Application

To execute the complete recommendation workflow, run:

bash
python -m src.main


The application loads 18 songs and uses the Balanced scoring strategy.

Example Recommendation Results

The following results were generated by running the application.

High-Energy Pop

Rank	Song	Score
1	Sunrise City	4.04
2	Gym Hero	3.16
3	Rooftop Lights	2.90
4	Storm Runner	2.17
5	Iron Orchard	2.03

Reliability evaluation:

text
Status: PASS
Reliability Score: 100.0%
Checks Passed: 3/3
No issues or warnings detected.


Chill Lofi

Rank	Song	Score
1	Library Rain	4.02
2	Midnight Coding	3.91
3	Spacewalk Thoughts	3.05
4	Focus Flow	2.69
5	Field of Lanterns	2.05

Reliability evaluation:

text
Status: PASS
Reliability Score: 100.0%
Checks Passed: 3/3

Warnings:
- Some artists appear more than once
in the recommendations.


Intense Rock

Rank	Song	Score
1	Storm Runner	4.10
2	Gym Hero	3.18
3	Iron Orchard	2.13
4	Sunrise City	1.95
5	Saturday Static	1.87

Reliability evaluation:

text
Status: PASS
Reliability Score: 100.0%
Checks Passed: 3/3
No issues or warnings detected.

End-to-End Evaluation Logging

After each profile has been evaluated, the application records its evaluation results.

The structured evaluation records are saved to:

text
logs/evaluation_results.jsonl


Application activity is recorded in:

text
logs/application.log


The JSON Lines file stores information such as the profile name, scoring mode, recommendation count, reliability score, evaluation status, issues, and warnings.

This allows previous evaluation runs to be reviewed without relying exclusively on terminal output.

Automated Test Execution

The complete automated test suite can be executed using:

bash
python -m pytest -v


Latest test results:

text
============================= test session starts ==============================
collected 26 items

tests/test_recommender.py ...                                                  [100%]

============================== 26 passed ========================================


All 26 automated tests passed successfully.

End-to-End Demonstration Reflection

The end-to-end demonstration shows that GrooveHUB can process different preference profiles and produce different recommendation rankings using the same song dataset.

For example, Sunrise City ranks first for High-Energy Pop, Library Rain ranks first for Chill Lofi, and Storm Runner ranks first for Intense Rock.

The application also demonstrates how recommendation explanations, artist diversity warnings, reliability evaluation, and persistent logging work together.

This confirms that the additional features are integrated into the working recommendation system rather than existing as separate demonstrations.



Reliability Evaluation Demonstration

GrooveHUB includes an automated reliability evaluation component that checks whether generated recommendations meet basic quality requirements.

The evaluation mechanism performs three checks:

Recommendation availability: Confirms that recommendations have been generated.
Score validity: Checks that recommendation scores are numeric, finite, and within the expected scoring range.
Explanation availability: Confirms that every recommendation contains a non-empty explanation.

Each successful check contributes to the overall reliability percentage.

Successful Evaluation Example

Input: A valid set of song recommendations containing numerical scores and explanations.

Expected behavior: All three reliability checks pass.

Result:

text
Reliability Evaluation:
Status: PASS
Reliability Score: 100.0%
Checks Passed: 3/3
No issues or warnings detected.

Failed Evaluation Examples

The evaluation component also identifies invalid recommendation results.

Test scenario	Expected behavior
Empty recommendations	Evaluation fails because no recommendations were generated.
Invalid score	Evaluation fails when a score is non-numeric or outside the expected range.
Missing explanation	Evaluation fails when a recommendation has no explanation.
Repeated artists	Evaluation produces a warning rather than automatically failing.

These checks help identify structural problems in recommendation results before they are treated as reliable outputs.

Evaluation Limitations

A 100% reliability score does not mean that recommendations are guaranteed to be accurate or that users will enjoy the songs.

The evaluation measures structural correctness, score validity, and explanation availability. It does not measure actual listener satisfaction or determine whether recommendations are musically appropriate.

This distinction is important because a recommendation system can produce technically valid results without necessarily producing personalized or enjoyable recommendations.



Automated Evaluation Harness

To further evaluate the reliability of GrooveHUB, I developed a separate automated evaluation harness in src/evaluation_harness.py.

The harness tests the recommendation system using three predefined user profiles:

High-Energy Pop
Chill Lofi
Intense Rock

For each profile, the harness:

Generates five song recommendations using the existing recommendation engine.
Evaluates the generated recommendations using evaluate_recommendations().
Checks whether the expected number of recommendations was generated.
Records the reliability score and evaluation result.
Includes any identified issues or warnings in the terminal output.
Running the Evaluation Harness

Run the following command from the project root:

bash
python -m src.evaluation_harness

Evaluation Results

The automated evaluation harness successfully evaluated all three predefined profiles.

text
GROOVEHUB AUTOMATED EVALUATION HARNESS

Songs loaded: 18
Scoring mode: balanced
Profiles to evaluate: 3

Evaluating: High-Energy Pop
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS

Evaluating: Chill Lofi
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS
WARNING: Some artists appear more than once
in the recommendations.

Evaluating: Intense Rock
Recommendations generated: 5/5
Reliability score: 100.00%
Checks passed: 3/3
Profile result: PASS

FINAL EVALUATION SUMMARY

Profiles evaluated: 3
Profiles passed:    3
Profiles failed:    0
Overall success:    100.00%

OVERALL RESULT: PASS

Evaluation Summary

All three profiles generated the expected five recommendations and passed the reliability checks.

The Chill Lofi profile produced a repeated-artist warning. This did not cause the evaluation to fail because repeated artists are treated as warnings rather than critical errors.

The harness demonstrates that GrooveHUB can evaluate multiple predefined inputs consistently and report an overall evaluation result.

The evaluation measures structural reliability rather than actual listener satisfaction or recommendation accuracy.