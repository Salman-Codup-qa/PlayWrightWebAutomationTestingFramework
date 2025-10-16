from app_selectors.login_selectors import (
    DASHBOARD_HEADER,
)
from app_selectors.dashboard_selectors import (
    INSPIRATIONS,
    PRODUCTS,
    REP_MAPS,
    RESOURCES,
    SHOP,
    SOLUTIONS,
    SALES_TOOLS,
    WHY_DMF,
    ACCOUNT_MENU,
    PROFILE_MENU,
    ACCOUNT_NAME,
)
from playwright.sync_api import Page
import time
from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import sync_playwright
import allure
import pytest
from pages.base_page import BasePage
import os



@allure.epic("Dashboard Tests")
@allure.feature("Dashboard Access")
@allure.story("Access Dashboard after Login")
class TestDashboard:
    
    @allure.title("Verify Dashboard access after login")
    @allure.description("Ensures the dashboard is accessible after performing login with email.")
    @pytest.mark.smoke
    @pytest.mark.dashboard
    @pytest.mark.regression
    def test_dashboard_access_after_login(self, auth_page: BasePage):
        """
        Uses the 'page' fixture to perform login and verify dashboard access.
        """
        auth_page = auth_page
        auth_page.goto("https://dmfluxury.com/pages/configurators")
        auth_page.take_screenshot("landing_page.jpg",full_page=True,attach=True)

        with allure.step("Verify Dashboard element is visible"):
            element = auth_page.locator(DASHBOARD_HEADER)
            assert element.is_visible(), "Dashboard element should be visible after login"
            
        auth_page.take_screenshot("google.jpg",full_page=True,attach=True)




    @allure.title("Verify Navigation Bar Links")
    @allure.description("Ensures all navigation bar links are present and clickable.")
    @pytest.mark.smoke
    @pytest.mark.dashboard
    @pytest.mark.regression
    def test_navbar_links(self, auth_page: BasePage):
        """
        Uses the 'page' fixture to perform login and verify navigation bar links.
        """
        auth_page = auth_page
        auth_page.goto("https://dmfluxury.com")
        auth_page.take_screenshot("landing_page.jpg",full_page=True,attach=True)

        with allure.step("Verify Navigation Bar Links"):
            nav_links = {
                "Products": PRODUCTS,
                "Shop": SHOP,
                "Solutions": SOLUTIONS,
                "Sales Tools": SALES_TOOLS,
                "Why DMF": WHY_DMF,
                "Inspirations": INSPIRATIONS,
                "Rep Maps": REP_MAPS,
                "Resources": RESOURCES,
            }

            for link_name, selector in nav_links.items():
                with allure.step(f"Check {link_name} link"):
                    element = auth_page.locator(selector)
                    assert element.is_visible(), f"{link_name} link should be visible"
                    # Optionally, you can also check if the link is clickable
                    try:
                        element.click()
                        auth_page.page.go_back()  # Navigate back after click
                    except Exception as e:
                        pytest.fail(f"{link_name} link should be clickable. Error: {str(e)}")

        auth_page.take_screenshot("google.jpg",full_page=True,attach=True)

    @allure.title("Verify 2 == 2")
    @allure.description("Simple test to verify that 2 equals 2.")
    @pytest.mark.smoke
    @pytest.mark.dashboard
    @pytest.mark.regression
    def test_numbers(self, auth_page: BasePage):
        #salman me
        assert 2 == 2, "2 should equal 2"
        auth_page.take_screenshot("Numberes.jpg",full_page=True,attach=True)