def format_mentions(content: str, mentions) -> str:
    """Replace <@id> with @username."""
    result = content
    for m in mentions:
        result = result.replace(f"<@!{m.id}>", f"@{m.name}").replace(f"<@{m.id}>", f"@{m.name}")
    return result