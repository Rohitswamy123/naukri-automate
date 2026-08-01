from .logger import log


def click_first_visible(page, selectors, timeout: int = 1500) -> bool:
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=timeout):
                element.scroll_into_view_if_needed(timeout=3000)
                try:
                    element.click(timeout=3000)
                except Exception:
                    element.evaluate("el => el.click()")
                log(f"Clicked using selector: {selector}")
                return True
        except Exception:
            continue
    return False


def fill_first_visible_input(page, selectors, value: str, timeout: int = 1200) -> bool:
    for selector in selectors:
        try:
            field = page.locator(selector).first
            if field.is_visible(timeout=timeout):
                field.fill(value)
                actual = field.input_value().strip()
                if actual == value.strip():
                    log(f"Filled input using selector: {selector}")
                    return True
        except Exception:
            continue
    return False


def get_visible_edit_container(page):
    container_selectors = [
        "[role='dialog']",
        ".modal",
        "[class*='modal']",
        "[class*='drawer']",
        "[class*='popup']",
    ]
    for selector in container_selectors:
        try:
            container = page.locator(selector).last
            if container.is_visible(timeout=1200):
                return container
        except Exception:
            continue
    return None


def click_save_if_visible(page) -> bool:
    save_candidates = [
        "button:has-text('Save')",
        "button:has-text('Save changes')",
        "input[value='Save']",
        "button[class*='save']",
        "button[data-ga-track*='save']",
    ]
    for selector in save_candidates:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=2000):
                button.scroll_into_view_if_needed(timeout=3000)
                try:
                    button.click(timeout=3000)
                except Exception:
                    button.evaluate("el => el.click()")
                page.wait_for_load_state("load")
                log(f"Clicked save button using selector: {selector}")
                return True
        except Exception:
            continue
    return False


def click_modal_save_with_scroll(page) -> bool:
    modal_save_candidates = [
        "[role='dialog'] button:has-text('Save')",
        "[role='dialog'] button:has-text('Save changes')",
        ".modal button:has-text('Save')",
        "[class*='modal'] button:has-text('Save')",
    ]

    for _ in range(6):
        if click_first_visible(page, modal_save_candidates):
            return True

        try:
            page.evaluate(
                """
                () => {
                    const modal = document.querySelector('[role="dialog"], .modal, [class*="modal"]');
                    if (modal) modal.scrollTop = modal.scrollHeight;
                    window.scrollBy(0, 500);
                }
                """
            )
        except Exception:
            pass

        page.wait_for_timeout(500)

    return False


def click_save_in_container(page, container) -> bool:
    save_selectors = [
        "button:has-text('Save')",
        "button:has-text('Save changes')",
        "button:has-text('Update')",
        "input[type='submit']",
        "[role='button']:has-text('Save')",
        "[role='button']:has-text('Update')",
    ]

    for _ in range(6):
        for selector in save_selectors:
            try:
                btn = container.locator(selector).first
                if btn.is_visible(timeout=800):
                    btn.scroll_into_view_if_needed(timeout=3000)
                    try:
                        btn.click(timeout=3000)
                    except Exception:
                        btn.evaluate("el => el.click()")
                    log(f"Clicked container save using selector: {selector}")
                    return True
            except Exception:
                continue

        try:
            container.evaluate("el => { el.scrollTop = el.scrollHeight; }")
        except Exception:
            pass
        page.wait_for_timeout(400)

    return False


def click_personal_details_edit(page) -> bool:
    precise_candidates = [
        "section:has-text('Personal details') button:has-text('Edit')",
        "section:has-text('Personal Details') button:has-text('Edit')",
        "section:has-text('Personal details') a:has-text('Edit')",
        "section:has-text('Personal Details') a:has-text('Edit')",
        "div:has-text('Personal details') button:has-text('Edit')",
        "div:has-text('Personal Details') button:has-text('Edit')",
        "div:has-text('Name') button:has-text('Edit')",
        "div:has-text('Name') a:has-text('Edit')",
        "[data-ga-track*='personal'] [class*='edit']",
    ]

    try:
        page.evaluate("window.scrollTo(0, 0)")
    except Exception:
        pass

    for _ in range(10):
        if click_first_visible(page, precise_candidates, timeout=1000):
            return True

        card_headings = [
            "Personal details",
            "Personal Details",
            "Name",
            "Basic details",
            "Basic Details",
        ]
        card_scoped_edit_selectors = [
            "button:has-text('Edit')",
            "a:has-text('Edit')",
            "button[aria-label*='Edit']",
            "[role='button'][aria-label*='Edit']",
            "[class*='edit'][role='button']",
            "[class*='icon'][class*='edit']",
        ]
        for heading in card_headings:
            card_candidates = [
                f"section:has-text('{heading}')",
                f"div:has-text('{heading}')",
                f"article:has-text('{heading}')",
            ]
            for card_selector in card_candidates:
                try:
                    card = page.locator(card_selector).first
                    if not card.is_visible(timeout=500):
                        continue
                    for edit_selector in card_scoped_edit_selectors:
                        try:
                            edit_btn = card.locator(edit_selector).first
                            if edit_btn.is_visible(timeout=500):
                                edit_btn.scroll_into_view_if_needed(timeout=3000)
                                try:
                                    edit_btn.click(timeout=3000)
                                except Exception:
                                    edit_btn.evaluate("el => el.click()")
                                log(
                                    "Clicked Personal Details card edit "
                                    f"using selector: {card_selector} >> {edit_selector}"
                                )
                                return True
                        except Exception:
                            continue
                except Exception:
                    continue

        try:
            page.evaluate("window.scrollBy(0, 450)")
        except Exception:
            pass
        page.wait_for_timeout(350)

    return False
