# Naukri Profile Automator

Automates periodic profile updates on Naukri to keep your profile active and highly visible to recruiters. 

Instead of traditional name-capitalization cycling (which is easily flagged), this bot implements realistic, human-paced profile updates to trigger Naukri's search-ranking algorithm.

---

## Key Features

1. **Profile Summary Endings Rotator:** 
   * Predefines a pool of custom concluding sentences tailored to your career domain.
   * Reads your live summary, detects which ending is currently active, and replaces it with a different ending from your pool.
   * Uses a base summary to guarantee the total text **never exceeds Naukri's 1,000-character limit** and never corrupts.
2. **Expected Salary (CTC) Pool Toggle:**
   * Rotates your expected salary dynamically between a range of values (e.g. standard brackets).
   * Filters out your current active salary from the pool before choosing, ensuring a change is always made.
3. **Dynamic Twice-Daily Scheduler:**
   * Runs the scheduler loop. Every day at 12:05 AM, it calculates two randomized execution times for the day:
     * **Morning Window:** A random minute between `09:00 AM – 10:00 AM`.
     * **Evening Window:** A random minute between `05:00 PM – 06:00 PM` (17:00 – 18:00).
   * Dynamically registers these times to break any static update pattern.
4. **Anti-Detection Evasion Mechanics:**
   * **Off-Screen Rendering:** Launches Chromium off-screen (at position `-32000,-32000`) so it doesn't steal focus from your screen or disrupt your work.
   * **Virtual Display Framebuffer (Xvfb):** Runs Playwright visibly inside a headless Linux/Docker container, successfully bypassing "true headless" bot detection.
   * **Organic Pacing & Delays:** Introduces natural delays (1.0 to 3.0 seconds) between clicks and typing, and types inputs character-by-character with random keyboard delay (150ms–300ms) to emulate human speed.
   * **Session File Persistence:** Saves login cookies into a `naukri_session.json` state. Once authenticated, subsequent runs use the saved session to bypass captchas, emails, and passwords completely.

---

## Project Structure

```text
naukri_bot/
├── config.py       — reads .env configurations and schedules
├── logger.py       — formatted timestamped logger
├── browser.py      — Chromium launch, offscreen positioner, Xvfb display server
├── auth.py         — login credentials handler & session persistence
├── profile.py      — SRE summary rotation and Expected CTC pool toggler logic
└── scheduler.py    — daily planner, loop triggers, and scheduler logic
main.py             — app entry point
Dockerfile          — Docker build file
docker-compose.yml  — Docker Compose configuration
```

---

## Setup & Local Installation

### 1. Requirements
* Python 3.10+
* Playwright

### 2. Installation
Create a virtual environment and install packages:
```bash
python3 -m venv .venv
source .venv/bin/activate

#for windows
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
NAUKRI_EMAIL=your_email@example.com
NAUKRI_PASSWORD=your_password_here

# Scheduling Configuration
RANDOM_DAILY_TWICE=true
# (Alternatively, for traditional schedules)
# UPDATE_EVERY_MINUTES=240
# UPDATE_AT_HHMM=09:30

# Optional URL & Session Caching override
# PROFILE_URL=https://www.naukri.com/mnjuser/profile
# SESSION_FILE=naukri_session.json
```

### 4. Running Locally
Run the scheduler:
```bash
python main.py
```
On the first run, the script will open Chromium, prompt you to log in (if cookies are missing), save the session, and perform its initial update.

---

## Docker Deployment (Recommended)

Docker is the easiest way to run the bot 24/7. It handles all virtual displays (`Xvfb`), Chromium dependencies, and scheduling automatically.

### 1. Pre-requisites
Make sure you have logged in locally once to generate `naukri_session.json` in your local directory (this avoids resolving Captchas inside the headless container).

### 2. Prepare Session Folder
Create a data folder and copy your session file into it:
```bash
mkdir -p data
cp naukri_session.json data/
```

### 3. Launch Docker Container
Build and start the container in detached mode:
```bash
docker-compose up -d --build
```

### 4. View Status & Container Logs
Follow the logs to verify execution:
```bash
docker-compose logs -f
```

### 5. Stop the Container
To turn off the background service:
```bash
docker-compose down
```

---

## Disclaimer
Please use this tool responsibly. Automating actions on web platforms should comply with terms of service.
