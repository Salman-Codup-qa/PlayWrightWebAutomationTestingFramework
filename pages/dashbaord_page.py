# pages/login_page.py
import time
from typing import Optional
import allure
from playwright.sync_api import Page
import pytest
from pages.base_page import BasePage
# from playwright_stealth import stealth_sync
from utils.google_utils import get_latest_email
from app_selectors.login_selectors import (
    LOGIN_TEXT,
    EMAIL_INPUT,
    CONTINUE_BUTTON,
    OTP_INPUT,
    SUBMIT_BUTTON,
    PROFILE_MENU,
    ERROR_ALERT,
)


class DashboardPage(BasePage):
    """
    Page Object for the OrangeHRM dashboard page (https://opensource-demo.orangehrmlive.com).
    Keep selectors and flows here so tests stay small and readable.
    """

    def __init__(self, page: Page, base_url: Optional[str] = None, default_timeout: int = 60000):
        super().__init__(page=page, base_url=base_url, default_timeout=default_timeout)

    # ----- Navigation -----
    def goto_dashboard(self) -> None:
        """Open the login page (uses base_url if provided)."""
        # Either full path or relative
        if self.base_url:
            self.goto(self.base_url)
        else:
            # fallback to an absolute path if base_url is not set
            self.goto(
                "https://dmfluxury.com")
       

    # ----- Actions -----


    def NavBarLinks(self, email, wait_for_dashboard=True):
        """Performs login with email and password"""
        with allure.step('And Wait for Email Field to appear'):
            self.page.wait_for_selector(EMAIL_INPUT, timeout=30000)
        with allure.step(f'Enter Email {email}'):
            self.type_text(EMAIL_INPUT, email)

        # Wait for submit to be attached & clickable
        with allure.step('And Wait for Continue to be clickable'):
            self.page.wait_for_selector(CONTINUE_BUTTON, state="attached", timeout=30000)
            self.safe_click(CONTINUE_BUTTON, timeout=30000)

        with allure.step('Wait for OTP Input to appear'):
            self.page.wait_for_selector(OTP_INPUT, timeout=120000)

        otp_code = None
        with allure.step('Get OTP from email'):
            otp_code = get_latest_email(query="subject:code")
            if otp_code:
                print(f"\nFinal Extracted OTP for use: {otp_code}")
            else:
                print("\nOTP extraction failed. Check email content and regex.")
                pytest.fail("Unable to Get the OTP from Email")

        with allure.step(f'Enter OTP And Submit{otp_code}'):
            self.page.wait_for_selector(self.OTP_INPUT, timeout=30000)
            self.type_text(OTP_INPUT, otp_code)
            self.safe_click(SUBMIT_BUTTON, timeout=30000)

































# class LoginPage(BasePage):
#     """
#     Page Object for the OrangeHRM login page (https://opensource-demo.orangehrmlive.com).
#     Keep selectors and flows here so tests stay small and readable.
#     """

#     def __init__(self, page: Page, base_url: Optional[str] = None, default_timeout: int = 60000):
#         super().__init__(page=page, base_url=base_url, default_timeout=default_timeout)

#     # ----- Navigation -----
#     def goto_login(self) -> None:
#         """Open the login page (uses base_url if provided)."""
#         # Either full path or relative
#         if self.base_url:
#             self.goto(self.base_url)
#         else:
#             # fallback to an absolute path if base_url is not set
#             self.goto(
#                 "https://dmfluxury.com")
#         time.sleep(10)
#         self.page.wait_for_selector(LOGIN_TEXT, timeout=30000).click()
#         time.sleep(10)
#         self.page.reload()

#     # ----- Actions -----


#     def login(self, email, wait_for_dashboard=True):
#         """Performs login with email and password"""
#         with allure.step('And Wait for Email Field to appear'):
#             self.page.wait_for_selector(EMAIL_INPUT, timeout=30000)
#         with allure.step(f'Enter Email {email}'):
#             self.type_text(EMAIL_INPUT, email)

#         # Wait for submit to be attached & clickable
#         with allure.step('And Wait for Continue to be clickable'):
#             self.page.wait_for_selector(CONTINUE_BUTTON, state="attached", timeout=30000)
#             self.safe_click(CONTINUE_BUTTON, timeout=30000)
        
#         with allure.step('Wait for OTP Input to appear'):
#             self.page.wait_for_selector(OTP_INPUT, timeout=120000)
        
#         otp_code = None
#         with allure.step('Get OTP from email'):
#             otp_code = get_latest_email(query="subject:code")
#             if otp_code:
#                 print(f"\nFinal Extracted OTP for use: {otp_code}")
#             else:
#                 print("\nOTP extraction failed. Check email content and regex.")
#                 pytest.fail("Unable to Get the OTP from Email")

#         with allure.step(f'Enter OTP And Submit{otp_code}'):
#             self.page.wait_for_selector(self.OTP_INPUT, timeout=30000)
#             self.type_text(OTP_INPUT, otp_code)
#             self.safe_click(SUBMIT_BUTTON, timeout=30000)
            
      
            
    
#         if wait_for_dashboard:
#             with allure.step('Verify Dashboard Appears'):
#                 try:
#                     self.page.wait_for_url("**/dashboard/**", timeout=30000)
#                 except:
#                     pytest.fail("Dashboard did not load after login")


#     def logout(self) -> None:
#         """
#         Try to log out by opening the profile dropdown and selecting Logout.
#         This is best-effort — selectors may require tuning if UI changes.
#         """
#         # open profile/dropdown
#         try:
#             self.safe_click(PROFILE_MENU)
#             # common logout selector text
#             self.safe_click("text=Logout")
#             # wait for login page to appear
#             self.wait_for("input[name='username']", timeout=30000)
#         except Exception:
#             # ignore if logout not available / already logged out
#             pass

#     # ----- Assertions / info -----


#     def is_login_error_visible(self):
#         """Detects if invalid credentials message appears"""
#         try:
#             self.page.wait_for_selector(ERROR_ALERT, timeout=30000)
#             msg = self.page.inner_text(ERROR_ALERT)
#             return "Invalid credentials" in msg or "Invalid" in msg
#         except Exception:
#             return False


#     def get_login_error_text(self) -> Optional[str]:
#         """Return the text of the login error alert, if present; else None."""
#         try:
#             if self.is_login_error_visible(timeout=1_000):
#                 return self.get_text(ERROR_ALERT).strip()
#         except Exception:
#             pass
#         return None


#     def is_logged_in(self):
#         try:
#             # Wait for dashboard breadcrumb to appear
#             self.page.wait_for_selector("header.oxd-topbar", timeout=30000)
#             current_url = self.page.url
#             return "/dashboard" in current_url or "dashboard" in current_url
#         except Exception:
#             return False
