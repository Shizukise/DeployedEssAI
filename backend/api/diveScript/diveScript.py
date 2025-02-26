from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import logging
from backend.app import app, db
from backend.api.diveScript.models import SpecificArticle
from .utils import departments
import subprocess
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiverScraper:
    """
    Attributes:
        username (str): Username for login.
        password (str): Password for login.
        team (str): Team name to filter data.
        driver (webdriver): Selenium WebDriver instance for Chrome.
        specific_materials (set): A set of material names to identify relevant articles during scraping.
    """

    def __init__(self, password, username="Atelier", team="Tous"):
        """Initialize DiverScraper with compatibility checks and fallbacks."""
        self.username = username
        self.password = password
        self.team = team

        self._initialize_memory()

        # Configure options
        self._configure_options()

        # Initialize driver
        self.driver = self._get_chromium_driver()

        self.specific_materials = set(["Dibond", "Plexi", "PVC3MM", "entretoises"])

    def _configure_options(self):
        """Configure Chrome options for headless mode and low resource usage."""
        self.options = Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=800,600")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--single-process")
        self.options.add_argument("--no-zygote")
        self.options.add_argument("--renderer-process-limit=1")
        self.options.add_argument("--max-old-space-size=256")
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 2,
            "profile.managed_default_content_settings.images": 2,
        })
        self.options.binary_location = "/usr/bin/google-chrome"

    def _get_chromium_driver(self):
        """Initialize the ChromeDriver using the system-installed binary."""
        try:
            # Use the system-installed ChromeDriver
            driver_path = "/usr/bin/chromedriver"
            service = Service(executable_path=driver_path)
            return webdriver.Chrome(service=service, options=self.options)
        except Exception as e:
            logger.error(f"Error initializing ChromeDriver: {e}")
            raise

    def _initialize_memory(self):
        """Initialize the memory context by fetching stored order IDs from the database."""
        with app.app_context():
            self.memory = {item.order_CO for item in SpecificArticle.query.all()}

    def clean_search_filters(self):
        """
        Clears all search filters on the web page. This resets previous filter inputs
        like order number, client name, and other fields.
        """
        filter_ids = ['filter-ref', 'filter-ct-number', 'filter-societe',
                      'filter-site', 'filter-site-address', 'filter-site-contact', 'filter-date']

        for field_id in filter_ids:
            try:
                field = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, field_id)))
                field.clear()
                logger.debug(f"Cleared filter field: {field_id}")
            except TimeoutException:
                logger.warning(f"Timeout while clearing filter field: {field_id}")
                continue

        # Submit the cleared filters
        try:
            field.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'dataTable')]")))
            logger.info("Search filters cleared successfully")
        except Exception as e:
            logger.error(f"Error submitting cleared filters: {e}")

    def apply_search_filters(self):
        """
        Applies search filters to the page. Specifically:
        - Filters for orders with status 'BAT validé'.
        - Filters by team name provided during initialization.
        """
        try:
            # Open status filter and select 'BAT validé'
            statut_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-id='filter-status']")))
            statut_button.click()

            option_bat_valide = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='BAT validé']")))
            option_bat_valide.click()
            logger.debug("Applied 'BAT validé' filter")

            if self.team != "Tous":
                # Open team filter and select specified team
                groupe_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-id='filter-designer-group']")))
                groupe_button.click()

                team_select = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{self.team}']")))
                team_select.click()
                logger.debug(f"Applied team filter: {self.team}")

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            raise

    def close_popups(self):
        """
        Closes any pop-up windows that may appear on the page.
        """
        try:
            popup_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//button[contains(text(),'OK') or contains(text(),'Valider') or contains(text(),'Fermer')]"))
            )
            popup_button.click()
            logger.debug("Closed popup")
        except TimeoutException:
            logger.debug("No popups found")
        except Exception as e:
            logger.warning(f"Error closing popup: {e}")

    def scrape_data_from_order_page(self, commande_id):
        """
        Scrapes data (articles and department) from a specific order page.
        """
        articles = []
        cdepartment = None
        try:
            # Execute JavaScript to reveal hidden columns
            self.driver.execute_script("""
                var hiddenColumns = document.querySelectorAll('.dtr-hidden');
                hiddenColumns.forEach(function(column) {
                    column.classList.remove('dtr-hidden');
                });
            """)

            # Wait for table to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'dataTable')]/tbody"))
            )

            # Get and decode the page source
            html_content = self.driver.page_source.encode("utf-8").decode("utf-8")

            # Find department
            for department in departments:
                if department in html_content:
                    cdepartment = department
                    break
            if cdepartment is None:
                cdepartment = "Inconnue"
                logger.warning(f"No department found for commande {commande_id}")

            # Extract article data
            lignes_articles = self.driver.find_elements(By.XPATH,
                                                        "//tr[contains(@class, 'even') or contains(@class, 'odd')]")

            for ligne in lignes_articles:
                try:
                    description = WebDriverWait(ligne, 10).until(
                        EC.visibility_of_element_located((By.XPATH, ".//td[1]"))
                    ).text.encode("utf-8").decode("utf-8")

                    quantite_element = WebDriverWait(ligne, 10).until(
                        EC.visibility_of_element_located((By.XPATH, ".//td[4]"))
                    ).text.encode("utf-8").decode("utf-8")
                    quantite = float(quantite_element) if quantite_element else "Inconnue"

                    if any(material.lower().strip().lower() in description.lower()
                           for material in self.specific_materials):
                        articles.append({
                            "Description": description.strip(),
                            "Quantité": quantite
                        })

                    if "divart" in description.lower() or "diver" in description.lower():
                        try:
                            collapse_button = WebDriverWait(ligne, 10).until(
                                EC.element_to_be_clickable((By.XPATH,
                                                            ".//td[1]//a[@data-toggle='collapse']")))
                            collapse_button.click()

                            diver_specific = WebDriverWait(ligne, 10).until(
                                EC.visibility_of_element_located((By.XPATH,
                                                                  ".//td[1]//div[contains(@class,'collapse') and contains(@class,'in')]"))
                            ).text.encode("utf-8").decode("utf-8")

                            quantite_elementDiv = ligne.find_element(By.XPATH,
                                                                    ".//td[4]").text.encode("utf-8").decode("utf-8")
                            quantiteDiv = float(quantite_elementDiv) if quantite_elementDiv else "Inconnue"

                            articles.append({
                                "Description": diver_specific.strip(),
                                "Quantité": quantiteDiv
                            })
                        except Exception as e:
                            logger.warning(f"Error handling collapse for row: {e}")
                except Exception as e:
                    logger.warning(f"Error extracting line for commande {commande_id}: {e}")
        except Exception as e:
            logger.error(f"Error extracting data for commande {commande_id}: {e}")
            raise

        return articles, cdepartment

    def run_scraper(self):
        """
        Loops through all order pages, scrapes relevant data, and navigates through pagination.

        Returns:
            list[dict]: A list of dictionaries containing order ID and its articles.
        """
        commandes = []
        current_page = 1
        seen_CO = []
        try:
            # Navigate through pages
            while True:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/commande/view/')]")))
                commande_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/commande/view/')]")
                for idx, element in enumerate(commande_elements):

                    commande_url = element.get_attribute("href")
                    commande_id = element.text

                    if commande_id in [CO for CO in self.memory]:  # self.memory on __init__ hold all commandes stored in database
                        continue  # if command is already in database, it means it got already scraped.
                    # we have commandes that already have been resolved.
                    self.driver.execute_script("window.open(arguments[0], '_blank');", commande_url)
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(2)

                    self.close_popups()
                    self.driver.execute_script("document.charset = 'UTF-8';")
                    articles, department = self.scrape_data_from_order_page(commande_id)
                    if len(articles) > 0:
                        commandes.append(
                            {"Référence": commande_id, "Articles Spécifiques": articles, "HREF": commande_url,
                             "Department": department})
                    if commande_id in seen_CO:
                        self.driver.quit()
                        return commandes
                    seen_CO.append(commande_id)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                # Handle pagination
                try:
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@title='Page Suivante']")))
                    next_button.click()
                    print(f"trying to move from page {current_page} to page {current_page + 1}")
                    # Check if the button is disabled
                    if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                        print("Pagination button is disabled. Last page reached.")
                        break
                    time.sleep(3)
                    current_page += 1
                except:
                    print("Dernière page atteinte, arrêt de la boucle.")
                    break
        except Exception as e:
            print(f"Erreur lors de l'extraction des commandes : {e}")
        return commandes

    def run_script(self):
        """
        Main function that runs the scraper:
        - Logs in to the website.
        - Clears and applies search filters.
        - Scrapes data and returns the results.

        Returns:
            list[dict]: A list of orders with their associated articles.
        """
        try:
            logger.info("Trying to access webapp")
            self.driver.get("https://plans.desautel-sai.fr/plans/commande/list")
            logger.info("Webapp accessed!")
            time.sleep(2)

            # Login steps
            login_box = self.driver.find_element(By.ID, "username")
            password_box = self.driver.find_element(By.ID, "password")
            login_box.send_keys(self.username)
            password_box.send_keys(self.password)
            login_box.send_keys(Keys.RETURN)
            time.sleep(3)

            print("logged in")
            # Filters and scraping
            self.clean_search_filters()
            time.sleep(2)
            self.apply_search_filters()
            time.sleep(2)
            ("filters aplied, scraper will run")
            data = self.run_scraper()
            return data
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []
        finally:
            self.driver.quit()