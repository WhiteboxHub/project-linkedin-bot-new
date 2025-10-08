"""
LinkedIn Easy Apply functionality
"""
import time
import csv
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils.browser_manager import get_browser
from utils.resume_parser import get_resume_path

def apply_to_jobs(config_path, job_ids):
    """
    Apply to jobs using LinkedIn Easy Apply
    
    Args:
        config_path: Path to the YAML configuration file
        job_ids: Dictionary of job IDs to process
    """
    # Initialize ApplyBot with the configuration
    apply_bot = ApplyBot(config_path)
    
    # Apply to each job
    for job_id in job_ids:
        if job_ids[job_id] == "To be processed":
            try:
                apply_bot.apply_to_job(job_id)
            except Exception as e:
                print(f"Error applying for job {job_id}: {e}")

class ApplyBot:
    """Bot for applying to LinkedIn jobs"""
    
    def __init__(self, config_path):
        """Initialize the ApplyBot with configuration"""
        import yaml
        
        # Load configuration
        with open(config_path, 'r') as stream:
            try:
                parameters = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc
        
        # Set instance variables from parameters
        self.username = parameters['username']
        self.password = parameters['password']
        self.phonenumber = parameters['phone_number']
        self.salary = parameters['salary']
        self.rate = parameters['rate']
        self.uploads = {} if parameters.get('uploads', {}) is None else parameters.get('uploads', {})
        self.resume_path = get_resume_path(self.uploads.get("Resume", ""))
        self.roletype = parameters.get('roletype', [])
        self.filename = f"output/applications/Output_of_{parameters['username']}.csv"
        self.blacklist = parameters.get('blacklist', [])
        self.blacklisttitles = parameters.get('blackListTitles', [])
        self.gender = parameters['gender']
        self.qa_file = Path(f"output/applications/qa_{self.username}.csv")
        self.answer = {}
        self.chrome_profile_name = parameters.get('chrome_profile_name', 'Default')
        self.custom_profile_path = parameters.get('profile_path', '')
        
        # Initialize browser with specific Chrome profile
        self.browser = get_browser(self.chrome_profile_name, self.custom_profile_path if self.custom_profile_path else None)
        self.wait = WebDriverWait(self.browser, 30)
        
        # Define locators for elements
        self.locator = {
            "next": (By.CSS_SELECTOR, "button[aria-label='Continue to next step']"),
            "review": (By.CSS_SELECTOR, "button[aria-label='Review your application']"),
            "submit": (By.CSS_SELECTOR, "button[aria-label='Submit application']"),
            "error": (By.CLASS_NAME, "artdeco-inline-feedback__message"),
            "upload_resume": (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-resume')]"),
            "upload_cv": (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-cover-letter')]"),
            "follow": (By.CSS_SELECTOR, "label[for='follow-company-checkbox']"),
            "upload": (By.NAME, "file"),
            "search": (By.CLASS_NAME, "jobs-search-results-list"),
            "links": (By.XPATH, '//div[@data-job-id]'),
            "fields": (By.CLASS_NAME, "jobs-easy-apply-form-section__grouping"),
            "radio_select": (By.CSS_SELECTOR, "input[type='radio']"),
            "multi_select": (By.XPATH, "//*[contains(@id, 'text-entity-list-form-component')]"),
            "text_select": (By.CLASS_NAME, "artdeco-text-input--input"),
            "2fa_oneClick": (By.ID, 'reset-password-submit-button'),
            "easy_apply_button": (By.XPATH, '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]'),
            "specific_easy_apply": (By.XPATH, '//button[contains(@class, "jobs-apply-button")]')
        }
        
        # Load QA data if available
        if self.qa_file.is_file():
            df = pd.read_csv(self.qa_file)
            for index, row in df.iterrows():
                self.answer[row['Question']] = row["Answer"]
        else:
            df = pd.DataFrame(columns=["Question", "Answer"])
            df.to_csv(self.qa_file, index=False, encoding='utf-8')
        
        print(f"--------------------------The Candidate Selected is {self.username}------------------------------")
        print(f'Phone: {self.phonenumber}')
        print(f'Salary: {self.salary}')
        print(f'Uploads: {self.uploads}')
        print(f'Locations: {parameters.get("locations", [])}')
        print(f'Positions: {parameters.get("positions", [])}')
        
    def apply_to_job(self, job_id):
        """Apply to a job with the given ID"""
        self.get_job_page(job_id)
        time.sleep(4)
        self.close_overlays()
        
        button = self.get_easy_apply_button()
        if button is None:
            if "You applied on" in self.browser.page_source:
                print("You have already applied to this position.")
                string_easy = "* Already Applied"
                result = False
            else:
                print("The Easy Apply button does not exist or is not clickable.")
                string_easy = "* Doesn't have Easy Apply Button"
                result = False
        else:
            if any(word in self.browser.title for word in self.blacklisttitles):
                print('Skipping this application, a blacklisted keyword was found in the job position.')
                string_easy = "* Contains blacklisted keyword"
                result = False
            else:
                string_easy = "* has Easy Apply Button"
                print("Found Easy Apply button and clicking the button.")
                time.sleep(1)
                try:
                    self.browser.execute_script("arguments[0].click();", button)
                    print("Successfully clicked the Easy Apply button using JavaScript.")
                except Exception as e:
                    print(f"Failed to click the Easy Apply button: {e}")
                    string_easy = "* Failed to click Easy Apply Button"
                    result = False
                    self.write_to_file(button, job_id, self.browser.title, result)
                    return result
                time.sleep(2)
                self.fill_out_fields()
                result = self.send_resume()
                if result:
                    string_easy = '*Applied: Sent the Resume'
                else:
                    string_easy = '*Did not apply: Failed to send Resume'
        
        print(f"\nPosition {job_id}:\n {self.browser.title} \n {string_easy} \n")
        self.write_to_file(button, job_id, self.browser.title, result)
        return result
    
    def get_job_page(self, job_id):
        """Navigate to the job page"""
        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
        self.browser.get(job_url)
        self.load_page()
        time.sleep(1)
    
    def load_page(self):
        """Load and scroll the page to ensure all content is loaded"""
        scrollpage = 0
        while scrollpage < 4000:
            self.browser.execute_script(f"window.scrollTo(0, {scrollpage});")
            scrollpage += 500
            time.sleep(0.2)
        time.sleep(3)
        self.browser.execute_script("window.scrollTo(0,0);")
    
    def close_overlays(self):
        """Close any overlay dialogs"""
        try:
            close_buttons = self.browser.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
            for close_button in close_buttons:
                close_button.click()
                time.sleep(1)
        except Exception as e:
            print(f"No overlays found or error closing overlay: {e}")
    
    def is_present(self, locator):
        """Check if an element is present on the page"""
        return len(self.browser.find_elements(locator[0], locator[1])) > 0
    
    def get_elements(self, type):
        """Get elements by locator type"""
        elements = []
        element = self.locator[type]
        if self.is_present(element):
            elements = self.browser.find_elements(element[0], element[1])
        return elements
    
    def get_easy_apply_button(self):
        """Find the Easy Apply button on the page"""
        print("Looking for Easy Apply button...")
        selectors = [
            (By.XPATH, '//button[contains(@class, "jobs-apply-button") and contains(., "Easy Apply")]'),
            (By.XPATH, '//button[contains(@class, "jobs-apply-button")]'),
            (By.CSS_SELECTOR, 'button.jobs-apply-button'),
            (By.XPATH, '//button[contains(text(), "Easy Apply")]'),
            (By.XPATH, '//button[contains(@aria-label, "Easy Apply")]'),
        ]
        try:
            for by, selector in selectors:
                try:
                    print(f"Trying selector: {selector}")
                    button = self.wait.until(EC.element_to_be_clickable((by, selector)))
                    if button and ("Easy Apply" in button.text or "Apply easily" in button.text or button.get_attribute("aria-label") and "Easy Apply" in button.get_attribute("aria-label")):
                        self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        print(f"Easy Apply button found with selector: {selector}")
                        return button
                except TimeoutException:
                    continue
            
            # Fallback: search all buttons for text
            print("Trying fallback: searching all <button> elements for 'Easy Apply' text...")
            all_buttons = self.browser.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                try:
                    text = button.text or ""
                    aria = button.get_attribute("aria-label") or ""
                    if ("Easy Apply" in text) or ("Easy Apply" in aria) or ("Apply easily" in text):
                        if button.is_enabled() and button.is_displayed():
                            self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                            print("Easy Apply button found in fallback search!")
                            return button
                except Exception:
                    continue
            print("Easy Apply button not found with any selector.")
        except Exception as e:
            print(f"Exception while finding Easy Apply button: {e}")
        return None
    
    def fill_out_fields(self):
        """Fill out form fields"""
        fields = self.browser.find_elements(By.CLASS_NAME, "fb-dash-form-element")
        for field in fields:
            if "Mobile phone number" in field.text:
                field_input = field.find_element(By.TAG_NAME, "input")
                field_input.clear()
                field_input.send_keys(self.phonenumber)
    
    def send_resume(self):
        """Send resume and complete application"""
        try:
            next_locator = (By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
            review_locator = (By.CSS_SELECTOR, "button[aria-label='Review your application']")
            submit_locator = (By.CSS_SELECTOR, "button[aria-label='Submit application']")
            error_locator = (By.CLASS_NAME, "artdeco-inline-feedback__message")
            upload_resume_locator = (By.XPATH, '//span[text()="Upload resume"]')
            upload_cv_locator = (By.XPATH, '//span[text()="Upload cover letter"]')
            follow_locator = (By.CSS_SELECTOR, "label[for='follow-company-checkbox']")
            submitted = False
            loop = 0
            
            while loop < 2:
                time.sleep(3)
                if self.is_present(upload_resume_locator):
                    try:
                        resume_locator = self.browser.find_element(By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-resume')]")
                        resume_locator.send_keys(self.resume_path)
                    except Exception as e:
                        print(f"Resume upload failed: {e}")
                
                if self.is_present(upload_cv_locator):
                    try:
                        cv_locator = self.browser.find_element(By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-cover-letter')]")
                        cv_locator.send_keys(self.uploads.get("Cover Letter", ""))
                    except Exception as e:
                        print(f"Cover letter upload failed: {e}")
                
                if self.is_present(follow_locator):
                    elements = self.get_elements("follow")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()
                
                if self.is_present(submit_locator):
                    elements = self.get_elements("submit")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()
                        print("Application Submitted")
                        submitted = True
                        break
                
                elif self.is_present(error_locator):
                    elements = self.get_elements("error")
                    if "application was sent" in self.browser.page_source:
                        print("Application Submitted")
                        submitted = True
                        break
                    elif elements:
                        while elements:
                            for element in elements:
                                self.process_questions()
                            print("Answering questions, waiting 20 seconds...")
                            time.sleep(20)
                            elements = self.get_elements("error")
                            if "application was sent" in self.browser.page_source:
                                print("Application Submitted")
                                submitted = True
                                break
                            elif self.is_present(self.locator["easy_apply_button"]):
                                print("Skipping application")
                                submitted = False
                                break
                        continue
                    else:
                        break
                
                elif self.is_present(next_locator):
                    elements = self.get_elements("next")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()
                
                elif self.is_present(review_locator):
                    elements = self.get_elements("review")
                    for element in elements:
                        button = self.wait.until(EC.element_to_be_clickable(element))
                        button.click()
                
                # loop += 1
        
        except Exception as e:
            print(f"Cannot apply to this job: {e}")
        
        return submitted
    
    def process_questions(self):
        """Process application questions"""
        time.sleep(3)
        form = self.get_elements("fields")
        time.sleep(2)
        for field in form:
            question = field.text
            answer = self.answer_questions(question.lower())
            
            if self.is_present(self.locator["radio_select"]):
                try:
                    input = field.find_element(By.CSS_SELECTOR, f"input[type='radio'][value='{answer}']")
                    input.click()
                except Exception as e:
                    print(e)
            
            elif self.is_present(self.locator["multi_select"]):
                try:
                    input = field.find_element(*self.locator["multi_select"])
                    input.send_keys(answer)
                except Exception as e:
                    print(e)
            
            elif self.is_present(self.locator["text_select"]):
                try:
                    input = field.find_element(*self.locator["text_select"])
                    input.send_keys(answer)
                except Exception as e:
                    print(e)
    
    def answer_questions(self, question):
        """Answer application questions"""
        answer = None
        if "salary" in question:
            answer = self.salary
        elif "gender" in question:
            answer = self.gender
        elif "relocate" in question:
            answer = "Yes"
        elif "bachelor's degree" in question:
            answer = "Yes"
        elif "are you comfortable" in question:
            answer = "Yes"
        elif "race" in question:
            answer = "Wish not to answer"
        elif "lgbtq" in question:
            answer = "Wish not to answer"
        elif "ethnicity" in question:
            answer = "Wish not to answer"
        elif "nationality" in question:
            answer = "Wish not to answer"
        elif "government" in question:
            answer = "I do not wish to self-identify"
        elif "are you legally" in question:
            answer = "Yes"
        elif "US citizen" in question:
            answer = "Yes"
        else:
            print(f"Not able to answer question automatically. Please provide answer for: {question}")
            answer = input("Enter your answer: ")
            if question not in self.answer:
                self.answer[question] = answer
                new_data = pd.DataFrame({"Question": [question], "Answer": [answer]})
                new_data.to_csv(self.qa_file, mode='a', header=False, index=False, encoding='utf-8')
        
        print(f"Answering question: {question} with answer: {answer}")
        return answer
    
    def write_to_file(self, button, job_id, browser_title, result):
        """Write application result to file"""
        def re_extract(text, pattern):
            target = re.search(pattern, text)
            return target.group(1) if target else text
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attempted = button is not None
        job = re_extract(browser_title.split(' | ')[0], r"\(?\d?\)?\s?(\w.*)")
        company = re_extract(browser_title.split(' | ')[1], r"(\w.*)")
        to_write = [timestamp, job_id, job, company, attempted, result]
        
        with open(self.filename, 'a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(to_write)