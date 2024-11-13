from bs4 import BeautifulSoup
import json
import re
import requests
from typing import Any, Dict, List, Optional
from src.utils.logger import log

# ------------------------------------------------------------------------------
# class object definition
# ------------------------------------------------------------------------------

class OttaScraper:
    """
    Class to scrape job description from Otta
    :param url: URL of the job description
    """
    def __init__(self, url):
        log('initializing OttaScraper')
        self.url = url
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
        log('OttaScraper initialized')

# ------------------------------------------------------------------------------
# helper methods
# ------------------------------------------------------------------------------

    def _fetch_webpage(self):
        """
        Fetch the webpage content
        :return: HTML content of the webpage
        """
        try:
            log('attempting to fetch webpage content...')
            response = requests.get(self.url)
            response.raise_for_status()  # Check if the request was successful
            self.html_content = response.text
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
            log('...webpage content fetched successfully')
        except Exception as e:
            raise Exception(f'Error fetching webpage content: {e}')

    def _extract_role_title_and_company_name(self):
        """
        Extract job title and company name from the HTML content using BeautifulSoup.
        """
        try:
            # Find the element containing the job title and company
            title_section = self.soup.find('div', {'class': 'bkeQyr'})
            if title_section:
                # Get the h1 element for the full title
                h1_element = title_section.find('h1', {'class': 'kSSTOp'})
                if h1_element:
                    # Find the company name link
                    company_link = h1_element.find('a', {'class': 'kQkLtz'})
                    if company_link:
                        self.job_description['company_name'] = company_link.text.strip()
                        # Get the full text and remove the company name to get the job title
                        full_text = h1_element.text.strip()
                        self.job_description['role_title'] = full_text.replace(self.job_description['company_name'], '').replace(',','').strip()
                        self.job_description['name_param'] = str(
                            self.job_description['company_name'].replace(' ',
                                                                         '-').replace(
                                ',', '').lower() +
                            '-' +
                            self.job_description['role_title'].replace(' ',
                                                                       '-').replace(
                                ',', '').lower()
                        )
                        log('role title and company name extracted successfully')
        except Exception as e:
            raise Exception(f'Error extracting role title and company name: {e}')

    def _extract_role_description(self):
        """
        Extract text from specified sections
        :return: Dictionary with section titles and their content
        """
        try:
            section = self.soup.find('h2', string="Role")
            section_content = section.find_next('div')
            role_description = section_content.get_text(strip=True)

            # format role description
            role_description = role_description.replace("Who you are", "\nWho you are\n")
            role_description = role_description.replace("What the job involves", "\n\nWhat the job involves\n")
            pattern = re.compile(r'([a-z])([A-Z])')
            role_description = pattern.sub(r'\1\n\2', role_description)

            self.job_description['role_description'] = role_description
            log('role description extracted successfully')
        except Exception as e:
            raise Exception(f'Error extracting role description: {e}')


    def _extract_key_skills(self):
        """
        Extract key technical skills from the HTML content using BeautifulSoup.
        """
        try:
            # First find the section containing technologies
            skills_container = self.soup.find('div', {'class': 'ddpLEU'})

            if not skills_container:
                # Try alternative class if first attempt fails
                skills_container = self.soup.find('div', {'class': 'sc-312c7ec1-0'})

            if skills_container:
                # Find all skill divs
                skill_elements = skills_container.find_all('div',
                                                           {'class': ['isAlRM']})

                # Extract and clean the text
                skills = []
                for element in skill_elements:
                    skill = element.text.strip()
                    if skill:  # Only add non-empty strings
                        skills.append(skill)

                self.job_description['key_skills'] = skills
                log('key skills extracted successfully')

        except Exception as e:
            raise Exception(f'Error extracting key skills: {e}')


    def _extract_company_sectors(self):
        """
        Extract company sector tags from the HTML content using BeautifulSoup.
        """
        try:
            # Find the container div with class that contains the sectors
            sector_container = self.soup.find('div', {'class': 'sc-791f8a83-1'})

            if sector_container:
                # Find all sector tags within the container
                sector_elements = sector_container.find_all('span',                                                    {
                                                                'class': 'sc-791f8a83-2'})

                # Extract text from each tag and store in a list
                company_sectors = [tag.text.strip() for tag in sector_elements]

                self.job_description['company_sectors'] = company_sectors
                log('company sectors extracted successfully')
        except Exception as e:
            raise Exception(f'Error extracting company sectors: {e}')

# ------------------------------------------------------------------------------
# primary method to be called externally
# ------------------------------------------------------------------------------

    def scrape(self):
        """
        Full pipeline function to scrape the job description
        :return: Dictionary with job description details
        """
        log('initializing full scrape of otta job description...')
        self._fetch_webpage()
        self._extract_role_title_and_company_name()
        self._extract_role_description()
        self._extract_key_skills()
        self._extract_company_sectors()
        log('...full scrape of otta job description complete')


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
# end of scrape_otta.py
# ------------------------------------------------------------------------------
