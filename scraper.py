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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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
        # if client_name:
        #     if "-" in client_name:
        #         client_name = client_name.split("-")[-1]
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

    parent_path = [job_id_lval, safe_client]
    
    folder_path = os.path.join("output", *parent_path)
    os.makedirs(folder_path, exist_ok=True)

    
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.attachment-thumb img"))
        )
    except TimeoutException:
        print("No images found in this job's Notes & Documents tab; skipping image download.")
        
        
    parent_xpath = "//table[@id='noteTable']//tr[@class='message-attachment-list-item ng-scope']"

    # Add explicit waits and scrolling
    # notes_documents_page = NotesDocumentsPage(driver)
    
    # Scroll multiple times to ensure all images are loaded
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give time for images to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Wait for all image elements to be present
    try:
        parent_elements = WebDriverWait(driver, 30).until(  # Increased timeout to 30 seconds
            EC.presence_of_all_elements_located((By.XPATH, parent_xpath))
        )
        
        # Keep track of downloaded images to avoid duplicates
        downloaded_images = []
        
        for parent_element in parent_elements:
            try:
                date_element = parent_element.find_element(By.XPATH, ".//td[@class='ng-binding' and contains(text(), ':')]")
                date_text = date_element.text
                if date_text:
                    date_text = date_text.split(" ")[:3]
                    date_text = "_".join(date_text)
                print(f"Date: {date_text}")     
                safe_date_text = sanitize_path_component(date_text)

                text = None
                
                try:
                    image_element = parent_element.find_element(By.XPATH, ".//td[@class='attachment-thumb']/img")
                    image_url = image_element.get_attribute("data-geo-image-modal-url")
                except:
                    image_url = None
                
                # If no image URL found, try looking for an anchor tag with data-ng-href
                if not image_url:
                    try:
                        anchor_element = parent_element.find_element(By.XPATH, ".//td[@class='attachment-thumb']//a")
                        image_url = anchor_element.get_attribute("data-ng-href")
                    except:
                        image_url = None

                # If no image or pdf consider it as a text file
                if not image_url:
                    try:
                        anchor_element = parent_element.find_element(By.XPATH, ".//td[@class='note-description ng-binding']")
                        text = anchor_element.text
                    except:
                        text = None

                
                # Skip if no valid URL found or if we've already downloaded this image
                if not image_url and not text or image_url in downloaded_images:
                    continue
                    
                print(f"Image/PDF URL: {image_url}")  
                
                if image_url:
                    print("Image URL found")
                    folder_path_for_images = os.path.join("output", *parent_path, date_text)
                    os.makedirs(folder_path_for_images, exist_ok=True)          

                    # Get file description if available
                    try:
                        # Get the div with class 'file-description' but exclude the span with file size
                        file_desc = parent_element.find_element(By.XPATH, ".//div[contains(@class, 'file-description')]").text
                        # Remove the file size span content using regex
                        file_desc = re.sub(r'\s*\(\d+\.?\d*\s*[KMG]B\)', '', file_desc).strip()
                        print(f"File description: {file_desc}")

                        # Clean up the URL to get just the file extension
                        if '?' in image_url:
                            base_url = image_url.split('?')[0]
                            base_url = base_url.split('&')[0]
                        else:
                            base_url = image_url
                            
                        # Use the cleaned file description as the filename
                        image_filename = f"{len(downloaded_images)}{file_desc}"
                        print(f"Image filename: {image_filename}")

                        image_path = os.path.join(folder_path_for_images, image_filename)
                    except:
                        print("No file description found; using default filename")
                        image_filename = f"file_{int(time.time())}_{len(downloaded_images)}.jpg"   
                        image_path = os.path.join(folder_path_for_images, image_filename)

                    print(f"Downloading image to: {image_path}")

                    # # Generate unique filename using timestamp and a counter
                    # image_filename = f"image_{int(time.time())}_{len(downloaded_images)}.jpg"
                    # image_path = os.path.join(folder_path_for_images, image_filename)
                    
                    # Download with retry mechanism
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            response = requests.get(image_url, timeout=30)
                            response.raise_for_status()
                            with open(image_path, "wb") as f:
                                f.write(response.content)
                            downloaded_images.append(image_url)
                            break
                        except (requests.RequestException, IOError) as e:
                            if attempt == max_retries - 1:
                                print(f"Failed to download image after {max_retries} attempts: {e}")
                                continue
                            time.sleep(2)  # Wait before retrying
                elif text:
                    print("Text found")
                    folder_path_for_text = os.path.join("output", *parent_path, date_text)
                    os.makedirs(folder_path_for_text, exist_ok=True)
                    text_path = os.path.join(folder_path_for_text, f"{safe_date_text}{len(downloaded_images)}.txt")
                    with open(text_path, "w") as f:
                        f.write(text)
                    downloaded_images.append(text)
            except Exception as e:
                print(f"Error processing single image in job: {e}")
                
        print(f"Successfully downloaded {len(downloaded_images)} files out of {len(parent_elements)} rows")

        return {
            "downloaded": len(downloaded_images),
            "total": len(parent_elements),
            "client_name": client_name,
            "service_name": service_name,
            "job_id": job_id_lval,
            "date": safe_date,
            "folder_path": folder_path,
        }
    except Exception as e:
        print(f"Error processing job: {e}")
        with open('failed_urls.csv', 'a') as f:
            f.write(f"{job_url}\n")


def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

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
            result = process_job_page(driver, url)
            print(result)

            if (result["downloaded"] == result["total"]):
                print("✅ All files downloaded successfully!")
            else:
                print("❌ Some files failed to download!")
                raise Exception("Some files failed to download!")

            
            time.sleep(3)
        except Exception as e:
            print(f"Error processing job: {e}")
            with open('failed_urls.csv', 'a') as f:
                f.write(f"{url}\n")

    print("✅ Finished scraping jobs!")

    # Remove or comment out the driver.quit() line
    driver.quit()  

    # # Add this to keep the script running
    # try:
    #     input("Press Enter to close the browser...")
    # finally:
    #     driver.quit()



if __name__ == "__main__":
    main()
