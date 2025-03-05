from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ZohoCRM:
    def __init__(self, driver):
        self.driver = driver
        self.search_box = (By.XPATH, "//input[@placeholder='Search']")
        self.company_link = (By.XPATH, "//a[contains(@href, '/tab/Accounts/custom-view')]")
        self.parent_company_field = (By.XPATH, "//span[contains(text(), 'Parent Account')]/following-sibling::span")

    def search_company(self, company_name):
        """Search for the company in Zoho CRM"""
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.search_box)
        ).send_keys(company_name)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.company_link)
        ).click()

    def get_parent_company(self):
        """Extract Parent Company Name if available"""
        try:
            parent_company = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.parent_company_field)
            ).text.strip()
            return parent_company
        except:
            return None  # No Parent Company Found
