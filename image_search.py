def zoek_product_foto(query: str) -> str | None:
    """Zoek een productfoto via DuckDuckGo. Geeft URL terug of None."""
    if not query or not query.strip():
        return None
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(f"{query} food", max_results=5, safesearch="moderate"))
            for r in results:
                url = r.get("image")
                if url and url.startswith("http"):
                    return url
    except Exception:
        return None
    return None
