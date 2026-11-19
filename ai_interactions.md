# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**
I used an AI coding assistant to extend GrooveHUB with advanced song features, artist diversity, multiple scoring modes, and formatted terminal output.

**Prompts used:**
- Challenge 1 — "Add at least five advanced song attributes, update the scoring logic, document simulated data, and add tests."
- Challenge 2 — "Implement Balanced, Genre-First, and Energy-Focused modes using a modular design pattern. Add a mode selector and tests."
- Challenge 3 — "Apply a 0.25-point penalty to songs by already-recommended artists. Update explanations and add tests."
- Challenge 4 — "Display recommendations in an ASCII table showing rank, song, artist, score, and scoring reasons. Handle long text and add tests."

**What did the agent generate or change?**
- data/songs.csv: Added popularity, release decade, and mood tags.
- src/recommender.py: Added advanced-feature scoring, three scoring strategies, and an artist-diversity penalty.
- src/main.py: Added scoring-mode selection and formatted recommendation tables.
- tests/test_recommender.py: Added tests for scoring, diversity, strategies, and table formatting.
- README.md: Documented the additional features.


**What did you verify or fix manually?**
I ran the application in all three scoring modes and compared the recommendations. I checked that the diversity penalty appeared in explanations, advanced features contributed to scores, and the table displayed all reasons. I also reviewed and reran tests after the AI corrected issues with score formatting, invalid modes, and table width.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**
Strategy

**How did AI help you brainstorm or implement it?**
The AI suggested separate scoring strategies while keeping advanced-feature scoring and artist-diversity logic shared. It also recommended a configurable SCORING_MODE setting in main.py.

**How does the pattern appear in your final code?**
In src/recommender.py, Balanced, Genre-First, and Energy-Focused strategies use different genre, mood, and energy weights. In src/main.py, SCORING_MODE selects the strategy. I tested all three modes and confirmed that their scores and explanations reflected the selected weights.



---

## AI Collaboration and Design Decisions:

### How I Used AI During Development:

I used ChatGPT as a development assistant throughout the extension of GrooveHUB. I used it to brainstorm improvements, understand different implementation approaches, troubleshoot Python errors, improve the recommendation algorithm, and develop additional automated tests.

AI assistance helped me explore advanced song features, multiple scoring strategies, artist diversity, reliability evaluation, and evaluation logging. I also used it to review terminal output and understand how changes to scoring weights affected recommendation rankings.

However, I did not rely on AI-generated code without checking the results. I ran the application, examined recommendation scores and explanations, and used automated tests to verify that the functionality worked as intended.

AI assistance during development is separate from the model used at runtime. GrooveHUB's recommendations are produced by deterministic Python scoring; its optional RAG feature uses lexical keyword retrieval over the local music knowledge base and does not call an LLM, use embeddings, or perform vector search.

### AI Suggestion I Accepted:

One suggestion I accepted was introducing a Strategy design pattern for the recommendation scoring modes.

Instead of creating three separate recommendation systems, I kept the recommendation process shared and allowed different scoring strategies to use different genre, mood, and energy weights.

I implemented Balanced, Genre-First, and Energy-Focused modes. This made the system easier to experiment with and allowed me to compare how different scoring priorities affected recommendations.

I also accepted the suggestion to introduce a repeat-artist penalty because it addressed a limitation in the original recommender: multiple songs by the same artist could appear in the recommendations. The 0.25-point penalty encouraged greater variety while still allowing repeated artists when their songs remained highly ranked.

### AI Suggestion I Rejected:

I considered using a more complicated AI model instead of extending the existing weighted scoring algorithm.

I decided not to pursue this suggestion because a more complex model was unnecessary for the project's size and objectives. GrooveHUB uses a small dataset of 18 songs, and its main purpose is to demonstrate how recommendation scores are calculated, explained, and evaluated.

A more complicated model would have introduced additional implementation requirements without necessarily improving the quality of recommendations for such a small dataset.

I chose to continue developing the existing scoring approach because it was easier to understand, test, explain, and compare across different user profiles.

This decision helped me understand that adding more complicated AI technology does not automatically make a system better. The solution should be appropriate for the problem, available data, and project requirements.

### What I Learned From Using AI:

Working with AI during development taught me that it can be a useful tool for exploring ideas, improving code, and identifying potential problems. However, AI-generated suggestions still need to be reviewed and tested.

I learned to compare suggested solutions against the actual project requirements rather than automatically accepting every recommendation.

The development of GrooveHUB also showed me the importance of independent decision-making. I used AI to help develop and improve the system, but I made decisions about which features were appropriate, how to evaluate the results, and which implementation approaches best suited the project.

Overall, AI helped accelerate development while allowing me to improve my understanding of software design, testing, and responsible AI-assisted development.