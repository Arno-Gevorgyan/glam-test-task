# Standard library
import random
import shutil

# External libraries
from sqlalchemy.ext.asyncio import AsyncSession

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

# Custom modules
from db.models import UserModel
from db.models._instagram import InstagramModel
from gql.base.types import MessageType
from gql.instagram.types import InstagramInput, InstagramType
from messages import ErrorMessage

CHROME_DRIVER_PATH = shutil.which("chromedriver")
if not CHROME_DRIVER_PATH:
    raise ValueError("chromedriver is not found in system's PATH.")

# Define a list of User-Agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1"
]


class InstagramDatabaseService:
    """
    Class responsible for database interactions related to Instagram data.
    """

    @staticmethod
    async def create_instagram_entry(session: AsyncSession, user: UserModel, photo_links: list,
                                     instagram_username: str) -> InstagramModel:
        """
        Creates a new InstagramModel entry with the given photo URLs and associates it with the provided user.

        :param session: An instance of AsyncSession for executing asynchronous database operations.
        :param user: The user model instance representing the user associated with the Instagram data.
        :param photo_links: A list of URLs representing the photos extracted from Instagram.
        :param instagram_username: Username for instagram account.

        :return: A newly created instance of the InstagramModel representing the stored data.
        """
        new_entry = InstagramModel(user_id=user.id, photo_urls=photo_links, account_username=instagram_username)

        # Add the new entry to the session
        session.add(new_entry)

        # Commit the session to save the changes to the database
        await session.commit()
        return new_entry


class InstagramScraperError(Exception):
    """
    Custom exception for errors during Instagram scraping.
    This error is raised when there are issues related to the scraping process.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"InstagramScraperError: {self.message}"


class InstagramScraper:
    """
    Class responsible for scraping Instagram using Selenium.
    """

    def __init__(self):
        self.options = self._get_chrome_options()

    @staticmethod
    def _get_chrome_options() -> webdriver.ChromeOptions:
        """
        Configure and return chrome options for selenium driver.
        """
        # Set up Chrome options
        options = webdriver.ChromeOptions()

        # Run Chrome in headless mode (without opening a GUI window)
        options.add_argument('--headless')

        # for docker
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Start Chrome maximized. This is useful for ensuring that the browser starts
        # in a consistent state, especially when automating.
        options.add_argument("start-maximized")

        # "enable-automation" is a flag that indicates the browser is being controlled by automated software.
        # "enable-logging" flag controls logging. Disabling both provides a smoother automation experience.
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        # Disabling the use of an automation extension, making our scraping activities less detectable.
        options.add_experimental_option('useAutomationExtension', False)

        # Disables a JavaScript feature called AutomationControlled, making scraping less detectable.
        options.add_argument('--disable-blink-features=AutomationControlled')

        # Choose a random User-Agent from the list. User-Agent defines the browser's type, version,
        # and other attributes. By randomizing it, we are trying to mimic the behavior of different browsers,
        # making it harder for websites to identify our scraper based on a static User-Agent.
        options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')

        return options

    async def extract_photos(self, username: str, max_count: int) -> list | str:
        """
        Extract photo URLs for a given Instagram username up to max_count.
        :param username: username for instagram account
        :param max_count: maximum photo count
        :return photos or error message
        """
        service = ChromeService(executable_path=CHROME_DRIVER_PATH)
        try:
            with webdriver.Chrome(service=service, options=self.options) as driver:
                driver.get(f"https://www.instagram.com/{username}/")
                # Check if the account does not exist
                if "Sorry, this page isn't available." in driver.page_source:
                    raise InstagramScraperError(ErrorMessage.ACCOUNT_NOT_FOUND.format(username))

                photos = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article div div div div a"))
                )
                photo_links = [photo.get_attribute('href') for photo in photos[:max_count]]
        except Exception as e:
            # raise the exception and print for log
            print(f"ERROR: extract_photos: {str(e)}")
            raise InstagramScraperError(ErrorMessage.EXTRACTING_PHOTOS.format(username))

        finally:
            # This ensures resources are released, even if an error occurs
            service.stop()
        return photo_links

    async def get_photos(self, session: AsyncSession, user: UserModel, data: InstagramInput) -> \
            InstagramType | MessageType:
        """
        Extracts photo URLs using the scraper and return as InstagramType.

        :param session: Database session for asynchronous database operations.
        :param user: Requested user model instance.
        :param data: Instagram input containing the username and maximum photo count.

        :return: An InstagramType instance containing the extracted photo URLs or message.
        """
        try:
            photo_links = await self.extract_photos(data.username, data.max_count)
            await InstagramDatabaseService.create_instagram_entry(session, user, photo_links, data.username)
            return InstagramType(urls=photo_links)
        except InstagramScraperError as e:
            return MessageType(message=str(e))
