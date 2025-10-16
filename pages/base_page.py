"""
A rich BasePage for Playwright tests providing a wide set of helpers
for common UI automation tasks.

Purpose:
- Provide robust, reusable actions (clicks, fills, waits, asserts)
- Helpers for working with storage, cookies, downloads, uploads
- Utilities for debugging: screenshots, highlighting, console capture
- Abstractions for waiting on network requests/responses and navigation

This file is intentionally comprehensive so tests/pages can call small, well-named
methods instead of repeating boilerplate.

Notes:
- Designed for Playwright sync API (playwright.sync_api.Page etc.)
- Keep `page` lifecycle management in fixtures (don't close the page here)
- Avoid making any network calls here; this is purely a helper wrapper
"""
from __future__ import annotations

import json
import time
import typing as t
from pathlib import Path

import allure
from playwright.sync_api import Page, Locator, expect, APIRequestContext, Request, Response

# Artifacts dirs
RESULTS_DIR = Path("results")
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = RESULTS_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


class BasePage:
    """
    Feature-rich BasePage wrapper around a Playwright Page instance.
    """

    def __init__(self, page: Page, base_url: t.Optional[str] = None, default_timeout: int = 60000):
        self.page = page
        self.base_url = base_url.rstrip("/") if base_url else None
        self.default_timeout = default_timeout

        # Internal buffers for console messages and network events
        self._console_messages: list[str] = []
        self._requests: list[Request] = []
        self._responses: list[Response] = []

    # ----------------------------
    # Navigation / URL helpers
    # ----------------------------
    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not self.base_url:
            raise ValueError(
                "base_url not set; provide full URL or set base_url on BasePage")
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def goto(self, path: str, **kwargs) -> None:
        """Navigate to a URL or relative path. Accepts same kwargs as page.goto (timeout, wait_until, etc.)."""
        url = self._build_url(path) if not path.startswith("http") else path
        self.page.goto(url, timeout=kwargs.pop(
            "timeout", self.default_timeout), **kwargs)

    def wait_for_url(self, url_or_pattern: str | t.Callable[[str], bool], timeout: int | None = None) -> None:
        """Wait for page URL to match a string or predicate function."""
        timeout = timeout or self.default_timeout

        def predicate():
            cur = self.page.url
            if callable(url_or_pattern):
                return bool(url_or_pattern(cur))
            return url_or_pattern in cur

        end = time.time() + timeout / 1000.0
        while time.time() < end:
            if predicate():
                return
            time.sleep(0.05)
        raise TimeoutError(
            f"Timed out waiting for URL match: {url_or_pattern}, current: {self.page.url}")

    # ----------------------------
    # Locator helpers
    # ----------------------------
    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def find_by_text(self, text: str, exact: bool = False) -> Locator:
        """Use Playwright text selector with optional exact match."""
        sel = f"text=\"{text}\"" if exact else f"text={text}"
        return self.page.locator(sel)

    # ----------------------------
    # Action helpers
    # ----------------------------
    def Hitclick(self, selector: str, timeout: int | None = None, force: bool = False) -> None:
        """Safe click with wait-for-attached + visible before clicking."""
        timeout = timeout or self.default_timeout
        loc = self.locator(selector)
        loc.wait_for(state="visible", timeout=timeout)
        loc.click(timeout=timeout, force=force)

    def safe_click(self, selector: str, retries: int = 3, retry_delay: float = 0.25,timeout=None) -> None:
        """Retrying click to handle flakiness (stale/obscured elements)."""
        last_exc = None
        for _ in range(retries):
            try:
                self.Hitclick(selector)
                return
            except Exception as e:
                last_exc = e
                time.sleep(retry_delay)
        raise last_exc

    def double_click(self, selector: str, timeout: int | None = None) -> None:
        timeout = timeout or self.default_timeout
        self.locator(selector).dblclick(timeout=timeout)

    def right_click(self, selector: str) -> None:
        self.locator(selector).click(button="right")

    def hover(self, selector: str, timeout: int | None = None) -> None:
        timeout = timeout or self.default_timeout
        self.locator(selector).hover(timeout=timeout)

    def drag_and_drop(self, source: str, target: str, timeout: int | None = None) -> None:
        timeout = timeout or self.default_timeout
        self.page.drag_and_drop(source, target, timeout=timeout)

    def scroll_to(self, selector: str) -> None:
        """Scroll the element into view using JS."""
        self.page.eval_on_selector(
            selector, "el => el.scrollIntoView({behavior: 'auto', block: 'center'})")

    def highlight(self, selector: str, duration: float = 0.5) -> None:
        """Temporarily add a red border around the element for debugging."""
        js = (
            "el=>{ const orig=el.style.boxShadow; el.style.boxShadow='0 0 0 3px rgba(255,0,0,0.7)';"
            f"setTimeout(()=>el.style.boxShadow=orig,{int(duration*1000)});"
        )
        try:
            self.page.eval_on_selector(selector, js)
        except Exception:
            pass

    def type_text(self, selector: str, text: str):
        """Wait for input and type text"""
        self.page.wait_for_selector(selector, timeout=20000)
        self.page.fill(selector, text)

    # ----------------------------
    # Input helpers
    # ----------------------------
    def fill(self, selector: str, value: str, clear: bool = True, timeout: int | None = None) -> None:
        timeout = timeout or self.default_timeout
        if clear:
            loc = self.locator(selector)
            loc.wait_for(state="visible", timeout=timeout)
            loc.fill(value, timeout=timeout)
        else:
            self.page.fill(selector, value, timeout=timeout)

    def type_slow(self, selector: str, value: str, delay: float = 0.05) -> None:
        loc = self.locator(selector)
        loc.click()
        for ch in value:
            self.page.keyboard.insert_text(ch)
            time.sleep(delay)

    def press(self, key: str) -> None:
        self.page.keyboard.press(key)

    def check(self, selector: str) -> None:
        self.locator(selector).check()

    def uncheck(self, selector: str) -> None:
        self.locator(selector).uncheck()

    def set_checkbox(self, selector: str, value: bool) -> None:
        if value:
            self.check(selector)
        else:
            self.uncheck(selector)

    def select_option(self, selector: str, value: t.Union[str, int, t.List[str], None]) -> None:
        self.locator(selector).select_option(value)

    # ----------------------------
    # Waits & assertions
    # ----------------------------
    def wait_for(self, selector: str, state: str = "visible", timeout: int | None = None) -> None:
        timeout = timeout or self.default_timeout
        self.locator(selector).wait_for(state=state, timeout=timeout)

    def wait_for_text(self, selector: str, text: str, timeout: int | None = None, exact: bool = False) -> None:
        timeout = timeout or self.default_timeout
        end = time.time() + timeout / 1000.0
        while time.time() < end:
            try:
                txt = self.get_text(selector)
                if exact and txt == text:
                    return
                if not exact and text in txt:
                    return
            except Exception:
                pass
            time.sleep(0.05)
        raise TimeoutError(
            f"Timed out waiting for text '{text}' in {selector}")

    def get_text(self, selector: str) -> str:
        return self.locator(selector).inner_text()

    def get_attribute(self, selector: str, name: str) -> t.Optional[str]:
        return self.locator(selector).get_attribute(name)

    def is_visible(self, selector: str, timeout: int | None = None) -> bool:
        try:
            self.locator(selector).wait_for(state="visible",
                                            timeout=timeout or self.default_timeout)
            return True
        except Exception:
            return False

    def is_enabled(self, selector: str) -> bool:
        try:
            return self.locator(selector).is_enabled()
        except Exception:
            return False

    def expect_visible(self, selector: str, timeout: int | None = None) -> None:
        expect(self.locator(selector)).to_be_visible(
            timeout=timeout or self.default_timeout)

    def expect_text(self, selector: str, text: str, timeout: int | None = None, exact: bool = True) -> None:
        if exact:
            expect(self.locator(selector)).to_have_text(
                text, timeout=timeout or self.default_timeout)
        else:
            expect(self.locator(selector)).to_contain_text(
                text, timeout=timeout or self.default_timeout)

    # ----------------------------
    # Cookies / storage
    # ----------------------------
    def get_cookies(self) -> list[dict]:
        return self.page.context.cookies()

    def set_cookie(self, cookie: dict) -> None:
        self.page.context.add_cookies([cookie])

    def clear_cookies(self) -> None:
        self.page.context.clear_cookies()

    def storage_state(self, path: str | Path) -> None:
        self.page.context.storage_state(path=str(path))

    def get_local_storage(self) -> dict:
        return self.page.evaluate("() => Object.assign({}, window.localStorage)")

    def set_local_storage(self, data: dict) -> None:
        # Overwrites entries provided
        for k, v in data.items():
            self.page.evaluate("(key, val) => localStorage.setItem(key, val)", k, json.dumps(
                v) if not isinstance(v, str) else v)

    # ----------------------------
    # Downloads / uploads
    # ----------------------------
    def download_and_save(self, click_selector: str, save_as: str | None = None, timeout: int | None = None) -> Path:
        timeout = timeout or self.default_timeout
        save_as = save_as or f"download-{int(time.time())}"
        downloads: list[Path] = []

        with self.page.expect_download(timeout=timeout) as download_info:
            self.safe_click(click_selector)
        download = download_info.value
        target_path = DOWNLOADS_DIR / save_as
        download.save_as(str(target_path))
        return target_path

    def set_input_files(self, selector: str, files: t.Union[str, Path, t.List[str | Path]]) -> None:
        self.locator(selector).set_input_files(files)

    # ----------------------------
    # Network / requests
    # ----------------------------
    def wait_for_response(self, url: t.Union[str, t.Callable[[str], bool]], timeout: int | None = None) -> Response:
        timeout = timeout or self.default_timeout
        return self.page.wait_for_response(lambda r: url in r.url if isinstance(url, str) else url(r.url), timeout=timeout)

    def wait_for_request(self, url: t.Union[str, t.Callable[[str], bool]], timeout: int | None = None) -> Request:
        timeout = timeout or self.default_timeout
        return self.page.wait_for_request(lambda r: url in r.url if isinstance(url, str) else url(r.url), timeout=timeout)

    # ----------------------------
    # Console & debug
    # ----------------------------
    def start_collecting_console(self) -> None:
        self._console_messages = []

        def _on_console(msg):
            try:
                txt = f"[{msg.type}] {msg.text}"
            except Exception:
                txt = str(msg)
            self._console_messages.append(txt)

        self.page.on("console", _on_console)

    def stop_collecting_console(self) -> list[str]:
        # Note: Playwright doesn't provide a remove listener API in all bindings; we keep messages
        return self._console_messages

    def attach_console_to_allure(self, name: str = "console.log") -> None:
        if self._console_messages:
            allure.attach("\n".join(self._console_messages), name=name,
                          attachment_type=allure.attachment_type.TEXT)

    # ----------------------------
    # Artifacts
    # ----------------------------
    def take_screenshot(self, name: t.Optional[str] = None, full_page: bool = True, attach: bool = True) -> Path:
        timestamp = int(time.time() * 1000)
        name = name or f"{self.__class__.__name__}-{timestamp}.png"
        path = SCREENSHOTS_DIR / name
        self.page.screenshot(path=str(path), full_page=full_page)
        if attach:
            try:
                allure.attach.file(str(path), name=name,
                                   attachment_type=allure.attachment_type.PNG)
            except Exception:
                try:
                    allure.attach(path.read_bytes(), name=name,
                                  attachment_type=allure.attachment_type.PNG)
                except Exception:
                    pass
        return path

    def take_pdf(self, path: str | None = None) -> Path:
        out = RESULTS_DIR / (path or f"page-{int(time.time())}.pdf")
        self.page.pdf(path=str(out))
        return out

    # ----------------------------
    # Utilities
    # ----------------------------
    def execute_script(self, script: str, *args):
        return self.page.evaluate(script, *args)

    def get_elements_count(self, selector: str) -> int:
        return self.locator(selector).count()

    def get_elements_texts(self, selector: str) -> list[str]:
        count = self.get_elements_count(selector)
        texts = []
        for i in range(count):
            texts.append(self.locator(selector).nth(i).inner_text())
        return texts

    def get_css_value(self, selector: str, prop: str) -> str:
        return self.page.eval_on_selector(selector, f"el => getComputedStyle(el).getPropertyValue('{prop}')")

    # ----------------------------
    # Retry helpers
    # ----------------------------
    def retry(self, func: t.Callable, retries: int = 3, delay: float = 0.2, *args, **kwargs):
        last_exc = None
        for _ in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                time.sleep(delay)
        raise last_exc

    # ----------------------------
    # Higher-level flows
    # ----------------------------
    def login_via_ui(self, username: str, password: str, login_url: str | None = None) -> None:
        """Generic login flow - expects typical username/password inputs and submit button.
        This should be overridden or used by page objects with correct selectors.
        """
        url = login_url or (
            f"{self.base_url}/web/index.php/auth/login" if self.base_url else None)
        if not url:
            raise ValueError("login_url or base_url must be provided")
        self.goto(url)
        # best-effort selectors - override in concrete pages
        self.fill("input[name='username']", username)
        self.fill("input[name='password']", password)
        self.safe_click("button[type='submit']")

    # ----------------------------
    # Cleanup/Helpers
    # ----------------------------
    def save_storage_state(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.page.context.storage_state(path=str(path))

    def load_storage_state_into_new_context(self, playwright, browser_name: str = "chromium", storage_path: str | Path = None, headless: bool = True):
        """Launch a new browser and context from storage state. Returns (browser, context, page)."""
        storage_path = storage_path or "auth.json"
        browser = getattr(playwright, browser_name).launch(headless=headless)
        context = browser.new_context(storage_state=str(storage_path))
        page = context.new_page()
        return browser, context, page


# End of file
