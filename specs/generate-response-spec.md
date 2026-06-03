# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
I will format each retrieved chunk as a clearly labeled context block. Each block will include the chunk number, game name, distance score, and rule text. I will separate chunks with clear delimiters so the model can tell where one source ends and the next begins. Including the game name helps the model cite the correct game, and including the distance score helps preserve retrieval transparency during debugging.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are RulesBot, a board-game rules assistant. Answer the user's question using only the rule text provided in the context. Do not use outside knowledge, prior knowledge, assumptions, or general board-game knowledge. If the answer is not clearly contained in the provided context, say that the answer could not be found in the loaded rulebook context. Do not invent rules, exceptions, examples, or missing details.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
When you answer, identify the game the rule came from. Use a simple citation format such as: "According to the [Game] rules..." If multiple games are relevant, separate the answer by game. Do not cite a game unless its retrieved context supports the answer.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
I could not find that answer in the loaded rulebook context.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
For this milestone, I will pass all retrieved chunks into the context because retrieve() already returns a small number of top results. This makes testing easier because I can see how the model handles both strong and weaker matches. The tradeoff is that weak chunks could distract the model or cause a less focused answer. In a stronger production version, I would filter out chunks with high distance scores or ask the user to clarify when the retrieved context is weak.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
The API call will use two messages. The system message will contain the grounding and citation instructions. The user message will contain the formatted retrieved context followed by the user's original question. Keeping the rules in the system message makes the model's behavior stricter, while putting the retrieved chunks and question in the user message gives the model the evidence it needs to answer.
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: What happens if you roll a 7 in Catan?
Response: According to the Catan rules, when a 7 is rolled, no resources are produced. Every player with more than 7 resource cards must discard half. The player who rolled moves the robber and steals one resource.
Correctly grounded? Yes
Cited the right game? Yes
```

**One thing you changed from your original spec after seeing the actual output:**

```
The response correctly identified Catan and answered from the retrieved context. One improvement I noticed is that the answer cites the game name but does not cite a specific source file or chunk number. For this lab, citing the game is acceptable, but in a stronger version I would include the source filename or chunk ID for better verification.
```
