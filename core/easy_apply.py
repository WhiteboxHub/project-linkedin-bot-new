"""
LinkedIn Easy Apply - Enhanced Version
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


def logged_sleep(seconds):
    """Sleep with logging"""
    time.sleep(seconds)


class ApplicationStats:
    """Track application statistics in real-time"""
    
    def __init__(self):
        self.total_found = 0
        self.already_applied = 0
        self.successfully_applied = 0
        self.failed = 0
        self.skipped = 0
        self.start_time = datetime.now()
    
    def print_stats(self):
        """Print current statistics"""
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        
        print("\n" + "="*60)
        print("APPLICATION STATISTICS")
        print("="*60)
        print(f"Time Elapsed: {elapsed:.1f} minutes")
        print(f"Jobs Found: {self.total_found}")
        print(f"Successfully Applied: {self.successfully_applied}")
        print(f"Already Applied: {self.already_applied}")
        print(f"Failed: {self.failed}")
        print(f"Skipped: {self.skipped}")
        print("="*60 + "\n")


def apply_to_jobs_with_search(config_path):
    """
    Main entry point: Page-by-page search and apply
    """
    Path("output/applications").mkdir(parents=True, exist_ok=True)
    Path("Qa").mkdir(parents=True, exist_ok=True)
   
    apply_bot = ApplyBot(config_path)
    
    try:
        apply_bot.login_linkedin()
        
        total_applications = apply_bot.search_and_apply_all()

        apply_bot.stats.print_stats()
        
        print(f"\n{'='*60}")
        print(f"APPLICATION PROCESS COMPLETED!")
        print(f"{'='*60}")
        print(f"Successfully Applied: {apply_bot.stats.successfully_applied} jobs")
        print(f"Results saved to: {apply_bot.filename}")
        print(f"Q&A saved to: {apply_bot.qa_file}")
        print(f"{'='*60}\n")
        
        return total_applications
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 0
        
    finally:
        try:
            apply_bot.browser.quit()
            print("Browser closed")
        except:
            pass


class ApplyBot:
    """Enhanced ApplyBot with all requirements"""
    
    def __init__(self, config_path):
        """Initialize the ApplyBot"""
        import yaml
        
        with open(config_path, 'r') as stream:
            try:
                parameters = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc
        
        # Set instance variables
        self.username = parameters['username']
        self.password = parameters['password']
        self.phonenumber = parameters['phone_number']
        self.salary = parameters['salary']
        self.rate = parameters['rate']
        self.uploads = {} if parameters.get('uploads', {}) is None else parameters.get('uploads', {})
        self.resume_path = get_resume_path(self.uploads.get("Resume", ""))
        self.roletype = parameters.get('roletype', [])
        self.locations = parameters.get('locations', [])
        self.positions = parameters.get('positions', [])
        self.experiencelevel = parameters.get('experience_level', [])
        self.filename = f"output/applications/Output_of_{parameters['username']}.csv"
        self.blacklist = parameters.get('blacklist', [])
        self.blacklisttitles = parameters.get('blackListTitles', [])
        self.gender = parameters['gender']
        self.qa_file = Path(f"output/applications/qa_{self.username}.csv")
        self.answer = {}
        
        self.date_filter = parameters.get('date_posted', 'r86400')  # Default: Past 24 hours
        
        self.stats = ApplicationStats()
        
        print("Initializing browser...")
        self.browser = get_browser()
        self.wait = WebDriverWait(self.browser, 30)
        print("Browser ready\n")
        
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
        }
        
        if self.qa_file.is_file():
            df = pd.read_csv(self.qa_file)
            for index, row in df.iterrows():
                self.answer[row['Question']] = row["Answer"]
            print(f"Loaded {len(self.answer)} saved answers")
        else:
            df = pd.DataFrame(columns=["Question", "Answer"])
            df.to_csv(self.qa_file, index=False, encoding='utf-8')
            print("Created Q&A database")
        
        # Create CSV with headers if doesn't exist
        if not Path(self.filename).exists():
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Job ID', 'Job Title', 'Company', 'Attempted', 'Success'])
        
        print(f"Initialization complete. Results will be saved to: {self.filename}")


    def get_date_filter_name(self, code=None):
        """Get human-readable date filter name"""
        filters = {
            'r86400': 'Past 24 hours',
            'r604800': 'Past Week',
            'r2592000': 'Past Month',
            '': 'Any Time'
        }
        return filters.get(code, 'Custom')

    def login_linkedin(self):
        """Login to LinkedIn"""
        print("Logging in to LinkedIn...")
        self.browser.get('https://www.linkedin.com/login')
        logged_sleep(8)
        
        try:
            self.browser.find_element(By.ID, 'username').clear()
            self.browser.find_element(By.ID, 'username').send_keys(self.username)
            self.browser.find_element(By.ID, 'password').clear()
            self.browser.find_element(By.ID, 'password').send_keys(self.password)
            self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
            logged_sleep(10)
            print("Login successful\n")
        except:
            print("Already logged in\n")

    def search_and_apply_all(self):
        """Main orchestrator: Search and apply page-by-page"""
        print("\n" + "="*60)
        print("STARTING PAGE-BY-PAGE APPLICATION")
        print("="*60 + "\n")
        
        total_applications = 0
        
        for position in self.positions:
            for location in self.locations:
                print(f"\n{'='*60}")
                print(f"Searching: {position} in {location}")
                print(f"{'='*60}\n")
                
                try:
                    applications = self.search_and_apply_for_position(position, location)
                    total_applications += applications
                except Exception as e:
                    print(f"Error: {e}")
                    continue
        
        return total_applications

    def search_and_apply_for_position(self, position, location):
        """Search and apply for one position/location - Recent jobs first"""
        # Only search recent jobs (Past 24 hours) first
        date_filters = ['r86400']  # Only recent jobs
        total_applied = 0

        for date_filter in date_filters:
            print(f"\n{'='*60}")
            print(f"Searching for {position} in {location}")
            print(f"Date filter: {self.get_date_filter_name(date_filter)}")
            print(f"Sorting by: Most Recent")
            print(f"{'='*60}\n")

            exp_lvl_str = ",".join(map(str, self.experiencelevel)) if self.experiencelevel else ""
            exp_lvl_param = f"&f_E={exp_lvl_str}" if exp_lvl_str else ""
            location_str = f"&location={location}"
            position_str = f"&keywords={position}"
            rolestring = self.roletype_to_string(self.roletype)
            date_param = f"&f_TPR={date_filter}" if date_filter else ""
            sort_param = "&sortBy=DD"  # Sort by Date Descending (Most Recent First)
            job_per_page = 0
            max_pages = 10

            for page_num in range(max_pages):
                print(f"\n{'-'*50}")
                print(f"PAGE {page_num + 1}")
                print(f"{'-'*50}\n")

                URL = f"https://www.linkedin.com/jobs/search/?f_LF=f_AL{position_str}{rolestring}{location_str}{exp_lvl_param}{date_param}{sort_param}&start={job_per_page}"

                try:
                    self.browser.get(URL)
                    logged_sleep(3)
                except Exception as e:
                    print(f"Failed to load page: {e}")
                    break

                self.close_overlays()

                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-job-id]')))
                except TimeoutException:
                    print("No more jobs found")
                    break

                self.load_page()

                job_cards = self.get_job_cards_with_status()

                if not job_cards:
                    print("No job cards found")
                    break

                print(f"Found {len(job_cards)} jobs on this page")

                for idx, (job_id, already_applied) in enumerate(job_cards, 1):
                    self.stats.total_found += 1

                    print(f"\n{'-'*60}")
                    print(f"[Page {page_num + 1}, Job {idx}/{len(job_cards)}] Job ID: {job_id}")
                    print(f"{'-'*60}")

                    if already_applied:
                        print("Already applied - skipping")
                        self.stats.already_applied += 1
                        continue

                    try:
                        result = self.apply_to_job(job_id)
                        if result:
                            total_applied += 1
                            self.stats.successfully_applied += 1
                            print(f"APPLICATION #{self.stats.successfully_applied} SUCCESSFUL!")
                        else:
                            self.stats.failed += 1
                    except Exception as e:
                        print(f"Error: {e}")
                        self.stats.failed += 1
                        continue

                    logged_sleep(2)

                self.stats.print_stats()
                job_per_page += 25
                logged_sleep(3)

        return total_applied

    def get_job_cards_with_status(self):
        """Get job cards and check if already applied"""
        job_cards = []
        
        try:
            cards = self.browser.find_elements(By.XPATH, '//div[@data-job-id]')
            
            for card in cards:
                try:
                    job_id = card.get_attribute("data-job-id")
                    if not job_id or job_id == "search":
                        continue
                    
                    already_applied = False
                    
                    text = card.text or ""
                    if 'Applied' in text or 'Application viewed' in text:
                        already_applied = True
                    
                    try:
                        card.find_element(By.XPATH, ".//*[contains(@class, 'job-card-container__footer-job-state')]")
                        already_applied = True
                    except:
                        pass
                    
                    if text in self.blacklist:
                        already_applied = True
                    
                    job_cards.append((job_id, already_applied))
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"Error getting job cards: {e}")
        
        return job_cards

    def roletype_to_string(self, roletype):
        """Convert role type to URL parameter"""
        if not roletype:
            return ""
        if roletype == [1]:
            return "&f_WT=1"
        if roletype == [2]:
            return "&f_WT=2"
        if roletype == [3]:
            return "&f_WT=3"
        if roletype == [1, 2]:
            return "&f_WT=1%2C2"
        if roletype == [1, 3]:
            return "&f_WT=1%2C3"
        if roletype == [2, 3]:
            return "&f_WT=2%2C3"
        if roletype == [1, 2, 3]:
            return "&f_WT=1%2C2%2C3"
        return ""
        
    def apply_to_job(self, job_id):
        """Apply to a job"""
        self.get_job_page(job_id)
        logged_sleep(4)
        self.close_overlays()
        
        button = self.get_easy_apply_button()
        
        if button is None:
            if "You applied on" in self.browser.page_source:
                print("Already applied")
                return False
            else:
                print("Easy Apply button not found")
                return False
        
        if any(word in self.browser.title for word in self.blacklisttitles):
            print('Skipping: blacklisted keyword')
            return False
        
        print("Clicking Easy Apply...")
        logged_sleep(1)
        
        try:
            self.browser.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"Click failed: {e}")
            return False
        
        logged_sleep(2)
        self.fill_out_fields()
        
        result = self.send_resume_persistent()
        
        if result:
            print(f"Successfully applied!")
        else:
            print(f"Failed to apply")
        
        self.write_to_file(button, job_id, self.browser.title, result)
        return result
        
    def send_resume_persistent(self):
        """Send resume and complete application"""
        try:
            next_locator = (By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
            review_locator = (By.CSS_SELECTOR, "button[aria-label='Review your application']")
            submit_locator = (By.CSS_SELECTOR, "button[aria-label='Submit application']")
            error_locator = (By.CLASS_NAME, "artdeco-inline-feedback__message")
            upload_resume_locator = (By.XPATH, "//*[contains(@id, 'jobs-document-upload-file-input-upload-resume')]")
            follow_locator = (By.CSS_SELECTOR, "label[for='follow-company-checkbox']")

            submitted = False

            while True:
                logged_sleep(2)

                # Upload resume if required
                if self.is_present(upload_resume_locator):
                    try:
                        resume_input = self.browser.find_element(*upload_resume_locator)
                        if self.resume_path:
                            resume_input.send_keys(self.resume_path)
                            print("Resume uploaded")
                    except Exception as e:
                        print(f"Resume upload issue: {e}")

                # Follow company
                if self.is_present(follow_locator):
                    try:
                        elements = self.get_elements("follow")
                        for element in elements:
                            button = self.wait.until(EC.element_to_be_clickable(element))
                            button.click()
                            print("Following company")
                            break
                    except Exception:
                        pass

                # Submit
                if self.is_present(submit_locator):
                    try:
                        submit_btn = self.wait.until(EC.element_to_be_clickable(submit_locator))
                        submit_btn.click()
                        print("Application submitted successfully.")
                        submitted = True
                        break
                    except Exception as e:
                        print(f"Submit issue: {e}")

                # Already submitted
                elif "application was sent" in self.browser.page_source:
                    print("Application already submitted.")
                    submitted = True
                    break

                # Next step
                elif self.is_present(next_locator):
                    try:
                        next_btn = self.wait.until(EC.element_to_be_clickable(next_locator))
                        next_btn.click()
                        print("Next step clicked")
                    except Exception:
                        break

                # Review
                elif self.is_present(review_locator):
                    try:
                        review_btn = self.wait.until(EC.element_to_be_clickable(review_locator))
                        review_btn.click()
                        print("Review clicked")
                    except Exception:
                        break

                # No more steps
                else:
                    print("Job closed or cannot proceed. Moving to next job.")
                    break

            return submitted

        except Exception as e:
            print(f"Error during application: {e}")
            return False

    def process_questions_persistent(self):
        """Process questions without skipping"""
        logged_sleep(2)
        form = self.get_elements("fields")
        
        all_answered = True
        
        for field in form:
            try:
                question = field.text
                if not question or len(question.strip()) == 0:
                    continue
                
                answer = self.answer_questions(question.lower())
                
                if answer is None:
                    all_answered = False
                    continue
                
                answered_this_field = False
                
                # Try radio
                try:
                    radios = field.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radios:
                        for r in radios:
                            try:
                                val = r.get_attribute('value') or ''
                                label = ''
                                try:
                                    lab = r.find_element(By.XPATH, './ancestor::label')
                                    label = lab.text or ''
                                except:
                                    pass
                                
                                if str(answer).lower() in str(val).lower() or str(answer).lower() in str(label).lower():
                                    try:
                                        r.click()
                                        answered_this_field = True
                                        break
                                    except:
                                        self.browser.execute_script("arguments[0].click();", r)
                                        answered_this_field = True
                                        break
                            except:
                                continue
                        
                        if answered_this_field:
                            continue
                except:
                    pass
                
                # Try text input
                try:
                    inputs = field.find_elements(By.CSS_SELECTOR, "input[type='text'], textarea")
                    if inputs:
                        try:
                            inputs[0].clear()
                            inputs[0].send_keys(answer)
                            answered_this_field = True
                            continue
                        except:
                            pass
                except:
                    pass
                
                if not answered_this_field:
                    print(f"Could not answer: {question[:50]}...")
                    all_answered = False
                    
            except Exception as e:
                print(f"Question processing error: {e}")
                all_answered = False
                continue
        
        return all_answered
    
    def answer_questions(self, question):
        """Answer questions"""
        answer = None
        
        if "salary" in question:
            answer = self.salary
        elif "gender" in question:
            answer = self.gender
        elif "relocate" in question:
            answer = "Yes"
        elif "bachelor's degree" in question or "degree" in question:
            answer = "Yes"
        elif "are you comfortable" in question:
            answer = "Yes"
        elif "race" in question or "ethnicity" in question:
            answer = "Wish not to answer"
        elif "lgbtq" in question:
            answer = "Wish not to answer"
        elif "are you legally" in question or "authorized" in question:
            answer = "Yes"
        elif "US citizen" in question:
            answer = "Yes"
        elif "years of experience" in question:
            answer = "3"
        elif "notice period" in question:
            answer = "2 weeks"
        else:
            if question in self.answer:
                answer = self.answer[question]
            else:
                print(f"\n{'!'*60}")
                print(f"NEW QUESTION REQUIRES YOUR INPUT:")
                print(f"{'!'*60}")
                print(f"Q: {question}")
                user_answer = input("Your answer (or press Enter to skip): ").strip()
                
                if user_answer:
                    answer = user_answer
                    self.answer[question] = answer
                    new_data = pd.DataFrame({"Question": [question], "Answer": [answer]})
                    new_data.to_csv(self.qa_file, mode='a', header=False, index=False, encoding='utf-8')
                    print(f"Answer saved for future applications")
                else:
                    print(f"Skipping this question for now")
                    return None
        
        if answer:
            print(f"Answering: {question[:40]}... -> {answer}")
        
        return answer
    
    def get_job_page(self, job_id):
        """Navigate to job page"""
        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
        self.browser.get(job_url)
        self.load_page()
        logged_sleep(1)

    def load_page(self):
        """Load and scroll page"""
        scrollpage = 0
        while scrollpage < 4000:
            self.browser.execute_script(f"window.scrollTo(0, {scrollpage});")
            scrollpage += 500
            time.sleep(0.2)
        logged_sleep(2)
        self.browser.execute_script("window.scrollTo(0,0);")
    
    def close_overlays(self):
        """Close overlay dialogs"""
        try:
            close_buttons = self.browser.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
            for close_button in close_buttons:
                close_button.click()
                time.sleep(1)
        except:
            pass
    
    def is_present(self, locator):
        """Check if element present"""
        return len(self.browser.find_elements(locator[0], locator[1])) > 0
    
    def get_elements(self, type):
        """Get elements by type"""
        elements = []
        element = self.locator[type]
        if self.is_present(element):
            elements = self.browser.find_elements(element[0], element[1])
        return elements
    
    def get_easy_apply_button(self):
        """Find Easy Apply button"""
        print("Looking for Easy Apply button...")

        logged_sleep(2)
        try:
            self.browser.execute_script("window.scrollTo(0, 400);")
            logged_sleep(0.5)
            self.browser.execute_script("window.scrollTo(0, 0);")
        except:
            pass

        selectors = [
            (By.CSS_SELECTOR, "button.jobs-apply-button--top-card"),
            (By.CSS_SELECTOR, "button[aria-label*='Easy Apply']"),
            (By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_inapply']"),
            (By.XPATH, "//button[contains(text(), 'Easy Apply')]"),
            (By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"),
            (By.CSS_SELECTOR, "button.artdeco-button--primary"),
        ]

        def is_easy_apply(elem):
            """Check if element is Easy Apply button"""
            text = (elem.text or "").lower()
            aria = (elem.get_attribute("aria-label") or "").lower()
            data = (elem.get_attribute("data-control-name") or "").lower()
            classes = (elem.get_attribute("class") or "").lower()

            easy = any(x in text or x in aria or x in data or x in classes
                    for x in ["easy apply", "apply easily", "inapply"])
            bad = any(x in text or x in aria for x in
                    ["save", "share", "message", "follow", "applied", "application sent", "view application"])
            return easy and not bad

        
        for idx, (by, sel) in enumerate(selectors, 1):
            try:
                elements = self.browser.find_elements(by, sel)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled() and is_easy_apply(elem):
                        self.browser.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", elem
                        )
                        print(f"Found Easy Apply button using selector #{idx}")
                        return elem
            except:
                continue

        
        print("Primary selectors failed, scanning all buttons...")
        try:
            for button in self.browser.find_elements(By.TAG_NAME, "button"):
                if button.is_displayed() and is_easy_apply(button):
                    self.browser.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", button
                    )
                    print("Found Easy Apply button in fallback scan")
                    return button
        except:
            pass

        # Check for external application
        try:
            external = self.browser.find_elements(
                By.XPATH,
                "//a[contains(text(), 'Apply on company website')] | "
                "//button[contains(text(), 'Apply on company website')]"
            )
            if external:
                print("External application detected - not Easy Apply.")
                return None
        except:
            pass

        print("Easy Apply button not found.")
        return None

    def fill_out_fields(self):
        """Fill out form fields"""
        try:
            fields = self.browser.find_elements(By.CLASS_NAME, "fb-dash-form-element")
            for field in fields:
                if "Mobile phone number" in field.text:
                    field_input = field.find_element(By.TAG_NAME, "input")
                    field_input.clear()
                    field_input.send_keys(self.phonenumber)
                    print("Phone filled")
        except:
            pass
    
    def write_to_file(self, button, job_id, browser_title, result):
        """Write to CSV"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            attempted = button is not None
            
            title_parts = browser_title.split(' | ')
            job = title_parts[0] if len(title_parts) > 0 else "Unknown"
            company = title_parts[1] if len(title_parts) > 1 else "Unknown"
            
            to_write = [timestamp, job_id, job, company, attempted, result]
            
            with open(self.filename, 'a+', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(to_write)
        except Exception as e:
            print(f"CSV write error: {e}")