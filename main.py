from naukri_bot.config import read_env
from naukri_bot.logger import log
from naukri_bot.scheduler import scheduler_loop

if __name__ == "__main__":
    try:
        cfg = read_env()
        scheduler_loop(cfg)
    except KeyboardInterrupt:
        log("Stopped by user.")
    except Exception as exc:
        log(f"Error: {exc}")
