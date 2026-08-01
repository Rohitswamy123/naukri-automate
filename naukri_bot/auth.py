from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .browser import open_offscreen_browser
from .logger import log


def accept_cookie_if_present(page) -> None:
    selectors = [
        "button:has-text('Accept')",
        "button:has-text('I Accept')",
        "button:has-text('Got it')",
        "button:has-text('Allow All')",
    ]
    for selector in selectors:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=1500):
                button.click(timeout=1500)
                log("Cookie banner handled.")
                return
        except Exception:
            continue


def login(page, email: str, password: str) -> None:
    log("Opening Naukri login page...")
    page.goto("https://www.naukri.com/nlogin/login", wait_until="load")
    accept_cookie_if_present(page)

    email_selectors = [
        "input[placeholder*='Email']",
        "input[placeholder*='Username']",
        "input[name='usernameField']",
        "input[id='usernameField']",
        "input[name*='user']",
        "input[id*='user']",
        "input[type='email']",
        "input[autocomplete='username']",
    ]
    password_selectors = [
        "input[placeholder*='password']",
        "input[type='password']",
        "input[name*='password']",
        "input[id='passwordField']",
        "input[id*='pass']",
        "input[autocomplete='current-password']",
    ]
    submit_selectors = [
        "button[type='submit']",
        "button:has-text('Login')",
        "button:has-text('Sign in')",
        "button:has-text('Continue')",
        "input[type='submit']",
    ]

    def fill_first_visible(selectors, value: str, field_name: str) -> bool:
        for selector in selectors:
            try:
                field = page.locator(selector).first
                if field.is_visible(timeout=1500):
                    field.fill(value, timeout=4000)
                    return True
            except Exception:
                continue
        log(f"Could not find {field_name} field with current selectors.")
        return False

    if not fill_first_visible(email_selectors, email, "email/username"):
        log("Trying homepage login flow...")
        page.goto("https://www.naukri.com/", wait_until="load")
        accept_cookie_if_present(page)
        login_openers = [
            "a:has-text('Login')",
            "button:has-text('Login')",
            "a[href*='nlogin']",
            "[title*='Login']",
        ]
        for selector in login_openers:
            try:
                opener = page.locator(selector).first
                if opener.is_visible(timeout=1200):
                    opener.click(timeout=3000)
                    page.wait_for_load_state("load")
                    break
            except Exception:
                continue

        if not fill_first_visible(email_selectors, email, "email/username"):
            raise RuntimeError(
                "Could not find email/username field on login page. "
                "Likely captcha/anti-bot or UI changed. Run with HEADLESS=false and login manually once."
            )

    if not fill_first_visible(password_selectors, password, "password"):
        raise RuntimeError(
            "Could not find password field on login page. "
            "Run with HEADLESS=false and update selectors in auth.py."
        )

    clicked_submit = False
    for selector in submit_selectors:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=1500):
                button.click(timeout=4000)
                clicked_submit = True
                break
        except Exception:
            continue

    if not clicked_submit:
        raise RuntimeError(
            "Could not find login submit button. "
            "Run with HEADLESS=false and update selectors in auth.py."
        )

    try:
        page.wait_for_url("**naukri.com/**", timeout=15000)
    except PlaywrightTimeoutError:
        pass

    page.wait_for_load_state("load")

    if "login" in page.url.lower():
        raise RuntimeError(
            "Login appears unsuccessful. Check credentials or complete captcha/2FA manually."
        )

    log("Login successful.")


def login_and_save_session(p, config: dict) -> None:
    """Login via off-screen browser and persist session to disk."""
    session_file = config["session_file"]
    log("Opening off-screen browser to perform login...")
    browser, context, page = open_offscreen_browser(p)
    try:
        login(page, config["email"], config["password"])
        context.storage_state(path=session_file)
        log(f"Session saved to {session_file}")
    finally:
        context.close()
        browser.close()
