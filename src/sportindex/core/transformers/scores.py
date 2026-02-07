def score_football(*, scores, time, periods, extras):
    def extract_periods(score):
        return {
            k: v for k, v in score.items()
            if k.startswith("period")
        }

    def extract_injury_time():
        return {
            k.replace("injuryTime", ""): v
            for k, v in time.items()
            if k.startswith("injuryTime")
        }

    return {
        "type": "period-based",
        "periods": {
            "home": extract_periods(scores["home"]),
            "away": extract_periods(scores["away"]),
        },
        "final": {
            "home": scores["home"].get("display"),
            "away": scores["away"].get("display"),
        },
        "penalties": {
            "home": scores["home"].get("penalties"),
            "away": scores["away"].get("penalties"),
        },
        "injury_time": extract_injury_time(),
    }


def score_tennis(*, scores, time, periods, extras):
    def extract_sets(score):
        return {
            k: score[k]
            for k in score
            if k.startswith("period") and not k.endswith("TieBreak")
        }

    def extract_tiebreaks(score):
        return {
            k.replace("period", "").replace("TieBreak", ""): v
            for k, v in score.items()
            if "TieBreak" in k
        }

    return {
        "type": "set-based",
        "sets": {
            "home": extract_sets(scores["home"]),
            "away": extract_sets(scores["away"]),
        },
        "tiebreaks": {
            "home": extract_tiebreaks(scores["home"]),
            "away": extract_tiebreaks(scores["away"]),
        },
        "points": {
            "home": scores["home"].get("point"),
            "away": scores["away"].get("point"),
        },
        "first_to_serve": extras["tennis"]["first_to_serve"],
    }


def score_mma(*, scores, time, periods, extras):
    return {
        "type": "bout",
        "winner": {
            "home": scores["home"].get("display"),
            "away": scores["away"].get("display"),
        },
        "fight": extras["fight"],
    }



_SCORE_HANDLERS = {
    "football": score_football,
    "tennis": score_tennis,
    "mma": score_mma,
}


def normalize_score(event: dict) -> dict | None:
    sport = event["sport"]
    handler = _SCORE_HANDLERS.get(sport)

    if not handler:
        return None

    return handler(
        scores=event["scores_raw"],
        time=event["time_raw"],
        periods=event.get("periods_descriptor"),
        extras=event["extras"],
    )