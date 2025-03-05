# pages/job_list_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JobListPage:
    def __init__(self, driver):
        self.driver = driver
        # Each job is an <a> with class "job-column-link"
        self.job_list = (By.XPATH, "//a[contains(@class, 'job-column-link')]")
        # Next page button has aria-label="Go to next page"
        self.pagination_next = (By.XPATH, "//button[@aria-label='Go to next page']")

    def get_all_jobs(self):
        """Returns a list of job elements (job links)."""
        try:
            print("🔎 Waiting for job elements to load...")
            jobs = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located(self.job_list)
            )
            print(f"✅ Found {len(jobs)} job elements!")
            return jobs
        except Exception as e:
            print(f"⚠️ Timeout: No jobs found. Error: {e}")
            return []

    def click_company_name(self, job_element):
        """Clicks on a job link and returns the text (company name)."""
        company_name = job_element.get_attribute("textContent").strip()
        job_element.click()
        return company_name


    def go_to_next_page(self):
        """Clicks the 'Next Page' button if available."""
        try:
            next_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.pagination_next)
            )
            next_button.click()
            print("🔄 Going to next page...")
            return True
        except:
            print("✅ No more pages found.")
            return False
