def get_confidence_level(confidence_score):
    try:
        score = float(confidence_score)
    except (ValueError, TypeError):
        return "Low"

    if score >= 80:
        return "High"

    if score >= 60:
        return "Medium"

    return "Low"