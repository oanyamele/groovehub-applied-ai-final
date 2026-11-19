# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
**GrooveHUB** 

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

GrooveHUB is designed to recommend songs based on a user's preferred genre, mood, and energy level. It is intended for classroom learning and demonstrating how a basic recommendation algorithm works. It assumes that users can describe their music preferences using these features. It is not designed to replace a real music streaming service or fully understand individual musical taste.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

GrooveHUB's balanced strategy awards 1 point for an exact genre match and 1 point for an exact mood match. Energy similarity contributes up to 2 points: it is calculated as 2 × (1 − |song energy − target energy|). A popularity prior can add up to 0.25 points. When the user supplies matching optional preferences, mood tags, release decade, acousticness, and danceability can each add a bounded bonus.

Genre-first and energy-focused strategies use different genre, mood, and energy weights. After scoring, the recommender selects songs in rank order and subtracts 0.25 points when an artist has already been selected, encouraging variety. Optional lexical RAG retrieval can add up to 0.50 points when a song matches retrieved music knowledge. Recommendations include explanations of the applied scoring reasons. The balanced core weights reflect the experiment that reduced genre weight from 2 to 1 and increased the maximum energy weight from 1 to 2; advanced features, diversity, and RAG were added separately.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The recommender uses a CSV catalog of 18 songs. Each song includes a title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, and mood tags. The balanced core score uses genre, mood, and energy; popularity is a small prior, while mood tags, release decade, acousticness, and danceability can contribute when the corresponding preference is supplied. Tempo and valence are not currently scored. The genres and moods cover different styles, but many genres appear only once, and this small dataset cannot represent the full range of musical styles or personal preferences.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The recommender explains why each song receives its score and supports three strategies, optional musical-feature preferences, artist diversity, and a configurable music knowledge base. The predefined profiles have historically placed Sunrise City, Library Rain, and Storm Runner first for High-Energy Pop, Chill Lofi, and Intense Rock, respectively. The scoring rules make it easy to test how changing feature weights affects results and provide a useful starting point for learning about ranking algorithms and personalized recommendations.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The dataset contains 18 songs. Lofi appears three times, pop appears twice, and most other genres appear only once, limiting variety. Core genre and mood matches are exact, so the system may not recognize similar styles or users who enjoy multiple genres. Tempo and valence are not used in scoring. Popularity, mood tags, release decade, acousticness, and danceability contribute only through a prior or when the corresponding optional preference is supplied. The system does not subtract points for genre or mood mismatches, so a song can still rank highly through energy or other bonuses. RAG uses lexical keyword overlap and can miss synonyms or superficial matches; it is not semantic retrieval. The repeat-artist penalty encourages variety but does not guarantee it. These are risks and design limitations, not evidence that the recommender has caused a filter bubble.
---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested GrooveHUB using three user profiles: High-Energy Pop, Chill Lofi, and Intense Rock. The original core-scoring experiment checked whether recommendations matched each profile's preferred genre, mood, and energy. Sunrise City, Library Rain, and Storm Runner ranked first for those profiles in that experiment. Gym Hero could rank highly despite a mood or genre mismatch because the scoring system adds matching-feature points and does not subtract for mismatches. These observations describe the core-weight experiment; the current harness also enables lexical RAG, and the final implementation includes advanced bonuses and artist-diversity ranking, so its scores can differ.

Historical Weight-Shift Experiment Results (core-only run):
I changed the genre weight from 2 points to 1 point and doubled the energy similarity weight from a maximum of 1 point to 2 points. The mood weight remained at 1 point. I then reran the recommender for all three profiles. The top recommendation for each profile remained the same: Sunrise City for High-Energy Pop, Library Rain for Chill Lofi, and Storm Runner for Intense Rock. The rankings for High-Energy Pop and Intense Rock also stayed in the same order. The Chill Lofi rankings changed slightly. In the original results, Focus Flow ranked third and Spacewalk Thoughts ranked fourth. After the weight change, Spacewalk Thoughts moved to third place and Focus Flow moved to fourth. Spacewalk Thoughts matched the preferred mood and had energy close to the target, while Focus Flow matched the preferred genre but not the mood. Giving energy more weight allowed Spacewalk Thoughts to rank higher. This experiment showed that changing the importance of different features can change rankings even when the song catalog stays the same. However, the new rankings are not automatically more accurate. I would need to compare the recommendations with listeners' actual preferences to determine whether the changes improve their experience.

Historical Profile Comparisons (core-only run):
High-Energy Pop vs. Chill Lofi:
High-Energy Pop recommended Sunrise City first, while Chill Lofi recommended Library Rain first. Sunrise City matched the pop and happy preferences and had high energy. Library Rain matched the lofi and chill preferences and had energy close to the lower target. This makes sense because the profiles prefer different musical styles and energy levels. Some songs can still appear in both lists when their energy scores are high enough.

High-Energy Pop vs. Intense Rock:
High-Energy Pop recommended Sunrise City first, while Intense Rock recommended Storm Runner first. Both profiles also included Gym Hero, Storm Runner, and Iron Orchard in their top five. This makes sense because both profiles target high-energy music. However, the reasons for individual recommendations differ. Gym Hero earns genre and energy points for High-Energy Pop, but mood and energy points for Intense Rock. This illustrates how the same song can appeal to the scoring rules of different profiles for different reasons.

Chill Lofi vs. Intense Rock:
Chill Lofi recommended Library Rain first, while Intense Rock recommended Storm Runner first. Library Rain matched the lofi and chill preferences and had energy close to 0.3. Storm Runner matched the rock and intense preferences and had energy close to 0.95. These differences make sense because the profiles target different genres, moods, and energy levels. Some high-energy songs can still appear in the Intense Rock recommendations without matching the preferred genre or mood, because energy similarity contributes points independently.

Overall, the core-only evaluations showed that GrooveHUB responds to different user preferences and that changing scoring weights can affect rankings. Energy can compensate for a genre or mood mismatch. The current repeat-artist penalty encourages variety, though it does not guarantee it.

---

## RAG Music Knowledge Enhancement

### Purpose

The RAG enhancement augments GrooveHUB's existing deterministic weighted recommender with contextual music knowledge before candidate songs are ranked. It lets explicit music requests influence scores and explanations when they match a custom knowledge base.

This implementation does not use embeddings, vector search, fine-tuning, or an LLM. It is lexical retrieval followed by deterministic scoring.

### Custom Knowledge-Base Structure

The knowledge base is `data/music_knowledge.json`, a JSON list of 14 documents. Each document can contain:

- `id` and `title`: document identity and short name.
- `genre`: the primary genre or subgenre.
- `artists`: representative artist names.
- `mood`: the primary mood or theme.
- `description`: musical characteristics and stylistic context.
- `keywords`: searchable styles and themes.

The documents cover pop, lofi, rock, metal, jazz, synthwave, ambient, reggae, country, classical, R&B, funk, folk, and Latin music.

### How Retrieval Works

`load_music_knowledge()` loads and validates the JSON list. `retrieve_music_context()` converts a string or profile dictionary into searchable text. String requests are searched directly. For profiles, explicit `music_request`, `query`, or `similar_to` fields take priority; otherwise the function combines genre, mood, desired tags, and release decade.

The function:

1. Converts text to lowercase.
2. Extracts alphanumeric terms of at least two characters.
3. Ignores common retrieval stop words.
4. Searches titles, genres, artists, moods, descriptions, and keywords.
5. Sorts matching documents by score and returns the top three.

An empty query or no matching terms returns no documents. Missing files and invalid JSON raise `ValueError` from the loader. `recommend_songs()` catches that loader failure and falls back to baseline behavior.

### Effect on Recommendation Scoring

`recommend_songs()` continues to calculate the original core, advanced-feature, and repeat-artist scores. When RAG is enabled, it loads the knowledge base and calls `apply_retrieved_context()` for every candidate song.

Retrieved context is compared with the song's genre, mood, artist, and mood tags. Matching each category can contribute to a maximum 0.50-point context bonus:

- Genre match.
- Mood match.
- Artist match.
- Mood-tag match.

The bounded bonus is included in the final score and the visible `retrieved context match (...)` explanation.

### Difference from the Baseline

Without RAG, `recommend_songs(..., rag_enabled=False)` uses only CSV song data and existing weighted scoring. With RAG enabled, matching knowledge-base context can increase a score and change a ranking. RAG supplements but does not replace the existing recommendation engine.

### Verified Before-and-After Examples

**Uplifting pop for a happy workout**

- Baseline top: Sunrise City — 4.205.
- RAG top: Sunrise City — 4.705.
- RAG added an artist, genre, mood, and mood-tag bonus of 0.50.

**Aggressive rock with Voltline**

- Baseline top: Storm Runner — 4.105.
- RAG top: Storm Runner — 4.605.
- RAG added rock/intense/Voltline context with a 0.50-point bonus.

**Warm relaxed jazz**

- Baseline top: Coffee Shop Stories — 4.105.
- RAG top: Coffee Shop Stories — 4.605.
- RAG added jazz/relaxed context with a 0.50-point bonus.

Across these requests, RAG changed scores and top-five ordering. This demonstrates ranking influence, but it does not prove listener satisfaction because no user-study or human relevance-judgment dataset is included.

### Limitations

The retriever is lexical rather than semantic. It cannot understand most synonyms or paraphrases unless their terms occur in the knowledge text. It may match superficial keyword overlap and has no embeddings, reranking, persistent index, or external retrieval source. The knowledge base contains 14 documents and is limited to classroom-provided music information. The 0.50-point bonus is deliberately small, so RAG supplements rather than overwhelms the existing scoring signals.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

If I continued developing GrooveHUB, I would add tempo, danceability, and acousticness to the scoring system. I would also expand the song catalog to include more genres, moods, and artists. Finally, I would also add a diversity rule to reduce repetitive recommendations and help users discover different types of music.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

My biggest learning moment was discovering that changing the weights in a recommendation algorithm can change song rankings, even when the song data stays the same. I learned that a song can rank highly without matching every user preference because the algorithm adds points for the features it does match. AI tools helped me understand the scoring logic, review my code, and identify possible biases. However, I still needed to run the program and compare the actual results to make sure the explanations matched what happened. I was surprised that such a simple algorithm could produce recommendations that felt personalized. I also learned that reasonable-looking results do not mean the system fully understands someone's musical taste. If I continued this project, I would use more songs, include additional musical features in the scoring, and add a way to recommend a wider variety of music. I would also test more user profiles to see how well the system handles different or conflicting preferences.