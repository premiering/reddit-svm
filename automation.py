import time
from playwright.sync_api import sync_playwright
import reddit

# Web automation for screenshots of Reddit posts
# todo, some clean up

def take_post_screenshot(id: str, url: str, output_file: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=reddit.REDDIT_USER_AGENT)
        # set dark mode
        ctx.add_cookies([{"name": "theme", "value": "2", "domain": "www.reddit.com", "path": "/"}])
        page = ctx.new_page()
        page.goto(url)
        time.sleep(2)

        try:
            close_popup_btn = page.locator("[id=secondary-button]")
            if close_popup_btn.count() > 0:
                close_popup_btn.click()
                time.sleep(0.1)
        except Exception:
            pass

        page.locator(f"[id=t3_{id}]").screenshot(path=output_file)
        browser.close()

def take_comment_screenshot(url: str, output_path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=reddit.REDDIT_USER_AGENT)
        # set dark mode
        ctx.add_cookies([{"name": "theme", "value": "2", "domain": "www.reddit.com", "path": "/"}])
        ctx.set_default_timeout(5000)
        page = ctx.new_page()
        page.goto(url)
        time.sleep(2)

        # closes the nsfw popup via the close button if it exists
        try:
            close_popup_btn = page.locator("[id=secondary-button]")
            if close_popup_btn.count() > 0:
                close_popup_btn.click()
                time.sleep(0.1)
        except Exception:
            pass

        # unexpand the comment we're taking a screenshot of (so comments of this comment don't show)
        try: 
            collapse_btn = page.get_by_label("Toggle Comment Thread")
            if collapse_btn.count() > 0:
                collapse_btn.nth(0).click()
                time.sleep(0.1)
        except Exception:
            pass

        page.locator(f"[thingid=t1_{(url[-8:])[:-1]}]").nth(1).screenshot(
            path=output_path
        )
        browser.close()