import os
from playwright.sync_api import sync_playwright
from naukri_bot.config import read_env

def run():
    try:
        cfg = read_env()
    except Exception as e:
        print(f"Error reading .env: {e}")
        cfg = {"session_file": "naukri_session.json"}
    
    session_file = cfg.get("session_file", "naukri_session.json")
    print(f"Target session file path: {session_file}")
    
    # If the file exists, we will delete/overwrite it.
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            print(f"Removed old/invalid session file: {session_file}")
        except Exception as e:
            print(f"Warning: Could not remove existing session file: {e}")
            
    with sync_playwright() as p:
        print("Launching visible browser on screen...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("Opening Naukri login page...")
        page.goto("https://www.naukri.com/nlogin/login")
        
        print("\n" + "="*70)
        print("ACTION REQUIRED:")
        print("1. A browser window has opened on your screen.")
        print("2. Log in manually (enter email, password, solve captchas, or complete OTP).")
        print("3. Once you are successfully logged in and are on the dashboard/profile page:")
        print("   Come back to this terminal and press ENTER.")
        print("="*70 + "\n")
        
        input("Press Enter here once you are logged in and on the profile dashboard page... ")
        
        # Save cookies & state
        context.storage_state(path=session_file)
        print(f"\nSuccess! Playwright session state saved to: {session_file}")
        print("You can now close the browser window and run 'python main.py'.\n")
        
        context.close()
        browser.close()

if __name__ == "__main__":
    run()
