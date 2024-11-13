# external package imports
import argparse
import json
# internal package imports
from src.core.generated_resume import GeneratedResume
from src.core.generated_cover_letter import GeneratedCoverLetter
from src.utils.logger import log
from src.utils.scrape_otta import OttaScraper
from src.utils.scrape_linkedin import LinkedinScraper

# ------------------------------------------------------------------------------
# load params and data
# ------------------------------------------------------------------------------

role_title_overrides =[
    "Senior Data Scientist",
    "Data Scientist",
    "AI/ML Consultant"
]

# ------------------------------------------------------------------------------
# generate resume and cover letter from flat files
#
# by default when given the flat file format, will look for the job description
# file in ./data/input/job_description/
#
# execute the function with the following commands:
# cd <project_dir>
# venv/Scripts/activate.bat # linux
# venv\Scripts\activate.bat # windows
# python main.py --job-description jd.json
# ------------------------------------------------------------------------------

def generate_resume_from_flat(
    job_description_file = "jd.json"
):
    """
    generates a resume and cover letter from a job description flat file that is
        properly formatted in the template provided
    :param job_description_file: formated flat file job description path
    """
    log('generating resume and cover letter from flat files')

    # read in job description json from the job description path
    full_jd_path = "./data/input/job_description/" + job_description_file

    log('job description loaded successfully')

    # open job description file json
    with open(full_jd_path, "r") as json_file:
        job_description = json.load(json_file)

    # create resume object
    generated_resume = GeneratedResume(

        job_description = job_description,
        role_title_overrides=role_title_overrides
    )

    generated_resume.generate_resume()

    generated_cover_letter = GeneratedCoverLetter(
        job_description=job_description,
        personal_info=generated_resume.personal_info,
        resume=generated_resume.professional_experience_output
    )

    generated_cover_letter.generate_cover_letter()

# ------------------------------------------------------------------------------
# generate resume from Otta
#
# execute the function with the following commands:
# cd <project_dir>
# venv/Scripts/activate.bat # linux
# venv\Scripts\activate.bat # windows
# python main.py --otta <otta_url>

# example
# python main.py --otta https://app.welcometothejungle.com/jobs/TI0RfVik
# ------------------------------------------------------------------------------

def generate_resume_via_otta(
    otta_url: str
):
    """
    ingests only the Otta URL and generates a complete tailored resume and cover
        letter
    :param otta_url: full URL of the otta job posting
    :return:
    """
    log('generating resume and cover letter from Otta')

    # create scrape object
    otta_scraper = OttaScraper(otta_url)

    # perform scrape
    otta_scraper.scrape()

    # create resume object
    generated_resume = GeneratedResume(
        job_description=otta_scraper.job_description,
        role_title_overrides=role_title_overrides
    )

    generated_resume.generate_resume()

    generated_cover_letter = GeneratedCoverLetter(
        job_description=otta_scraper.job_description,
        personal_info=generated_resume.personal_info,
        resume=generated_resume.professional_experience_output
    )

    generated_cover_letter.generate_cover_letter()

# ------------------------------------------------------------------------------
# generate resume from linkedin
#
# warning: linked in is highly resistant to scraping; repeated use of this
# function over short periods of time will likely result in LinkedIn blocking
# usage of the scaper
#
# execute the function with the following commands:
# cd <project_dir>
# venv/Scripts/activate.bat # linux
# venv\Scripts\activate.bat # windows
# python main.py --linkedin <linkedin_url>
#
# example
# python main.py --linkedin 'https://www.linkedin.com/jobs/view/pmo-project-manager-senior-at-lumen-solutions-group-inc-4020127114?position=49&pageNum=0&refId=unnAc2CazojYu2txaJX9lg%3D%3D&trackingId=IVtY7gFQHebr5VxMk0104Q%3D%3D'
# ------------------------------------------------------------------------------

def generate_resume_via_linkedin(
    linkedin_url: str
):
    """
    ingests only the LinkedIn URL and generates a complete tailored resume and
        cover letter
    param linkedin_url: full URL of the LinkedIn job posting
    return:
    """
    log('generating resume and cover letter from LinkedIn')

    # create scrape object
    linkedin_scraper = LinkedinScraper(linkedin_url)

    # perform scrape
    linkedin_scraper.scrape()

    # create resume object
    generated_resume = GeneratedResume(
        job_description=linkedin_scraper.job_description,
        role_title_overrides=role_title_overrides
    )

    generated_resume.generate_resume()

    generated_cover_letter = GeneratedCoverLetter(
        job_description=linkedin_scraper.job_description,
        personal_info=generated_resume.personal_info,
        resume=generated_resume.professional_experience_output
    )

    generated_cover_letter.generate_cover_letter()

# ------------------------------------------------------------------------------
# other functions
# ------------------------------------------------------------------------------

def generate_resume_content_only(
    job_description_file = "jd.json"
):
    """
    generates a resume and cover letter from a job description flat file that is
        properly formatted in the template provided
    :param job_description_file: formated flat file job description path
    """
    log('generating resume and cover letter from flat files')

    # read in job description json from the job description path
    full_jd_path = "./data/input/job_description/" + job_description_file

    log('job description loaded successfully')

    # open job description file json
    with open(full_jd_path, "r") as json_file:
        job_description = json.load(json_file)

    # create resume object
    generated_resume = GeneratedResume(
        env_vars=env_vars,
        model_config=model_config,
        doc_format=doc_format,
        job_description = job_description,
        resume_input=resume_input,
        role_title_overrides=role_title_overrides
    )

    generated_resume.generate_resume_content()

    return generated_resume

# ------------------------------------------------------------------------------
# main function
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Generate a resume and cover letter from a job description')

    # Create a mutually exclusive group - only one argument can be used at a time
    group = parser.add_mutually_exclusive_group(required=True)

    # Add arguments for each function
    group.add_argument('--job-description', '-j',
                       help='Path to the job description file')
    group.add_argument('--otta', '-o',
                       help='Otta job posting URL')
    group.add_argument('--linkedin', '-l',
                       help='LinkedIn job posting URL')

    args = parser.parse_args()

    # Call appropriate function based on which argument was provided
    if args.job_description:
        generate_resume_from_flat(args.job_description)
    elif args.otta:
        generate_resume_via_otta(args.otta)
    elif args.linkedin:
        generate_resume_via_linkedin(args.linkedin)


if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------
# end of main.py
# ------------------------------------------------------------------------------
