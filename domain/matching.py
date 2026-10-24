"""Pure matching and ranking logic used by the recommendation screen."""


def parse_selected_notes(notes_input):
    """Parse comma-separated notes input into a list of individual notes."""
    if not notes_input or not notes_input.strip():
        return []
    return [note.strip() for note in notes_input.split(",") if note.strip()]


def matches_notes(perfume_notes, selected_notes, strict=True):
    """Return whether a perfume contains the requested notes."""
    if not selected_notes:
        return True

    perfume_notes_lower = [note.lower() for note in perfume_notes]
    if strict:
        return all(
            any(note.lower() in perfume_note for perfume_note in perfume_notes_lower)
            for note in selected_notes
        )
    return any(
        any(note.lower() in perfume_note for perfume_note in perfume_notes_lower)
        for note in selected_notes
    )


def match_score(product, profile, notes_selected, strict_notes=True):
    """Calculate a product's match tier and percentage."""
    score = 0
    total = 0

    if profile["gender"] != "Any":
        total += 1
        if (
            profile["gender"] == "Unisex"
            or product["gender"] == "Unisex"
            or product["gender"] == profile["gender"]
        ):
            score += 1

    for field in ("intensity", "season", "concept", "longevity"):
        if profile[field] != "Any":
            total += 1
            if product[field] == profile[field]:
                score += 1

    if not matches_notes(product["notes"], notes_selected, strict=strict_notes):
        return None

    total = total or 1
    match_percentage = int((score / total) * 100)
    if match_percentage == 100:
        tier = 1
    elif score >= 2 or match_percentage >= 67:
        tier = 2
    else:
        tier = 3
    return tier, score, total, match_percentage


def filter_rank_products(
    profile, notes_input, sort_mode, products, translate, strict_notes=True
):
    """Filter and rank products using the application's matching rules."""
    notes_selected = parse_selected_notes(notes_input)
    scored = []
    for product in products:
        result = match_score(product, profile, notes_selected, strict_notes=strict_notes)
        if result is None:
            continue
        tier, score, total, match_percentage = result
        scored.append(
            {
                **product,
                "match": match_percentage,
                "_score": score,
                "_tier": tier,
            }
        )

    if sort_mode == translate("Best match"):
        scored.sort(key=lambda item: (item["_tier"], -item["_score"]))
    elif sort_mode == translate("Name A-Z"):
        scored.sort(key=lambda item: item["name"])
    elif sort_mode == translate("Name Z-A"):
        scored.sort(key=lambda item: item["name"], reverse=True)
    return scored
