# AI Resume and Cover Letter Generator

This project uses Anthropic's chat completion models to generate tailored resumes and cover letters based on job descriptions. It takes a comprehensive list of your skills and experiences from a JSON file and customizes them to match specific job requirements.

## Features

- Generates tailored resumes and cover letters from three different input sources:
  - Local JSON job description file
  - Welcome to the Jungle (formerly Otta.com) job postings
  - LinkedIn job postings
- Provides feedback on areas for professional improvement
- Configurable document formatting
- Flexible model parameters for different generation strategies

## Prerequisites

- Python 3.x
- Anthropic API key
- Virtual environment tool (e.g., venv, conda)

## Setup

1. Clone the repository
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Copy sample.env to .env
cp sample.env .env
# Edit .env and add your Anthropic API key
Anthropic_API_KEY=your-api-key-here
```

## Project Structure

```
├── config/                  # Configuration files
│   ├── doc_format.yaml     # Document formatting settings
│   └── model_v1.24.yaml    # Model parameters
├── data/
│   ├── assets/             # Images for document headers
│   ├── input/
│   │   ├── cover_letter_content/     # Optional custom cover letter content
│   │   ├── job_description/          # Job description JSON files
│   │   └── resume/                   # Resume input files
│   └── output/             # Generated documents
├── notebooks/              # Jupyter notebooks for development
├── src/
│   ├── core/              # Main application logic
│   └── utils/             # Helper functions and utilities
└── tests/                 # Test files
```

## Usage

1. Prepare your resume input file:
   - Copy `data/input/resume/resume_input_sample.json` to `data/input/resume/resume_input.json`
   - Modify the JSON file with your complete professional history

2. Generate resume and cover letter using one of three methods:

```bash
# Using a local JSON job description
python main.py --job-description jd.json

# Using Welcome to the Jungle (formerly Otta)
python main.py --otta https://app.welcometothejungle.com/jobs/example-job-id

# Using LinkedIn
python main.py --linkedin https://www.linkedin.com/jobs/view/example-job-id
```

### Job Description File Format

If using a local JSON file, ensure it follows this structure:
```json
{
    "company_name": "Company Name",
    "role_title": "Job Title",
    "name_param": "job-title-company-name",
    "role_description": "Full job description...",
    "key_skills": ["skill1", "skill2"],
    "company_sectors": ["sector1", "sector2"]
}
```

## Configuration

### Document Formatting

Modify `config/doc_format.yaml` to customize the appearance of generated documents:
- Font styles and sizes
- Line spacing
- Header images
- Color schemes

### Model Parameters

Current model parameters are in `config/model_v1.24.yaml`. Key settings include:
- Temperature for resume/cover letter generation
- Number of responsibilities per experience
- Output formatting requirements

To use older model versions, modify the config file path in `main.py`.

## Output

Generated files are saved in `data/output/`:
- Resume as DOCX file
- Cover letter as DOCX file
- `areas-of-improvement.md` containing suggestions for skill development

## Notes

- The LinkedIn scraper may be rate-limited with frequent use
- Welcome to the Jungle (formerly Otta) class names remain unchanged despite the platform's rebranding
- Custom cover letter content can be added in `data/input/cover_letter_content/[company_name].txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

Copyright (c) 2024 x81k25

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.