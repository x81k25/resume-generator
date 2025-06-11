# standard library imports
import argparse
import json
import os
from pathlib import Path
import sys

# third party imports
from dotenv import load_dotenv
from loguru import logger

# custom/internal imports
from src.core.generated_resume import GeneratedResume
from src.core.generated_cover_letter import GeneratedCoverLetter
import src.utils as utils

# ------------------------------------------------------------------------------
# load params and data
# ------------------------------------------------------------------------------

# remove default handler
logger.remove()

# Add your handlers with custom format
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True
)

# get env vars
load_dotenv(override=True)

# resume generation vars
role_title_overrides =[
    "Senior Data Scientist",
    "Data Scientist",
    "AI/ML Consultant"
]

# ------------------------------------------------------------------------------
#
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
#
# generate resume from Otta
#
# execute the function with the following commands:
# cd <project_dir>
# venv/Scripts/activate.bat # linux
# venv\Scripts\activate.bat # windows
# python main.py --otta <otta_url>
#
# example
# python main.py --otta https://app.welcometothejungle.com/jobs/TI0RfVik
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
# python main.py --LinkedIn <linkedin_url>
#
# example
# python main.py --LinkedIn 'https://www.linkedin.com/jobs/view/pmo-project-manager-senior-at-lumen-solutions-group-inc-4020127114?position=49&pageNum=0&refId=unnAc2CazojYu2txaJX9lg%3D%3D&trackingId=IVtY7gFQHebr5VxMk0104Q%3D%3D'
#
# ------------------------------------------------------------------------------

def generate_artifacts(
    job_description_type: str = "flat_file",
    job_description_source: str = "jd.json",
    generate_cover_letter: bool = False
):
    """
    generates a resume and cover letter from a job description flat file that is
        properly formatted in the template provided

    :param job_description_type: either flat_file, otta, or linked
    :param job_description_source: either file location or jd url
    :param generate_cover_letter: whether to generate a cover letter
    """
    if job_description_type == "flat_file":
        logger.info('generating resume flat file')

        # read in job description json from the job description path
        full_jd_path = "./data/input/job_description/" + job_description_source

        logger.info('job description loaded successfully')

        # open job description file json
        with open(full_jd_path, "r", encoding='utf-8') as json_file:
            job_description = json.load(json_file)
    elif job_description_type == "otta":
        logger.info('generating resume from Otta')

        # create scrape object
        otta_scraper = utils.OttaScraper(job_description_source)

        # perform scrape
        otta_scraper.scrape()
        job_description = otta_scraper.job_description

    elif job_description_type == "linkedin":
        logger.info('generating resume from LinkedIn')

        # create scrape object
        linkedin_scraper = utils.LinkedinScraper(job_description_source)

        # perform scrape
        linkedin_scraper.scrape()
        job_description = linkedin_scraper.job_description

    # create resume object
    generated_resume = GeneratedResume(
        job_description=job_description,
        role_title_overrides=role_title_overrides
    )

    # create file level logger
    log_parent_path = os.getenv("LOG_OUTPUT_PATH")
    log_file_path = generated_resume.job_description['name_param'] + ".log"
    log_full_path = Path(log_parent_path) / log_file_path
    logger.add(
        log_full_path,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"
    )
    # remove contents if file already exists
    if os.path.exists(log_full_path):
        open(log_full_path, 'w').close()

    # generate and write content
    generated_resume.generate_resume()

    # generate cover letter if needed
    if generate_cover_letter:
        logger.info('generating cover letter from flat file')

        generated_cover_letter = GeneratedCoverLetter(
            job_description=job_description,
            personal_info=generated_resume.personal_info,
            resume=generated_resume.professional_experience_output
        )

        generated_cover_letter.generate_cover_letter()


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

    # arg to determine whether cover letter should be generated
    parser.add_argument('--cover-letter', '-cl', action='store_true',
                       help='Generate cover letter in addition to resume')

    args = parser.parse_args()

    # Call appropriate function based on which argument was provided
    if args.job_description:
        generate_artifacts(
            job_description_type="flat_file",
            job_description_source=args.job_description,
            generate_cover_letter=args.cover_letter
        )
    elif args.otta:
        generate_artifacts(
            job_description_type="otta",
            job_description_source=args.otta,
            generate_cover_letter=args.cover_letter
        )
    elif args.linkedin:
        generate_artifacts(
            job_description_type="linkedin",
            job_description_source=args.linkedin,
            generate_cover_letter=args.cover_letter
        )


if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------
# end of main.py
# ------------------------------------------------------------------------------