from PyStoreJSONLib import PyStoreManager

store = PyStoreManager("./data")

def get_config(guild_id: int):
    db = store.get_database(f"{guild_id}/ServerInfo")
    rows = db.get_all()
    return rows[0] if rows else None

def set_config(guild_id: int, config: dict):
    db = store.get_database(f"{guild_id}/ServerInfo")
    if not db.get_all():
        db.insert(config)
    else:
        db.update_by("Guild ID", guild_id, config)

def get_leaderboard(guild_id: int):
    db = store.get_database(f"{guild_id}/Leaderboard")
    return db.sort("Mentions", reverse=True)

def set_leaderboard(guild_id: int, leaderboard: list):
    db = store.get_database(f"{guild_id}/Leaderboard")
    for row in leaderboard:
        db.insert(row)
