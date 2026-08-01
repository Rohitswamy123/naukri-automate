import os

from dotenv import load_dotenv


def as_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def read_env() -> dict:
    load_dotenv()

    email = os.getenv("NAUKRI_EMAIL", "").strip()
    password = os.getenv("NAUKRI_PASSWORD", "").strip()
    profile_url = os.getenv(
        "PROFILE_URL",
        "https://www.naukri.com/mnjuser/profile",
    ).strip()
    every_minutes = os.getenv("UPDATE_EVERY_MINUTES", "").strip()
    update_at = os.getenv("UPDATE_AT_HHMM", "").strip()
    session_file = os.getenv("SESSION_FILE", "naukri_session.json").strip()
    random_twice = os.getenv("RANDOM_DAILY_TWICE", "").strip().lower() in {"1", "true", "yes", "y", "on"}

    if not email or not password:
        raise ValueError("Please set NAUKRI_EMAIL and NAUKRI_PASSWORD in .env")

    # If random daily twice is enabled, we don't strictly require the other schedules
    if not random_twice:
        if every_minutes and update_at:
            raise ValueError("Set only one of UPDATE_EVERY_MINUTES or UPDATE_AT_HHMM")
        if not every_minutes and not update_at:
            every_minutes = "240"

    return {
        "email": email,
        "password": password,
        "profile_url": profile_url,
        "every_minutes": every_minutes if not random_twice else "",
        "update_at": update_at if not random_twice else "",
        "session_file": session_file,
        "random_twice": random_twice,
    }
