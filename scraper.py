import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import re


# Page object imports
from pages.geoop_login_page import LoginPage
from pages.job_list_page import JobListPage
from pages.job_page import JobPage
from pages.notes_documents_page import NotesDocumentsPage
from utils.image_wait import wait_for_angular


# Config file with USERNAME, PASSWORD, LOGIN_URL, JOBS_URL
import config_geoop
from config_geoop import JOB_URLS_LIST as urls

COOKIES_FILE = "cookies.json"

def load_cookies_json(driver, filename=COOKIES_FILE):
    """Load cookies from JSON file to skip 2FA."""
    if os.path.exists(filename):
        print("🔄 Attempting to load cookies to skip 2FA...")
        with open(filename, "r") as f:
            cookies = json.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("✅ Cookies loaded successfully!")

def save_cookies_json(driver, filename=COOKIES_FILE):
    """Save cookies to JSON after passing login + 2FA."""
    cookies = driver.get_cookies()
    with open(filename, "w") as f:
        json.dump(cookies, f, indent=2)
    print("✅ Cookies saved to JSON!")

def sanitize_path_component(component):
    """Sanitize a path component by removing or replacing invalid characters."""
    # Remove leading/trailing spaces
    component = component.strip()
    # Replace invalid characters with underscores
    component = re.sub(r'[<>:"/\\|?*]', '_', component)
    # Replace multiple spaces with single underscore
    component = re.sub(r'\s+', '_', component)
    return component

def process_job_page(driver, job_url):
    """Process a single job URL: extract details, download notes and images."""
    driver.get(job_url)
    time.sleep(3)

    # Extract data from the Job tab
    job_page = JobPage(driver)
    try:
        client_name = job_page.get_client_name()
        if client_name:
            if "-" in client_name:
                client_name = client_name.split("-")[-1]
    except Exception:
        client_name = ""
    try:
        service_name = job_page.get_service_name()
    except Exception:
        service_name = ""
        
    try:
        job_id = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//span[@data-ng-show='job.id']"))
        )
        text_job_id = job_id.text
        job_text_li = text_job_id.split(" ")
        for job_id_val in job_text_li:
            if job_id_val.startswith("#"):
                job_id_lval = job_id_val
        
        if job_id_lval:
            job_id_lval = job_id_lval.replace('#', '')
        else:
            job_id_lval = None
    except:
        job_id_lval = None
        

    print(f"Scraping job: client={client_name}, service={service_name}")

    # Sanitize folder names
    safe_client = sanitize_path_component(client_name)
    safe_service = sanitize_path_component(service_name)

    try:
        date_visit = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@data-ng-hide='visits | isEmpty']"))
        )
        date_text = date_visit.text
        
        date_elements = []
        if date_text:
            date_text = date_text.split(" ")
            for date in date_text:
                    if "-" in date or ":" in date:
                        continue
                    else:
                        date_elements.append(date)
        if len(date_elements) == 2:
            safe_date = "_".join(date_elements)
        elif len(date_elements) == 4:
            safe_date = "_".join(date_elements[:2])
        else:
            safe_date = ""
    except TimeoutException:
        safe_date = ""
        print("No images found in this job's Notes & Documents tab; skipping image download.")

    safe_date = sanitize_path_component(safe_date)
    
    # Switch to the "Notes & Documents" tab
    job_page.go_to_notes_documents()
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # try:
    #     driver.execute_script("""
    #         if (window.angular) {
    #             var injector = angular.element(document.body).injector();
    #             var $timeout = injector.get('$timeout');
    #             $timeout.flush();
    #         }
    #     """)
    # except Exception as e:
    #     print("Angular flush error:", e)

    # try:
    #     WebDriverWait(driver, 15).until(
    #         EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.attachment-thumb img"))
    #     )
    # except TimeoutException:
    #     print("No images found in this job's Notes & Documents tab; skipping image download.")
    
    folder_path = os.path.join("output", safe_client, f"#{job_id_lval}_{safe_service}_{safe_date}")
    os.makedirs(folder_path, exist_ok=True)

    
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.attachment-thumb img"))
        )
    except TimeoutException:
        print("No images found in this job's Notes & Documents tab; skipping image download.")
        
        
    parent_xpath = "//tr[@class='message-attachment-list-item ng-scope']"

    try:
        parent_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, parent_xpath))
        )
        

        
        for parent_element in parent_elements:
            try:
                date_element = parent_element.find_element(By.XPATH, ".//td[@class='ng-binding' and contains(text(), ':')]")
                date_text = date_element.text
                if date_text:
                    date_text = date_text.split(" ")[:3]
                    date_text = "_".join(date_text)
                print(f"Date: {date_text}")     
                safe_date_text = sanitize_path_component(date_text)
                    
                image_element = parent_element.find_element(By.XPATH, ".//td[@class='attachment-thumb']/img")
                image_url = image_element.get_attribute("data-geo-image-modal-url")
                print(f"Image URL: {image_url}")  
                
                
                folder_path_for_images = os.path.join("output", safe_client, f"#{job_id_lval}_{safe_service}_{safe_date}", safe_date_text)
                os.makedirs(folder_path_for_images, exist_ok=True)          

                # Generate unique filename for each image
                image_filename = f"image_{int(time.time())}.jpg"
                image_path = os.path.join(folder_path_for_images, image_filename)
                
                with open(image_path, "wb") as f:
                    f.write(requests.get(image_url).content)
            except Exception as e:
                print(f"Error processing single image in job: {e}")
    except Exception as e:
        print(f"Error processing job: {e}")
        with open('failed_urls.csv', 'a') as f:
            f.write(f"{job_url}\n")


def main():
    driver = webdriver.Chrome()

    # ---------------------
    # 1) Login to GeoOp
    # ---------------------
    print("🔎 Navigating to GeoOp login page...")
    driver.get(config_geoop.LOGIN_URL)
    time.sleep(3)

    load_cookies_json(driver)
    driver.refresh()
    time.sleep(3)

    try:
        login_page = LoginPage(driver)
        login_page.enter_username(config_geoop.USERNAME)
        login_page.enter_password(config_geoop.PASSWORD)
        login_page.click_login()
        time.sleep(3)
    except Exception as e:
        print("Login with password failed")


    # 3) Save cookies for future runs
    save_cookies_json(driver)

    # ---------------------
    driver.get(config_geoop.JOBS_URL)
    time.sleep(3)

    for url in urls:
        try:
            process_job_page(driver, url)
            time.sleep(3)
        except Exception as e:
            print(f"Error processing job: {e}")
            with open('failed_urls.csv', 'a') as f:
                f.write(f"{url}\n")

    print("✅ Finished scraping jobs!")
    driver.quit()



if __name__ == "__main__":
    main()
