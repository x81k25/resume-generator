from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
import requests
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from time import sleep
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional
from src.utils.logger import log

# ------------------------------------------------------------------------------
# class object definition
# ------------------------------------------------------------------------------

class LinkedinScraper:
    """
    Class to scrape job description from LinkedIn
    :param url: URL of the job description
    """
    def __init__(self, url):
        log("initializing LinkedinScraper...")
        # input attributes
        self.full_url = url
        # attributes created during initialization
        self.url = self.clean_linkedin_job_url(self.full_url)
        self.session = self._create_session()
        self.user_agent = UserAgent()
        # attributes generated from scraping
        self.html_content = None
        self.soup = None
        self.job_description: Dict[str, Optional[str | List[str]]] = {
            'company_name': None,
            'role_title': None,
            'name_param': None,
            'role_description': None,
            'key_skills': [],
            'company_sectors': []
        }
        log("...LinkedinScraper initialized")

# ------------------------------------------------------------------------------
# static helper methods
# ------------------------------------------------------------------------------

    @staticmethod
    def clean_linkedin_job_url(full_url):
        """
        Clean a LinkedIn job URL by removing tracking parameters.
        Returns a minimal URL that only contains the job ID.
        """
        # Parse the URL
        parsed = urlparse(full_url)

        # Extract the job ID from the path
        job_id = parsed.path.split('/')[-1].replace('/', '')

        # If the job ID contains a question mark, remove everything after it
        if '?' in job_id:
            job_id = job_id.split('?')[0]

        # Construct the clean URL
        clean_url = f"https://www.linkedin.com/jobs/view/{job_id}"

        return clean_url


    @staticmethod
    def _create_session():
        """Create a session with retry strategy"""
        session = requests.Session()

        # Configure retry strategy
        retries = Retry(
            total=5,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

# ------------------------------------------------------------------------------
# helper methods
# ------------------------------------------------------------------------------

    def _get_headers(self):
        """Generate headers that look like a real browser"""
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def _fetch_webpage(self, url=None, max_retries=3):
        """
        Scrape a LinkedIn job posting with proper rate limiting and error handling.
        Updates self.html_content and self.soup attributes on success.

        Args:
            url (str, optional): LinkedIn job URL. If not provided, uses self.url
            max_retries (int): Maximum number of retry attempts

        Raises:
            ValueError: If no URL is provided or set
            Exception: If scraping fails after max retries
        """
        log("attempting to fetch webpage...")

        # Update url if provided, otherwise use instance url
        if url:
            self.url = url

        if not self.url:
            raise ValueError(
                "No URL provided. Set url in constructor or provide it to scrape()")

        retry_count = 0

        while retry_count < max_retries:
            try:
                # Add a random delay between requests (2-5 seconds)
                sleep(random.uniform(2, 5))

                # Make the request with proper headers
                response = self.session.get(
                    self.url,
                    headers=self._get_headers(),
                    timeout=10
                )

                # Check for rate limiting
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 60))
                    log(f"rate limited. Waiting {wait_time} seconds...")
                    sleep(wait_time)
                    retry_count += 1
                    continue

                response.raise_for_status()
                self.html_content = response.text
                self.soup = BeautifulSoup(self.html_content, 'html.parser')
                log("...fetch successful")
                return  # Exit method after successful fetch

            except requests.exceptions.RequestException as e:
                log(f"error occurred: {str(e)}")
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(
                        f"LinkedinScraper: Failed to scrape job after {max_retries} attempts")
                sleep(random.uniform(5, 10))  # Wait longer between retries

        # Only raise this if we somehow exit the while loop without returning or raising another exception
        raise Exception(
            "failed to scrape job after exhausting all retries")

    def _extract_company_name(self):
        """
        Extracts company name from the LinkedIn job posting HTML content.
        Updates self.job_description['company_name'] with the result.
        Raises:
            Exception: If company name cannot be found in the HTML content
        """
        try:
            log("extracting company name...")
            # Check if we have HTML content
            if not self.soup:
                raise Exception(
                    "No HTML content available. Run _fetch_webpage() first."
                )

            # First try to find the company name in the topcard section
            company_element = self.soup.find('a', {
                'class': 'topcard__org-name-link'})

            # If not found in topcard, try the sub-nav section
            if not company_element:
                company_element = self.soup.find('a', {
                    'class': 'sub-nav-cta__optional-url'})

            # Extract the text and clean it
            if company_element:
                company_name = company_element.get_text().strip()
                self.job_description['company_name'] = company_name
                log(f"...successfully extracted company name: {company_name}")
            else:
                raise Exception("Could not find company name in HTML content")

        except Exception as e:
            raise Exception(f"error extracting company name: {str(e)}")


    def _extract_role_title(self):
        """
        Extracts role title from the LinkedIn job posting HTML content.
        Updates self.job_description['role_title'] with the result.

        Raises:
            Exception: If role title cannot be found in the HTML content
        """
        try:
            log("extracting role title...")
            # Check if we have HTML content
            if not self.soup:
                raise Exception(
                    "No HTML content available. Run _fetch_webpage() first.")

            # Try to find the role title in the top-card-layout section
            title_element = self.soup.find('h1',
                                           {'class': 'top-card-layout__title'})

            # If not found, try the alternative class name
            if not title_element:
                title_element = self.soup.find('h1',
                                               {'class': 'topcard__title'})

            # Extract and clean the text
            if title_element:
                role_title = title_element.get_text().strip()
                self.job_description['role_title'] = role_title
                log("successfully extracted role title: {role_title}")
            else:
                raise Exception("could not find role title in HTML content")

        except Exception as e:
            raise Exception(f"error extracting role title: {str(e)}")

    def _generate_name_param(self):
        """
        Generate a name parameter for the job description.
        The name parameter is a lowercase string with spaces replaced by hyphens.
        """
        log("generating name parameter...")
        if self.job_description['role_title'] and self.job_description['company_name']:
            name_param = str(
                self.job_description['role_title'].replace(' ', '-').replace(',', '').lower() +
                '-' +
                self.job_description['company_name'].replace(' ', '-').replace(',', '').lower()
            )
            self.job_description['name_param'] = name_param
            log(f"successfully generated name parameter: {name_param}")
        else:
            raise Exception("cannot generate name parameter; missing role title or company name")


    def _extract_role_description(self):
        """
        Extracts role description from the LinkedIn job posting HTML content.
        Updates self.job_description['role_description'] with the result.
        Excludes company summary section.

        Raises:
            Exception: If role description cannot be found in the HTML content
        """
        try:
            # Check if we have HTML content
            if not self.soup:
                raise Exception(
                    "no HTML content available; run _fetch_webpage() first."
                )

            # Find the description section
            description_element = self.soup.find('div', {'class': 'description__text'})

            if not description_element:
                raise Exception(
                    "could not find description section in HTML content")

            # Get the text content
            description_text = description_element.get_text(separator='\n',
                                                            strip=True)

            # Split the text by sections to remove company summary
            sections = description_text.split('**UP.Labs Summary:**')
            if len(sections) > 1:
                # Take only the role description part (before company summary)
                role_description = sections[0].strip()
            else:
                # If no company summary found, take the whole description
                role_description = description_text.strip()

            # Clean up the text
            # Remove any extra whitespace between sections while preserving formatting
            role_description = re.sub(r'\n\s*\n\s*\n+', '\n\n',
                                      role_description)

            self.job_description['role_description'] = role_description
            log("successfully extracted role description")

        except Exception as e:
            raise Exception(
                f"LinkedinScraper._extract_role_description: Error extracting role description: {str(e)}"
            )

# ------------------------------------------------------------------------------
# primary method to be called externally
# ------------------------------------------------------------------------------

    def scrape(self):
        """
        Full pipeline function to scrape the job description
        :return: Dictionary with job description details
        """
        log("initializing full scrape of linkedin url...")
        self._fetch_webpage()
        self._extract_company_name()
        self._extract_role_title()
        self._generate_name_param()
        self._extract_role_description()
        log("...scrape complete")


    def write_jd(
        self,
        path = "./data/input/job_description/"
    ):
        """
        Write job description to file
        :param path: path to write the job description to json
        """
        # write self.job_description to file as json
        json_path = path + self.job_description['name_param'] + ".json"

        with open(json_path, 'w') as json_file:  # type: Any
            json.dump(self.job_description, json_file, indent=4)

# ------------------------------------------------------------------------------
# end of scrape_linkedin.py
# ------------------------------------------------------------------------------
