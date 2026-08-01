import os
import time

import schedule
from playwright.sync_api import sync_playwright

from .auth import login_and_save_session
from .browser import XvfbDisplay, open_offscreen_browser
from .logger import log
from .profile import has_profile_access, open_profile, touch_profile_summary_space, touch_expected_salary_toggle
import random


def _run_update(config: dict) -> None:
    session_file = config["session_file"]

    with XvfbDisplay(), sync_playwright() as p:
        if not os.path.exists(session_file):
            log("No session file found — performing initial login...")
            login_and_save_session(p, config)

        log(f"Using saved session from {session_file}")
        browser, context, page = open_offscreen_browser(p, session_file)
        try:
            if not has_profile_access(page, config["profile_url"]):
                log("Session expired — re-logging in...")
                context.close()
                browser.close()
                login_and_save_session(p, config)

                browser, context, page = open_offscreen_browser(p, session_file)
                open_profile(page, config["profile_url"])

                if not has_profile_access(page, config["profile_url"]):
                    raise RuntimeError(
                        "Could not access profile page after re-login. "
                        "Check credentials or Naukri anti-bot restrictions."
                    )

            # Define available touch strategies
            actions = [
                ("Profile Summary Space Toggle", lambda pg, url: touch_profile_summary_space(pg, url)),
                ("Expected Salary Toggle", lambda pg, url: touch_expected_salary_toggle(pg, url))
            ]
            
            action_name, action_fn = random.choice(actions)
            log(f"Selected profile touch action: '{action_name}'")
            ok = action_fn(page, config["profile_url"])

            if ok:
                log("Profile touch update completed successfully.")
            else:
                log("Profile touch update action failed.")
        finally:
            context.close()
            browser.close()


def run_once_safe(config: dict) -> None:
    log("Starting one update cycle...")
    try:
        _run_update(config)
    except Exception as exc:
        log(f"Update failed with error: {exc}")


def plan_daily_updates(config: dict) -> None:
    log("Planning daily random touch times...")
    # Clear any previous scheduled profile touch jobs to prevent duplicate pile-up
    schedule.clear("profile-touch-job")

    # Random minute in 09:00 AM - 10:00 AM window
    morning_min = random.randint(0, 59)
    morning_time = f"09:{morning_min:02d}"

    # Random minute in 05:00 PM - 06:00 PM window (17:00 - 18:00)
    evening_min = random.randint(0, 59)
    evening_time = f"17:{evening_min:02d}"

    log(f"Today's scheduled touch times: Morning at {morning_time}, Evening at {evening_time}")

    schedule.every().day.at(morning_time).do(run_once_safe, config=config).tag("profile-touch-job")
    schedule.every().day.at(evening_time).do(run_once_safe, config=config).tag("profile-touch-job")


def scheduler_loop(config: dict) -> None:
    every_minutes = config.get("every_minutes")
    update_at = config.get("update_at")
    random_twice = config.get("random_twice")

    if random_twice:
        log("Random daily twice mode enabled (9:00-10:00 AM & 5:00-6:00 PM).")
        # Schedule the daily planner to run every day at 00:05 AM
        schedule.every().day.at("00:05").do(plan_daily_updates, config=config)
        # Call it immediately on boot to schedule today's runs
        plan_daily_updates(config)
    elif every_minutes:
        minutes = int(every_minutes)
        log(f"Scheduling update every {minutes} minute(s).")
        schedule.every(minutes).minutes.do(run_once_safe, config=config)
    else:
        log(f"Scheduling daily update at {update_at}.")
        schedule.every().day.at(update_at).do(run_once_safe, config=config)

    log("Running first update immediately...")
    run_once_safe(config)

    log("Scheduler started. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)
