from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JobPage:
    def __init__(self, driver):
        self.driver = driver
        # Use the unique ID for client name from your HTML snippet
        self.client_name = (By.XPATH, "//a[@id='job_client_link']")
        # For the service name, refine your XPath if needed (using a unique class if available)
        self.job_title = (By.XPATH, "//div[contains(@class, 'job-edit-details-limit') and contains(., 'Job Title:')]")
        # If the service date is shown in the first tab, leave it here;
        # otherwise, if it’s only visible in the Notes tab, you might extract it there.
        self.service_date = (By.XPATH, "//span[contains(@class, 'schedule-date')]")
        # Selector for the "Notes & Documents" tab; update if needed
        self.notes_documents_tab = (By.XPATH, "//li[@id='noteslink']/a")

    def get_client_name(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.client_name)
        ).text.strip()

    def get_service_name(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.job_title)
        )
        full_text = element.text.strip()  # e.g. "Job Title: Swap filters"
        # Remove the "Job Title:" prefix to get just the service name
        service_name = full_text.replace("Job Title:", "").strip()
        return service_name

    def get_service_date(self):
        # If the service date is only visible in the Notes tab, ensure that tab is clicked before calling this
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.service_date)
        ).text.strip()

    def go_to_notes_documents(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.notes_documents_tab)
        ).click()
