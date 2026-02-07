# from ..player import transform_player


# def transform_period(raw: dict) -> dict:
#     """ Transform a incident of type 'period', aka end of a period (half, extra time, etc.), into a structured format. """
#     return {
#         "id": None, # No unique ID for period incidents
#         "reg_time": raw.get("time"),
#         "added_time": 0, 
#         "type": "period",
#         "text": raw.get("text"), # e.g. FT, HT, etc.
#         "home_score": raw.get("homeScore"),
#         "away_score": raw.get("awayScore"),
#     }

# def transform_card(raw: dict) -> dict:
#     """ Transform a incident of type 'card' into a structured format. """
#     return {
#         "id": raw.get("id"),
#         "reg_time": raw.get("time"),
#         "added_time": raw.get("addedTime", 0),
#         "type": "card",
#         "player": transform_player(raw.get("player", {})),
#         "reason": raw.get("reason"),
#         "rescinded": raw.get("rescinded", False),
#         "color": raw.get("incidentClass"),
#         "home": raw.get("isHome"),
#     }

# def transform_var_decision(raw: dict) -> dict:
#     """ Transform a incident of type 'var_decision' into a structured format. """
#     return {
#         "id": raw.get("id"),
#         "reg_time": raw.get("time"),
#         "added_time": raw.get("addedTime", 0),
#         "type": "var_decision",
#         "decision": raw.get("text"),
#         "home": raw.get("isHome"),
#         "detail": raw.get("incidentClass"), # Penalty check, offside, card upgrade, etc.
#         "player": transform_player(raw.get("player", {})),
#     }

# def transform_goal(raw: dict) -> dict:
#     """ Transform a incident of type 'goal' into a structured format. """
#     return {
#         "id": raw.get("id"),
#         "reg_time": raw.get("time"),
#         "added_time": raw.get("addedTime", 0),
#         "type": "goal",
#         "home": raw.get("isHome"),
#         "scorer": transform_player(raw.get("player", {})),
#         "assist": transform_player(raw.get("assist1", {})),
#         # TODO - Add the passing network !! Could be very valuable for further analysis...
#         "home_score": raw.get("homeScore"),
#         "away_score": raw.get("awayScore"),
#     }

# def transform_substitution(raw: dict) -> dict:
#     """ Transform a incident of type 'substitution' into a structured format. """
#     return {
#         "id": raw.get("id"),
#         "reg_time": raw.get("time"),
#         "added_time": raw.get("addedTime", 0),
#         "type": "substitution",
#         "player_in": transform_player(raw.get("playerIn", {})),
#         "player_out": transform_player(raw.get("playerOut", {})),
#         "injury": raw.get("injury", False),
#         "home": raw.get("isHome"),
#     }

# def transform_extra_time(raw: dict) -> dict:
#     """ Transform a incident of type 'extra_time' into a structured format. """
#     return {
#         "id": None, # No unique ID for extra time incidents
#         "reg_time": raw.get("time"),
#         "added_time": raw.get("addedTime", 0), # Added time at which extra time has been decided
#         "extra_time": raw.get("length"), # Value actually added
#         "type": "extra_time",
#     }

# MAP_INCIDENT_TYPE_TO_TRANSFORMER = {
#     "period": transform_period,
#     "card": transform_card,
#     "varDecision": transform_var_decision,
#     "goal": transform_goal,
#     "substitution": transform_substitution,
#     "injuryTime": transform_extra_time
#     # TODO - To implement: "inGamePenalty", ...
# }

# def transform_incident(raw: dict) -> dict:
#     """ Transform a single incident entry for a detailed event. """
#     return MAP_INCIDENT_TYPE_TO_TRANSFORMER.get(raw.get("incidentType"), lambda x: x)(raw)
