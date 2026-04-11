TEST_CONFIG = {
    # =========================================================
    # FOOTBALL DOMAIN
    # =========================================================
    "football": {
        "sport": "football",
        "valid_dates": ["2026-02-08", "2026-02-10", "2026-05-16"], 
        
        # Categories -> Unique Tournaments -> Seasons -> Tournaments
        "tournaments": [
            {
                "category_id": 1465, # Europe
                "unique_tournament_id": 7, # UEFA Champions League
                "season_id": 76953, # 2025/2026
                "round": {"round": 1} # Champions League Round 1
            },
            {
                "category_id": 1465, # Europe
                "unique_tournament_id": 7, # UEFA Champions League
                "season_id": 61644, # 2024/2025
                "round": {"round": 636, "round_slug": "playoff-round", "round_prefix": "Qualification"}
            },
            {
                "category_id": 1, # England
                "unique_tournament_id": 17, # Premier League
                "season_id": 76986, # 2025/2026
                "round": {"round": 1} # Premier League Day 1
            },
            {
                "category_id": 1, # England
                "unique_tournament_id": 17, # Premier League
                "season_id": 61627, # 2024/2025
            },
            {
                "category_id": 1468, # World
                "unique_tournament_id": 16, # FIFA World Cup
                "season_id": 58210, # 2026
            },
            {
                "category_id": 1468, # World
                "unique_tournament_id": 16, # FIFA World Cup
                "season_id": 41087, # 2022
            },
        ],

        # Events
        "events": [
            {
                "event_id": 10230635, # WC 2022 Final: Argentina vs France
                "event_custom_id": "GObsuWb",
            },
            {
                "event_id": 14061910, # Ligue 1 2025/2026: PFC vs PSG (16/05/2026)
                "event_custom_id": "UHsvwc",
            },
        ],

        # Independent Entities
        "teams": [1644, 4481, 42],
        "players": [155995, 12994, 1421273],
        "managers": [129465, 794075],
        "referees": [69853, 72926],
        "venues": [843, 624],
    },

    # =========================================================
    # BASKETBALL DOMAIN
    # =========================================================
    "basketball": {
        "sport": "basketball",
        "valid_dates": [], 
        
        # Categories -> Unique Tournaments -> Seasons -> Tournaments
        "tournaments": [
            {
                "category_id": 15, # USA
                "unique_tournament_id": 132, # NBA
                "season_id": 80229, # 2025/2026
            },
            {
                "category_id": 15, # USA
                "unique_tournament_id": 132, # NBA
                "season_id": 84238, # 2024/2025
            },
        ],

        # Events
        "events": [
            {
                "event_id": 14442321,
                "event_custom_id": "qtbsEtb",
            },
            {
                "event_id": 14442067,
                "event_custom_id": "rtbsEtb",
            }
        ],

        # Independent Entities
        "teams": [3429],
        "players": [998725],
        "managers": [810805],
    },

    # =========================================================
    # TENNIS DOMAIN
    # =========================================================
    "tennis": {
        "sport": "tennis",
        
        # Categories -> Unique Tournaments -> Seasons -> Tournaments
        "tournaments": [
            {
                "category_id": 3, # ATP
                "unique_tournament_id": 2480, # Roland Garros
                "season_id": 61364, # 2025
            },
            {
                "category_id": 3, # ATP
                "unique_tournament_id": 2480, # Roland Garros
                "season_id": 52016, # 2024
            }
        ],

        # Events
        "events": [
            {
                "event_id": 13919038,
                "event_custom_id": "vGHbsytkc",
            }
        ],

        # Independent Entities
        "teams": [275923], # Players are represented as "teams" in the API for tennis
    },

    # =========================================================
    # MOTORSPORT DOMAIN
    # =========================================================
    "motorsport": {
        "sport": "motorsport",
        
        # Categories -> Unique Stages -> Seasons -> Stages (Race)
        "stages": [
            {
                "category_id": 36, # Formula 1
                "unique_stage_id": 40, # Formula 1
                "stage_season_id": 214140, # 2026
                "stage_id": 214141, # Australian GP
            },
            {
                "category_id": 36, # Formula 1
                "unique_stage_id": 40, # Formula 1
                "stage_season_id": 209766, # 2025
                "stage_id": 209774, # Monaco GP
            },
            {
                "category_id": 36, # Formula 1
                "unique_stage_id": 40, # Formula 1
                "stage_season_id": 209766, # 2025
                "stage_id": 209953, # Monaco GP Race
            },
        ],
    
        # Independent Entities
        "teams": [214910, 271315], # Mercedes, George Russell
    },

    # =========================================================
    # CYCLING DOMAIN
    # =========================================================
    "cycling": {
        "sport": "cycling",
        
        # Categories -> Unique Stages -> Seasons -> Stages (Cycling)
        "stages": [
            {
                "category_id": 1458, # International
                "unique_stage_id": 9, # Cycling Men
                "stage_season_id": 220825, # 2026
                "stage_id": 220828, # Tour de France
            },
            {
                "category_id": 1458, # International
                "unique_stage_id": 9, # Cycling Men
                "stage_season_id": 210189, # 2025
                "stage_id": 210217, # Tour de France
            },
            {
                "category_id": 1458, # International
                "unique_stage_id": 9, # Cycling Men
                "stage_season_id": 220825, # 2026
                "stage_id": 220923, # Tour de France Stage 3
            },
        ],
        "teams": [],
    },

    # =========================================================
    # MISCELLANEOUS & ERRORS
    # =========================================================
    "misc": {
        "rankings": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 34, 35],
        "country_codes": ["FR", "GB", "NO"],
        "channels": [287, 42], # Canal+, Bein Sports 1
    },

    "errors": {
        "invalid_id": "99999999999999",
        "invalid_date": "2026-15-99",
    }
}