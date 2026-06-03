from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score

    Return the response as a plain string.
    """
    fallback_message = "I could not find that answer in the loaded rulebook context."

    if not retrieved_chunks:
        return fallback_message

    context_blocks = []

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context_blocks.append(
            f"--- Chunk {i} ---\n"
            f"Game: {chunk['game']}\n"
            f"Distance: {chunk['distance']:.3f}\n"
            f"Rule Text:\n{chunk['text']}"
        )

    context = "\n\n".join(context_blocks)

    system_prompt = (
        "You are RulesBot, a board-game rules assistant. "
        "Answer the user's question using only the rule text provided in the context. "
        "Do not use outside knowledge, prior knowledge, assumptions, or general board-game knowledge. "
        "If the answer is not clearly contained in the provided context, say that the answer could not be found "
        "in the loaded rulebook context. "
        "Do not invent rules, exceptions, examples, or missing details. "
        "When you answer, identify the game the rule came from. "
        "Use a simple citation format such as: 'According to the [Game] rules...' "
        "If multiple games are relevant, separate the answer by game. "
        "Do not cite a game unless its retrieved context supports the answer."
    )

    user_prompt = (
        f"Context:\n{context}\n\n"
        f"User question:\n{query}"
    )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    return response.choices[0].message.content