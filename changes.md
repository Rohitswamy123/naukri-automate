# Changes from Original Naukri Automate Codebase

This document tracks all the modifications made to shift the bot's behavior from name capitalization cycling to invisible updates on other profile sections.

---

## Completed Modifications

### 1. Removed Name Capitalization Cycling
*   **Target Files:**
    *   [naukri_bot/config.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/config.py)
    *   [naukri_bot/profile.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/profile.py)
    *   [naukri_bot/scheduler.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/scheduler.py)
    *   [.env](file:///Users/rohit/Desktop/projects/naukri_automate/.env)
*   **Changes:**
    *   Removed `ENABLE_RANDOM_NAME_UPDATE`, `NAME_VARIANTS`, and `NAME_STATE_FILE` configurations from `.env` and `naukri_bot/config.py`.
    *   Removed functions `update_name_alternating()`, `get_next_name()`, `verify_name_saved()`, and `touch_profile_save()` from `naukri_bot/profile.py`.

### 2. Implemented Profile Summary Period Toggling
*   **Target Files:**
    *   [naukri_bot/profile.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/profile.py)
*   **Changes:**
    *   Implemented `touch_profile_summary_space(page, profile_url)`. It locates the Profile Summary card using TopTier header selectors, clicks Edit, reads the textarea, toggles a trailing period (dot), clicks Save, and reloads to verify the update. This bypasses database-level string trimming filters.

### 3. Implemented Expected Salary (Expected CTC) Toggling
*   **Target Files:**
    *   [naukri_bot/profile.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/profile.py)
*   **Changes:**
    *   Implemented `touch_expected_salary_toggle(page, profile_url)`.
    *   Locates the Preferences Edit button, waits for the Expected CTC input to become visible, and toggles the salary value:
        *   If it is `40,00,000`, it changes it to `42,00,000`.
        *   If it is `42,00,000`, it changes it to `40,00,000`.
        *   Otherwise, it defaults to `40,00,000`.
    *   Uses Playwright's native `select_text()` method to clear the field platform-independently and types the new value.

### 4. Integrated Randomized Touches
*   **Target Files:**
    *   [naukri_bot/scheduler.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/scheduler.py)
*   **Changes:**
    *   Modified the background update loop `_run_update()` to randomly select between **Profile Summary Space Toggle** or **Expected Salary Toggle** on each run cycle.

### 5. Implemented Randomized Twice Daily Scheduling Mode
*   **Target Files:**
    *   [naukri_bot/config.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/config.py)
    *   [naukri_bot/scheduler.py](file:///Users/rohit/Desktop/projects/naukri_automate/naukri_bot/scheduler.py)
    *   [.env](file:///Users/rohit/Desktop/projects/naukri_automate/.env)
*   **Changes:**
    *   Added configurable `RANDOM_DAILY_TWICE=true` setting.
    *   When enabled, it executes a daily planner job (`plan_daily_updates`) every day at `00:05 AM` (and immediately on startup).
    *   This planner dynamically calculates two randomized touch execution times:
        *   **Morning Window:** A random minute between `09:00 AM` and `10:00 AM` (e.g. `09:42`).
        *   **Evening Window:** A random minute between `05:00 PM` and `06:00 PM` (e.g. `17:18`).
    *   Registers those two dynamic times to execute for that day, completely breaking any static periodicity signature.

---

## Verification & Testing History
*   **Profile Summary Period Toggle Test:** Verified successfully. Modal loaded, trailing period (dot) was toggled, saved, and successfully reloaded/verified.
*   **Expected Salary Toggle Test:** Verified successfully. Modal loaded, read current expected CTC value as `4,40,00,000` (from a truncated manual typing test), cleared it cleanly using `select_text()`, successfully typed `4200000`, clicked Save, and reload-verified it as `4200000` inside the preferences drawer.
*   **Dynamic Scheduler Test:** Configured and compiled successfully.
