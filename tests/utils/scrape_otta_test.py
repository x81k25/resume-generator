import pytest
from unittest.mock import Mock, patch
import json
import tempfile
import os
from bs4 import BeautifulSoup
from src.utils.scrape_otta import OttaScraper


def load_sample_html():
	"""Load sample HTML file from the same directory"""
	current_dir = os.path.dirname(os.path.abspath(__file__))
	html_path = os.path.join(current_dir, 'otta_sample.html')

	try:
		with open(html_path, 'r', encoding='utf-8') as file:
			return file.read()
	except FileNotFoundError:
		raise FileNotFoundError(f"Sample HTML file not found at {html_path}")


# Load sample HTML once for all tests
SAMPLE_HTML = load_sample_html()


@pytest.fixture
def mock_response():
	"""Create a mock response object"""
	mock_resp = Mock()
	mock_resp.text = SAMPLE_HTML
	mock_resp.raise_for_status = Mock()
	return mock_resp


@pytest.fixture
def scraper():
	"""Create a scraper instance"""
	return OttaScraper("https://test-url.com")


def test_initialization(scraper):
	"""Test scraper initialization"""
	assert scraper.url == "https://test-url.com"
	assert scraper.html_content is None
	assert scraper.soup is None
	assert scraper.job_description == {
		'company_name': None,
		'role_title': None,
		'name_param': None,
		'role_description': None,
		'key_skills': [],
		'company_sectors': []
	}


@patch('requests.get')
def test_fetch_webpage(mock_get, scraper, mock_response):
	"""Test fetching webpage content"""
	mock_get.return_value = mock_response

	scraper._fetch_webpage()

	assert scraper.html_content == SAMPLE_HTML
	assert isinstance(scraper.soup, BeautifulSoup)
	mock_get.assert_called_once_with("https://test-url.com")


@patch('requests.get')
def test_fetch_webpage_error(mock_get, scraper):
	"""Test error handling in fetch webpage"""
	mock_get.side_effect = Exception("Connection error")

	with pytest.raises(Exception) as exc_info:
		scraper._fetch_webpage()
	assert "Error fetching webpage content" in str(exc_info.value)


def test_extract_role_title_and_company_name(scraper):
	"""Test extracting role title and company name"""
	scraper.soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

	scraper._extract_role_title_and_company_name()

	assert scraper.job_description['company_name'] == "Quora"
	assert scraper.job_description['role_title'] == "Data Scientist"
	assert scraper.job_description['name_param'] == "data-scientist-quora"


def test_extract_role_description(scraper):
	"""Test extracting role description"""
	scraper.soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

	scraper._extract_role_description()

	assert "Who you are" in scraper.job_description['role_description']
	assert "What the job involves" in scraper.job_description[
		'role_description']
	assert "statistical techniques" in scraper.job_description[
		'role_description']


def test_extract_key_skills(scraper):
	"""Test extracting key skills"""
	scraper.soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

	scraper._extract_key_skills()

	expected_skills = ["Python", "R", "Redshift"]
	assert all(skill in scraper.job_description['key_skills'] for skill in
			   expected_skills)


def test_extract_company_sectors(scraper):
	"""Test extracting company sectors"""
	scraper.soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

	scraper._extract_company_sectors()

	expected_sectors = ["B2C", "Education", "Internet of Things", "Learning",
						"Social",
						"Machine Learning", "Product Management",
						"Data Integration"]
	assert all(
		sector in scraper.job_description['company_sectors'] for sector in
		expected_sectors)


@patch('requests.get')
def test_full_scrape_pipeline(mock_get, scraper, mock_response):
	"""Test the full scraping pipeline"""
	mock_get.return_value = mock_response

	scraper.scrape()

	assert scraper.job_description['company_name'] == "Quora"
	assert scraper.job_description['role_title'] == "Data Scientist"
	assert len(scraper.job_description['key_skills']) > 0
	assert len(scraper.job_description['company_sectors']) > 0


def test_write_jd(scraper):
	"""Test writing job description to file"""
	scraper.job_description.update({
		'company_name': "Quora",
		'role_title': "Data Scientist",
		'name_param': "data-scientist-quora",
		'role_description': "Test description",
		'key_skills': ["Python", "R", "Redshift"],
		'company_sectors': ["B2C", "Education"]
	})

	with tempfile.TemporaryDirectory() as tmpdir:
		scraper.write_jd(path=tmpdir + "/")

		expected_file = os.path.join(tmpdir, "data-scientist-quora.json")
		assert os.path.exists(expected_file)

		with open(expected_file, 'r') as f:
			saved_data = json.load(f)
			assert saved_data == scraper.job_description


if __name__ == '__main__':
	pytest.main([__file__])