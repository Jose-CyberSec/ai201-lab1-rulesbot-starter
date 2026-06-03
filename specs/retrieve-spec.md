# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I will use _collection.query() to run semantic search against the stored rulebook chunks. I will pass query_texts=[query] because ChromaDB expects a list of query strings, even when there is only one query. I will pass n_results=n_results so the function returns the configured number of closest matching chunks. I will also include ["documents", "metadatas", "distances"] so I can return the chunk text, the game metadata, and the similarity distance score.
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
One returned item should look like this:

{
    "text": "When a 7 is rolled, no players receive resources...",
    "game": "Catan",
    "distance": 0.471
}

The "text" value comes from results["documents"][0]. The "game" value comes from results["metadatas"][0], using the "game" key stored during ingestion. The "distance" value comes from results["distances"][0]. The results should stay ordered by distance, with the lowest distance first.
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
_collection.query() returns nested lists because it can handle multiple queries at once. Since this app only sends one query at a time using query_texts=[query], the actual returned results are inside index [0]. I need to use results["documents"][0], results["metadatas"][0], and results["distances"][0]. If I use results["documents"] directly, I would get a list containing another list instead of the actual chunk text strings.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
For this milestone, I will return all n_results instead of filtering by a strict threshold. This makes it easier to inspect and debug retrieval results because I can see both strong and weak matches. The tradeoff is that some lower-quality chunks may be returned, especially for vague questions. Later, I could add a threshold around 0.7 or lower to flag weak matches and prevent the generator from answering with poor context.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
If the collection is empty, retrieve() should return an empty list. If the query matches no chunks well, ChromaDB may still return the closest n_results, but the distance scores will likely be high, which shows that the results are weak. If the query matches chunks from multiple games, retrieve() should return them ranked by similarity. This can happen with broad questions like "How do you win?" because multiple games have winning conditions. In that case, the generator may need to answer by game or ask the user to clarify.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: What happens if you roll a 7 in Catan?
Top result game: Catan
Distance score: 0.471
Does it make sense? Yes. The top result came from Catan, which matches the game named in the query. The retrieved chunk was related to rolling a 7 and the rule that hexes produce no resources on that roll.
```

**One thing about the query results that surprised you:**

```
The top result was from the correct game, but one of the lower-ranked results came from Uno. This surprised me because the query clearly mentioned Catan. It shows that semantic search returns the closest matches across the whole vector database unless we add filtering by game or a relevance threshold. It also shows why distance scores are important for debugging retrieval quality.
```
