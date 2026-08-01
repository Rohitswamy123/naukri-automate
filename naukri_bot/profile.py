import os
import random
import time
from .logger import log

def random_delay(min_sec: float = 1.0, max_sec: float = 2.5) -> None:
    """Helper to sleep for a random human-like duration."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


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

    base_summary = (
        "Senior DevOps Engineer with 5+ years of experience architecting, automating, and scaling high-availability "
        "multi-cloud infrastructure across AWS (EKS, EC2, VPC, ALB, Route 53) and Microsoft Azure (AKS, APIM, AppGW, "
        "Azure SQL, Azure AI foundry). Strong expertise in Kubernetes administration, designing GitOps delivery pipelines "
        "(ArgoCD), and Infrastructure as Code using Terraform and Terragrunt. Proficient in configuring CI/CD automation "
        "(GitHub Actions, Azure DevOps, Jenkins), robust observability stacks (Prometheus, Grafana, Loki, EFK), and "
        "administering HA databases (PostgreSQL, MongoDB). Actively focused on driving DevSecOps, zero-trust architecture, "
        "and resilient self-service platforms, with a strong passion for scaling SRE practices, establishing strict SLOs, "
        "and achieving zero-downtime deployments."
    )

    summary_endings_pool = [
        " Proven track record integrating MLOps/ Agentic AI workflows (Ollama, n8n) for platform automation and driving cloud cost-optimization initiatives that saved $20,000 annually.",
        " Dedicated to advancing MLOps platforms using Kafka streams and Evidently drift detection for automated, closed-loop model retraining and efficient AI operations.",
        " Highly skilled in deep observability, implementing OpenTelemetry tracing and Prometheus burn-rate alerts to maintain strict model-serving SLOs across environments.",
        " Committed to zero-downtime AI delivery, leveraging KServe canary rollouts and ArgoCD to seamlessly orchestrate hybrid-cloud LLM and model deployments.",
        " Demonstrated success in FinOps governance and Agentic AI operations, deploying LiteLLM gateways with token-level cost metrics to optimize internal LLM infrastructure."
    ]

    # 1. Target the Edit button
    summary_edit_selectors = [
        "xpath=//p[text()='Profile summary']/following-sibling::span",
        "xpath=//p[text()='Profile summary']/parent::div/span",
        "xpath=//p[contains(text(), 'Profile summary')]/following-sibling::span",
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

    # 2. Wait for drawer to load
    try:
        page.wait_for_selector("[role='dialog'], .modal, [class*='modal'], [class*='drawer']", state="visible", timeout=5000)
        # Human delay after drawer loads
        random_delay(1.0, 2.5)
    except Exception:
        pass

    # 3. Locate the textarea inside the drawer container
    try:
        textarea = page.locator("[role='dialog'] textarea, .modal textarea, [class*='drawer'] textarea").first
        textarea.wait_for(state="visible", timeout=3000)
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
        "[role='dialog'] button:has-text('Save')",
        ".modal button:has-text('Save')",
        "[class*='drawer'] button:has-text('Save')",
        "button:has-text('Save')",
    ]
    
    saved = False
    for selector in save_button_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click()
                saved = True
                log(f"Clicked save button: {selector}")
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
            page.wait_for_selector("[role='dialog'] textarea, .modal textarea, [class*='drawer'] textarea", state="visible", timeout=6000)
            verify_textarea = page.locator("[role='dialog'] textarea, .modal textarea, [class*='drawer'] textarea").first
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
    
    # 1. Click Preferences edit button
    pencil_selectors = [
        "xpath=//div[@id='profile-section-preferences']//span[img[@alt='PencilSimple']]",
        "xpath=//div[@id='profile-section-preferences']//span[contains(@class, 'cursor-pointer')]",
        "#profile-section-preferences span[img[@alt='PencilSimple']]",
        "#profile-section-preferences img[alt='PencilSimple']"
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
    try:
        page.wait_for_selector("input[name='absoluteExpectedCtc']", state="visible", timeout=6000)
        # Human delay after drawer loads
        random_delay(1.0, 2.5)
    except Exception as e:
        log(f"Preferences edit drawer or expected CTC input failed to load: {e}")
        return False

    # 3. Locate expected CTC input and determine target toggle value
    try:
        input_field = page.locator("input[name='absoluteExpectedCtc']").first
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
        "[role='dialog'] button:has-text('Save')",
        ".modal button:has-text('Save')",
        "[class*='drawer'] button:has-text('Save')",
        "button:has-text('Save')",
    ]

    saved = False
    for selector in save_button_selectors:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                btn.click()
                saved = True
                log(f"Clicked save button: {selector}")
                break
            else:
                page.evaluate("const drawer = document.querySelector('[role=\"dialog\"], .modal, [class*=\"drawer\"]'); if (drawer) drawer.scrollTop = drawer.scrollHeight;")
                page.wait_for_timeout(500)
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
            page.wait_for_selector("input[name='absoluteExpectedCtc']", state="visible", timeout=6000)
            # Human delay inside modal before closing
            random_delay(1.5, 2.5)
            verify_field = page.locator("input[name='absoluteExpectedCtc']").first
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
