def zoek_product_foto(query: str) -> str | None:
    """Zoek een echte productfoto via DuckDuckGo. Geeft URL terug of None."""
    if not query or not query.strip():
        return None
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(
                f"{query} gerecht",
                max_results=10,
                safesearch="moderate",
                type_image="photo",
                size="Medium",
            ))
            for r in results:
                url = r.get("image")
                if url and url.startswith("http"):
                    return url
    except Exception:
        return None
    return None
