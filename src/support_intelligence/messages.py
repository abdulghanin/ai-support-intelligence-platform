def normalize_message(text: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        raise ValueError("Message cannot be empty")
    return cleaned
