from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ZohoLoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_field = (By.ID, "login_id")  # Adjust selector
        self.password_field = (By.ID, "password")
        self.login_button = (By.ID, "nextbtn")  # Adjust for Zoho's button

    def enter_username(self, username):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.username_field)
        ).send_keys(username)

    def enter_password(self, password):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.password_field)
        ).send_keys(password)

    def click_login(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.login_button)
        ).click()
