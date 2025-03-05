import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class NotesDocumentsPage:
    def __init__(self, driver):
        self.driver = driver
        # Use an XPath to select all note rows on the tab.
        self.note_rows = (By.XPATH, "//tr[contains(@class, 'message-attachment-list-item')]")
    
    def get_service_notes(self):
        """
        Loops through each note row and extracts:
          - The service date (assumed to be in the 2nd <td>)
          - The note description (assumed to be in the 4th <td>)
          - The image URL if present (attempted from the 3rd <td>)
        Returns a concatenated string of these details.
        """
        note_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(self.note_rows)
        )
        all_notes = []
        for row in note_elements:
            try:
                # Extract the service date (2nd <td>)
                service_date = row.find_element(By.XPATH, "./td[2]").text.strip()
            except:
                service_date = "UnknownDate"
            try:
                # Extract the note description (4th <td>)
                note_description = row.find_element(By.XPATH, "./td[4]").text.strip()
            except:
                note_description = "No description"
            try:
                # Try to locate an image inside the 3rd <td>
                img_elem = row.find_element(By.XPATH, "./td[3]//img")
                img_url = img_elem.get_attribute("src")
            except:
                img_url = ""
            note_entry = f"Date: {service_date}\nNote: {note_description}\nImage URL: {img_url}"
            all_notes.append(note_entry)
        return "\n\n".join(all_notes)

    def download_images(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        
        # Scroll to the bottom to trigger lazy-loading
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Force AngularJS to flush its timeout/digest cycle (optional; can be commented out if causing issues)
        try:
            self.driver.execute_script("""
                if (window.angular) {
                    var injector = angular.element(document.body).injector();
                    var $timeout = injector.get('$timeout');
                    $timeout.flush();
                }
            """)
        except Exception as e:
            print("Angular flush error:", e)
        
        # Wait explicitly until images are visible, handling the case where no images load.
        try:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.attachment-thumb img"))
            )
        except TimeoutException:
            print("No images found after waiting; skipping image download.")
            return
        
        # Now get all image elements
        images = self.driver.find_elements(By.CSS_SELECTOR, "td.attachment-thumb img")
        print(f"Found {len(images)} image elements.")
        
        downloaded = 0
        for i, img in enumerate(images):
            img_url = img.get_attribute("src")
            if not img_url:
                print(f"⚠️ No URL for image {i+1}")
                continue
            try:
                response = requests.get(img_url)
                file_path = os.path.join(folder_path, f"image_{i+1}.jpg")
                with open(file_path, "wb") as f:
                    f.write(response.content)
                downloaded += 1
            except Exception as e:
                print(f"⚠️ Error downloading image {i+1}: {e}")
        print(f"Downloaded {downloaded} images to {folder_path}")

