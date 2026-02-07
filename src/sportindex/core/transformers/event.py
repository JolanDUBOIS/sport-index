from .team import transform_team
from .competition import transform_tournament, transform_season
from .venue import transform_venue
from .referee import transform_referee


def infer_score_model(raw: dict) -> str:
    if raw.get("fightType") or raw.get("winType"):
        return "fight"
    if any("TieBreak" in k for k in raw.get("homeScore", {})):
        return "set-based"
    if raw.get("periods"):
        return "multi-period"
    return "aggregate"


def normalize_periods(raw: dict) -> dict:
    home = raw.get("homeScore", {}) or {}
    away = raw.get("awayScore", {}) or {}
    periods_meta = raw.get("periods", {}) or {}
    time = raw.get("time", {}) or {}

    periods = {}

    # Explicit period definitions (tennis, basketball, etc.)
    if periods_meta:
        for key, label in periods_meta.items():
            if not key.startswith("period"):
                continue
            idx = key.replace("period", "")
            periods[idx] = {
                "label": label,
                "home": home.get(key),
                "away": away.get(key),
                "extra": {
                    "tiebreak": {
                        "home": home.get(f"{key}TieBreak"),
                        "away": away.get(f"{key}TieBreak"),
                    }
                }
            }

    # Football-style implicit periods
    elif any(k.startswith("period") for k in home):
        for k, v in home.items():
            if not k.startswith("period"):
                continue
            idx = k.replace("period", "")
            periods[idx] = {
                "label": f"Period {idx}",
                "home": v,
                "away": away.get(k),
                "extra": {
                    "injury_time": time.get(f"injuryTime{idx}")
                }
            }

    # Fight sports: rounds without per-round score
    elif raw.get("fightType"):
        total = time.get("totalPeriodCount")
        if total:
            for i in range(1, total + 1):
                periods[str(i)] = {
                    "label": f"Round {i}",
                    "home": None,
                    "away": None,
                    "extra": {}
                }

    return periods


def normalize_final_score(raw: dict) -> dict:
    home = raw.get("homeScore", {}) or {}
    away = raw.get("awayScore", {}) or {}

    return {
        "home": (
            home.get("display")
            or home.get("normaltime")
            or home.get("points")
        ),
        "away": (
            away.get("display")
            or away.get("normaltime")
            or away.get("points")
        ),
        "winner_code": raw.get("winnerCode"),
    }


def transform_score(raw: dict) -> dict:
    return {
        "model": infer_score_model(raw),
        "periods": normalize_periods(raw),
        "final": normalize_final_score(raw),
    }


def transform_event(raw: dict) -> dict:
    return {
        "id": raw.get("id"),
        "custom_id": raw.get("customId"),
        "slug": raw.get("slug"),
        "timestamp": raw.get("startTimestamp"),
        "gender": raw.get("gender"),

        "tournament": transform_tournament(raw.get("tournament", {})),
        "season": transform_season(raw.get("season", {})),

        "participants": {
            "home": transform_team(raw.get("homeTeam", {})),
            "away": transform_team(raw.get("awayTeam", {})),
        },

        "score": transform_score(raw),

        "referee": transform_referee(raw.get("referee", {})),

        "round_info": raw.get("roundInfo"),
        "status": raw.get("status"),

        "venue": transform_venue(raw.get("venue", {})),

        "extra": {
            "first_to_serve": raw.get("firstToServe"),
            "rules": {
                "default_period_count": raw.get("defaultPeriodCount"),
                "default_period_duration": raw.get("defaultPeriodLength"),
                "overtime_duration": raw.get("defaultOvertimeLength"),
            },
            "red_cards": {
                "home": raw.get("homeRedCards", 0),
                "away": raw.get("awayRedCards", 0),
            }
        },

        # Fight sports (only populated when relevant)
        "fight": {
            "type": raw.get("fightType"),
            "order": raw.get("order"),
            "weight_class": raw.get("weightClass"),
            "win_type": raw.get("winType"),
            "final_round": raw.get("finalRound"),
        } if raw.get("fightType") else None
    }
