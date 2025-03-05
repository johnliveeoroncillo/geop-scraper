from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_field = (By.ID, "loginname")  # Corrected selector
        self.password_field = (By.ID, "geoop-password")  # Corrected selector
        self.login_button = (By.ID, "loginID")  # Corrected selector

    def enter_username(self, username):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.username_field)
        ).send_keys(username)

    def enter_password(self, password):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.password_field)
        ).send_keys(password)

    def click_login(self):
        """Click login button after ensuring it's visible and clickable"""
        try:
            login_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "loginID"))
            )
            login_btn.click()  # Normal click
        except:
            print("⚠️ Normal click failed, trying JavaScript click")
            login_btn = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "loginID"))
            )
            self.driver.execute_script("arguments[0].click();", login_btn)  # JavaScript click


