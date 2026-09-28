import os

SYSTEM_INSTRUCTION = (
    "You are a customer support assistant. Answer only from the provided "
    "context. If the context does not contain the answer, say you do not know. "
    "Do not invent policies, prices, or order details."
)


def generate_answer(question: str, context: str) -> str:
    """Generate an answer using the configured LLM provider."""
    provider = os.getenv("LLM_PROVIDER", "demo").lower()

    if provider == "demo":
        return context

    model = os.environ["LLM_MODEL"]
    prompt = f"Context:\n{context}\n\nCustomer question:\n{question}"

    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model=model,
            instructions=SYSTEM_INSTRUCTION,
            input=prompt,
            store=False,
        )
        return response.output_text

    if provider == "gemini":
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
        if not response.text:
            raise RuntimeError("Gemini returned no text")
        return response.text

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model=model,
            max_tokens=512,
            system=SYSTEM_INSTRUCTION,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    raise ValueError(f"Unsupported LLM provider: {provider}")
