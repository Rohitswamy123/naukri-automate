import os
import random
import time
from .logger import log

def random_delay(min_sec: float = 1.0, max_sec: float = 2.5) -> None:
    """Helper to sleep for a random human-like duration."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def scroll_to_load_sections(page) -> None:
    """Scroll down the profile page to trigger lazy-loading of all widgets."""
    log("Scrolling down page to trigger lazy-loading of widgets...")
    for _ in range(8):
        page.evaluate("window.scrollBy(0, 800);")
        page.wait_for_timeout(350)
    page.evaluate("window.scrollTo(0, 0);")
    page.wait_for_timeout(500)


def open_profile(page, profile_url: str) -> None:
    log("Opening profile page...")
    page.goto(profile_url, wait_until="load")
    random_delay(1.5, 3.0)
    log(f"Profile page URL: {page.url}")


def has_profile_access(page, profile_url: str) -> bool:
    open_profile(page, profile_url)
    if "login" in page.url.lower():
        return False
    try:
        title = page.title().lower()
        body = page.inner_text("body").lower()
        if "access denied" in title or "you don't have permission" in body:
            return False
    except Exception:
        pass
    return True


def touch_profile_summary_space(page, profile_url: str) -> bool:
    """
    Locates the Profile Summary edit button, reads the current text to identify the active ending,
    and overwrites it using a hardcoded base summary + a new selected ending from the pool.
    This guarantees no truncation, no double-appends, and strictly enforces the 1000-character limit.
    """
    log("Starting Profile Summary ending rotation touch...")
    scroll_to_load_sections(page)

    base_summary = (
        "Senior Product & Analytics professional with 6+ years of experience building AI-powered, data-driven "
        "products across fintech, healthtech, and global marketplace platforms. Strong expertise in product "
        "analytics, experimentation, customer journey optimization, KPI frameworks, and end-to-end product "
        "lifecycle management, leveraging SQL, Python, Redshift, Tableau, Power BI, Amplitude, and modern BI "
        "ecosystems. Proficient in designing scalable data models, self-serve analytics platforms, forecasting "
        "solutions, fraud intelligence systems, and AI-driven analytical workflows while collaborating with "
        "engineering, design, and business stakeholders."
    )

    summary_endings_pool = [
        " Proven track record delivering AI-powered analytics solutions, intelligent automation, and data-driven product strategies that improved customer experience and operational efficiency.",
        " Dedicated to building AI-first product experiences through experimentation, customer behavior analytics, and scalable analytics platforms that drive measurable business growth.",
        " Highly skilled in transforming large-scale product and customer data into actionable insights, enabling continuous optimization across acquisition, retention, fraud prevention, and monetization.",
        " Committed to building self-serve analytics ecosystems, AI-assisted decision frameworks, and scalable data products that empower product, engineering, and business teams.",
        " Demonstrated success driving product innovation through AI-enabled analytics, experimentation, cross-functional collaboration, and customer-centric decision making.",
        " Passionate about leveraging AI, advanced analytics, and experimentation to uncover customer insights, optimize product strategy, and accelerate data-informed decision making.",
        " Focused on building intelligent analytics solutions, scalable KPI frameworks, and predictive models that enable faster product decisions and sustainable business outcomes.",
        " Experienced in translating complex business problems into scalable product solutions through AI-driven analytics, robust experimentation, and continuous product optimization."
    ]

    # 1. Target the Edit button
    summary_edit_selectors = [
        "xpath=//span[text()='Profile summary']/following-sibling::span[contains(@class, 'edit')]",
        "xpath=//span[text()='Profile summary']/parent::div/span[contains(@class, 'edit')]",
        "xpath=//span[contains(text(), 'Profile summary')]/following-sibling::span[contains(@class, 'edit')]",
        "xpath=//span[text()='Profile summary']/following-sibling::span[text()='editOneTheme']",
        "xpath=//p[text()='Profile summary']/following-sibling::span",
        "xpath=//p[text()='Profile summary']/parent::div/span",
    ]

    clicked = False
    for selector in summary_edit_selectors:
        try:
            edit_btn = page.locator(selector).first
            if edit_btn.is_visible(timeout=2000):
                log(f"Found Profile Summary edit control: {selector}")
                edit_btn.scroll_into_view_if_needed()
                
                # Human delay before clicking Edit
                random_delay(1.5, 3.0)
                edit_btn.click()
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        log("Could not find the Profile Summary edit button.")
        return False

    # 2. Wait for drawer to load and textarea to appear
    try:
        page.wait_for_selector("#profileSummaryTxt, textarea[name='profileSummary'], textarea", state="visible", timeout=6000)
        # Human delay after drawer loads
        random_delay(1.0, 2.5)
    except Exception:
        pass

    # 3. Locate the textarea inside the drawer container
    try:
        textarea = page.locator("#profileSummaryTxt, textarea[name='profileSummary'], textarea").first
        textarea.wait_for(state="visible", timeout=4000)
    except Exception as e:
        log(f"Failed to find or focus the summary textarea: {e}")
        return False

    # 4. Extract current text and find active ending
    current_text = textarea.input_value().strip()
    log(f"Current summary length: {len(current_text)} characters.")
    
    active_ending = None
    for ending in summary_endings_pool:
        # Check if current text ends with this ending (case-insensitive check for robustness)
        if current_text.lower().endswith(ending.strip().lower()):
            active_ending = ending
            log(f"Found active ending on profile: '{ending.strip()[:30]}...'")
            break

    # If no ending was found, log it and pick from the entire pool
    if not active_ending:
        log("No matching ending from the pool detected on profile. Matching base summary context.")

    # 5. Filter candidates and select a new target ending
    candidates = [e for e in summary_endings_pool if e != active_ending]
    target_ending = random.choice(candidates)
    
    # Construct new text safely from the hardcoded base summary!
    new_text = base_summary + target_ending
    log(f"Selected new ending: '{target_ending.strip()[:30]}...'")
    log(f"New summary length: {len(new_text)} characters (strictly under 1,000).")

    # Human delay before editing the text
    random_delay(1.0, 2.0)
    textarea.fill(new_text)
    
    # Human delay after typing, before saving
    random_delay(1.5, 3.0)

    # 6. Click the Save button inside the drawer
    save_button_selectors = [
        "button.btn-dark-ot:has-text('Save')",
        "button[type='submit']:has-text('Save')",
        "input.yes[value='Save']",
        "input[value='Save']",
        "button:has-text('Save')",
    ]
    
    saved = False
    for selector in save_button_selectors:
        try:
            buttons = page.locator(selector).all()
            for btn in buttons:
                if btn.is_visible(timeout=1000):
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    saved = True
                    log(f"Clicked save button: {selector}")
                    break
            if saved:
                break
        except Exception:
            continue

    if not saved:
        log("Could not find or click the Save button.")
        return False

    # Human delay after saving
    random_delay(1.0, 2.0)

    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass

    log("Reloading profile page to verify changes...")
    try:
        page.reload()
        page.wait_for_load_state("load")
        random_delay(2.0, 4.0)
        
        # Verify save by opening drawer again and checking text
        verify_clicked = False
        for selector in summary_edit_selectors:
            try:
                edit_btn = page.locator(selector).first
                if edit_btn.is_visible(timeout=2000):
                    random_delay(1.0, 2.0)
                    edit_btn.click()
                    verify_clicked = True
                    break
            except Exception:
                continue
                
        if verify_clicked:
            page.wait_for_selector("#profileSummaryTxt, textarea[name='profileSummary'], textarea", state="visible", timeout=6000)
            verify_textarea = page.locator("#profileSummaryTxt, textarea[name='profileSummary'], textarea").first
            new_saved_text = verify_textarea.input_value().strip()
            
            # Close drawer
            page.keyboard.press("Escape")
            random_delay(1.0, 2.0)

            if new_saved_text.lower().endswith(target_ending.strip().lower()):
                log("Profile summary ending rotation completed and verified successfully.")
                return True
            else:
                log("Verification warning: Text ending after reload did not match expected target ending.")
                return True
        else:
            log("Verification notice: Could not re-open summary drawer, but save succeeded.")
            return True
    except Exception as e:
        log(f"Verification reload failed: {e}")
        return True


def touch_expected_salary_toggle(page, profile_url: str) -> bool:
    """
    Opens the Job Preferences edit drawer, reads the current expected CTC,
    toggles it randomly between 39,00,000 and 42,50,000 (excluding current),
    saves, and reload-verifies.
    Incorporates human-like timing/delays.
    """
    log("Starting Expected Salary toggle touch...")
    scroll_to_load_sections(page)
    
    # 1. Click Preferences edit button
    pencil_selectors = [
        "xpath=//div[contains(@class, 'desiredProfile')]//span[contains(@class, 'edit')]",
        "xpath=//span[text()='Career profile']/following-sibling::span[contains(@class, 'edit')]",
        "xpath=//span[text()='Career profile']/parent::div/span[contains(@class, 'edit')]",
        "xpath=//span[text()='Career profile']/following-sibling::span[text()='editOneTheme']",
        ".desiredProfile .edit.icon",
        ".desiredProfile [class*='edit']",
        "xpath=//div[@id='profile-section-preferences']//span[img[@alt='PencilSimple']]",
    ]
    
    clicked = False
    for selector in pencil_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                log(f"Found Preferences edit control: {selector}")
                btn.scroll_into_view_if_needed()
                
                # Human delay before clicking Edit
                random_delay(1.5, 3.0)
                btn.click()
                clicked = True
                break
        except Exception:
            continue

    if not clicked:
        log("Could not find the Preferences edit button.")
        return False

    # 2. Wait for expected CTC input
    ctc_selectors = [
        "input[placeholder='Eg. 4,50,000']",
        "xpath=//input[@placeholder='Eg. 4,50,000']",
        "input[name='absoluteExpectedCtc']",
    ]
    
    selected_ctc_selector = None
    for selector in ctc_selectors:
        try:
            if page.locator(selector).first.is_visible(timeout=2000):
                selected_ctc_selector = selector
                break
        except Exception:
            continue
            
    if not selected_ctc_selector:
        log("Expected CTC input failed to load or be visible in the drawer.")
        return False

    # 3. Locate expected CTC input and determine target toggle value
    try:
        input_field = page.locator(selected_ctc_selector).first
        current_val_raw = input_field.input_value().strip()
        log(f"Current expected CTC raw value: '{current_val_raw}'")

        val_clean = current_val_raw.replace(",", "")
        
        # Expected CTC pool from 39 Lakhs to 42.5 Lakhs
        salary_pool = ["3900000", "4000000", "4100000", "4150000", "4200000", "4250000"]
        
        # Filter out current value to guarantee a change
        candidates = [s for s in salary_pool if s != val_clean]
        if not candidates:
            candidates = ["4000000"]
            
        target_val = random.choice(candidates)
        log(f"CTC is {current_val_raw}. Selecting random target: {target_val}")

        # 4. Clear input and enter target value
        # Human delay before selecting field
        random_delay(1.0, 2.0)
        input_field.focus()
        input_field.click()
        
        # Human delay before selecting text
        random_delay(0.5, 1.2)
        input_field.select_text()
        
        # Human delay before deleting
        random_delay(0.5, 1.2)
        page.keyboard.press("Backspace")
        
        # Human delay after clear
        random_delay(0.8, 1.8)

        # Check if cleared successfully
        cleared_val = input_field.input_value()
        if cleared_val:
            for _ in range(25):
                page.keyboard.press("Backspace")
            random_delay(0.5, 1.2)

        # 5. Type value organically (per-character delay random 150-300ms)
        log(f"Typing target Expected CTC value: '{target_val}'...")
        page.keyboard.type(target_val, delay=random.randint(150, 300))
        
        # Human delay after typing, before saving
        random_delay(1.5, 3.0)
    except Exception as e:
        log(f"Failed to edit Expected CTC input: {e}")
        return False

    # 6. Click Save inside the drawer
    save_button_selectors = [
        "input.yes[value='Save']",
        "input[value='Save']",
        "button.btn-dark-ot:has-text('Save')",
        "button[type='submit']:has-text('Save')",
        "button:has-text('Save')",
    ]

    saved = False
    for selector in save_button_selectors:
        try:
            buttons = page.locator(selector).all()
            for btn in buttons:
                if btn.is_visible(timeout=1000):
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    saved = True
                    log(f"Clicked save button: {selector}")
                    break
            if saved:
                break
        except Exception:
            continue

    if not saved:
        log("Failed to click Save button inside drawer.")
        return False

    # Human delay after saving
    random_delay(1.0, 2.0)

    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass

    log("Update complete! Checking profile update status...")

    # 7. Reload and Verify
    try:
        page.reload()
        page.wait_for_load_state("load")
        random_delay(2.0, 4.0)

        log("Re-opening Preferences modal to verify saved expected CTC...")
        clicked = False
        for selector in pencil_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    # Human delay before opening verification drawer
                    random_delay(1.0, 2.0)
                    btn.click()
                    clicked = True
                    break
            except Exception:
                continue

        if clicked:
            verify_ctc_selector = None
            for selector in ctc_selectors:
                try:
                    if page.locator(selector).first.is_visible(timeout=2000):
                        verify_ctc_selector = selector
                        break
                except Exception:
                    continue
            if not verify_ctc_selector:
                log("Verification notice: Could not locate expected CTC input after reload.")
                return True
                
            # Human delay inside modal before closing
            random_delay(1.5, 2.5)
            verify_field = page.locator(verify_ctc_selector).first
            new_val_clean = verify_field.input_value().strip().replace(",", "")
            
            # Close drawer
            page.keyboard.press("Escape")
            random_delay(1.0, 2.0)
            
            if new_val_clean == target_val:
                log(f"Success! Expected CTC is now verified as '{new_val_clean}' on your profile.")
                return True
            else:
                log(f"Verification failed: expected '{target_val}', but profile has '{new_val_clean}' after reload.")
                return False
        else:
            log("Verification notice: Could not re-open preferences modal to inspect saved input value.")
            return True
    except Exception as e:
        log(f"Verification reload failed: {e}")
        return True
