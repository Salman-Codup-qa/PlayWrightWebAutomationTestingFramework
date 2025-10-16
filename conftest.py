import json
import os
import time
from pathlib import Path
from typing import Generator

import pytest
import allure

from pages.base_page import BasePage

from app_selectors.login_selectors import (
    LOGIN_TEXT,
    TITLE_TEXT,
    EMAIL_INPUT,
    CONTINUE_BUTTON,
    OTP_TEXT,
    OTP_INPUT,
    SUBMIT_BUTTON,
    ALERT_ERROR,
    DASHBOARD_HEADER,
    USER_MENU,
    LOGOUT_LINK,
    PROFILE_MENU,
    ERROR_ALERT,
)
from utils.google_utils import get_latest_email


# Directories for artifacts
RESULTS_DIR = Path("results")
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
VIDEOS_DIR = RESULTS_DIR / "videos"
TRACES_DIR = RESULTS_DIR / "traces"

# --- Auth state (storage) ---
AUTH_STATE_FILE = RESULTS_DIR / "auth.json"


for d in (RESULTS_DIR, SCREENSHOTS_DIR, VIDEOS_DIR, TRACES_DIR):
    d.mkdir(parents=True, exist_ok=True)


def pytest_addoption(parser):
    parser.addoption(
        "--record-video",
        action="store_true",
        default=False,
        help="Record video for each test (saved to results/videos).",
    )
    parser.addoption(
        "--recreate-auth",
        action="store_true",
        default=False,
        help="Force recreate the auth storage_state file (results/auth.json).",
    )
    # Note: pytest-playwright already provides --browser / --headed / --browser-channel etc.
    # We keep only options that complement plugin features here.


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot automatically on failure"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page:
            try:
                # Take screenshot
                screenshot = page.screenshot(full_page=True)
                allure.attach(
                    screenshot,
                    name=f"Screenshot - {item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                print(f"⚠️ Screenshot capture failed: {e}")


@pytest.fixture(scope="function")
def auth_page(browser, create_auth_state, base_url):
    """Opens a page using pre-saved authentication storage"""
    context = browser.new_context(storage_state=create_auth_state)
    page = context.new_page()
    page.goto(f"{base_url}/pages/configurators",
              wait_until="domcontentloaded")

    try:
        page.wait_for_selector(DASHBOARD_HEADER, timeout=60000)
    except:
        print("⚠️  Not logged in from storage_state, try recreating auth.json")

    yield BasePage(page=page,base_url=base_url)
    context.close()



@pytest.fixture(scope="session")
def base_url(pytestconfig) -> str:
    return "https://dmfluxury.com"


@pytest.fixture(scope="function")
def browser_context_args(pytestconfig) -> dict:
    """
    This fixture is consumed by pytest-playwright to set context options.
    See: pytest-playwright uses this fixture name to pass arguments to new contexts.
    We set viewport and optional video recording directory here.
    """
    args = {
        "viewport": {"width": 1280, "height": 720},
    }
    if pytestconfig.getoption("--record-video"):
        # Playwright expects a directory path; plugin will place one video file per page.
        args["record_video_dir"] = str(VIDEOS_DIR)
        # You may also control size/quality with "record_video_size" if desired:
        # args["record_video_size"] = {"width": 1280, "height": 720}
    return args


@pytest.fixture(autouse=True)
def _maybe_trace(pytestconfig, request, page):
    """
    If --trace is set, start tracing on the page's context before the test and save after.
    This fixture is autouse so it runs for every test (when option set).
    """
    if not pytestconfig.getoption("--trace"):
        yield
        return

    trace_name = f"{request.node.name}-{int(time.time())}.zip"
    trace_path = TRACES_DIR / trace_name
    try:
        # Start tracing (screenshots, snapshots, sources)
        page.context.tracing.start(
            screenshots=True, snapshots=True, sources=True)
    except Exception:
        # If tracing isn't available for some reason, continue silently
        pass

    yield

    try:
        # Stop tracing and save to zip
        page.context.tracing.stop(path=str(trace_path))
        # Attach to Allure if test failed or always (choose behavior below)
        report = getattr(request.node, "rep_call", None)
        if report is not None and report.failed:
            allure.attach.file(str(trace_path), name="playwright-trace",
                               attachment_type=allure.attachment_type.ZIP)
    except Exception:
        pass


@pytest.fixture(autouse=True)
def _attach_on_failure(request, page, pytestconfig):
    """
    Autouse fixture that runs for every test: after the test it checks if the test failed.
    If failed, attach screenshot, page source, and video (if recorded) to Allure.
    Depends on the `page` fixture provided by pytest-playwright.
    """
    yield  # run the test

    report = getattr(request.node, "rep_call", None)
    if report is None or not report.failed:
        return

    timestamp = int(time.time())

    # Attempt screenshot (bytes) and attach
    try:
        png_bytes = page.screenshot(full_page=True)
        allure.attach(png_bytes, name="screenshot",
                      attachment_type=allure.attachment_type.PNG)
    except Exception:
        # Try to save to file if bytes method fails
        try:
            screenshot_path = SCREENSHOTS_DIR / \
                f"{request.node.name}-{timestamp}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(str(screenshot_path), name="screenshot-file",
                               attachment_type=allure.attachment_type.PNG)
        except Exception:
            pass

    # Attach page HTML
    try:
        html = page.content()
        allure.attach(html, name="page-source",
                      attachment_type=allure.attachment_type.HTML)
    except Exception:
        pass

    # Attach video if available (ensure page is closed so Playwright finalizes video)
    try:
        # Close the page to flush the video file (if not already closed)
        try:
            page.close()
        except Exception:
            pass

        # page.video() may be None or nonexistent — check carefully
        video_obj = getattr(page, "video", None)
        if video_obj:
            try:
                video_path = video_obj.path()
                if video_path and Path(video_path).exists():
                    allure.attach.file(
                        video_path, name="test-video", attachment_type=allure.attachment_type.MP4)
            except Exception:
                # Some versions require getting video from context/pages - best-effort only
                pass
    except Exception:
        pass


@pytest.fixture(scope="session")
def create_auth_state(pytestconfig, playwright):
    """
    Create and persist a Playwright storage_state for Shopify login.
    Bypasses automation detection by using a persistent user data dir and visible browser.
    """
    base_url = pytestconfig.getoption("--base-url") or "https://dmfluxury.com"
    recreate = pytestconfig.getoption("--recreate-auth")
    auth_path = AUTH_STATE_FILE

    if auth_path.exists() and not recreate:
        print("Using existing auth storage state.")
        return str(auth_path)
    print("Creating new auth storage state...")
    browser_opt = pytestconfig.getoption("--browser")
    if isinstance(browser_opt, (list, tuple)):
        browser_name = browser_opt[0] if browser_opt else "chromium"
    else:
        browser_name = browser_opt or "chromium"


    browser = getattr(playwright, browser_name).launch(
        headless=False,
        args=["--start-maximized"]
    )
    context = browser.new_context(
        no_viewport=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)

    page.goto("https://dmfluxury.com", wait_until="domcontentloaded")
    time.sleep(150)
    # page.wait_for_selector(LOGIN_TEXT, timeout=30000).click()
    # page.wait_for_selector(EMAIL_INPUT, timeout=30000)
    # page.fill(EMAIL_INPUT, EMAIL)
    # page.click(CONTINUE_BUTTON)

    # page.wait_for_load_state("networkidle", timeout=60000)

    # try:
    #     page.wait_for_selector(OTP_INPUT, timeout=30000)
    # except:
    #     print("Retrying after reload...")
    #     page.reload()
    #     page.wait_for_selector(OTP_INPUT, timeout=30000)

    #     # Read OTP from email
    #     otp_code = get_latest_email(query="subject:code")
    #     if not otp_code:
    #         raise RuntimeError("❌ Failed to fetch OTP from email.")
    #     print(f"\n✅ OTP Extracted: {otp_code}")

    #     page.fill(OTP_INPUT, otp_code)
    #     page.click(SUBMIT_BUTTON)

    #     # Verify successful login
    #     try:
    #         page.wait_for_selector(DASHBOARD_HEADER, timeout=60000)
    #         print("✅ Shopify login successful.")
    #     except Exception:
    #         debug_html = page.content()
    #         (RESULTS_DIR / "auth-debug.html").write_text(debug_html, encoding="utf-8")
    #         context.close()
    #         raise RuntimeError("❌ Login failed — see results/auth-debug.html")

    # Save auth storage state
    context.storage_state(path=str(auth_path))
    context.close()

    if not auth_path.exists():
        raise RuntimeError("Failed to create auth storage state.")

    return str(auth_path)
