# ----- Selectors (centralized) -----
LOGIN_TEXT = "text=Dealer Login"
TITLE_TEXT = '//title[text()="Sign in - DMF Luxury"]'
EMAIL_INPUT = "input[name='email']"
CONTINUE_BUTTON = "button[name='commit']"
OTP_TEXT = '//h2[contains(text(),"Enter code")]'
OTP_INPUT = 'input[placeholder="6-digit code"]'
SUBMIT_BUTTON = '//span[contains(text(),"Submit")]/parent::button'
ALERT_ERROR = "p[class='textfield-error']"

DASHBOARD_HEADER = '//h2[text()="Welcome back Salman!"]'
USER_MENU = "p.oxd-userdropdown-name"
LOGOUT_LINK = "a:has-text('Logout')"
# used for logout visibility
PROFILE_MENU = "img[alt='profile picture'], .oxd-userdropdown-img"
ERROR_ALERT = "div.oxd-alert-content"