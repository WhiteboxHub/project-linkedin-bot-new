# LinkedIn Job Application Bot

An automated tool for streamlining the job application process on LinkedIn using Selenium.

## Project Overview

This bot automates the process of searching for jobs on LinkedIn based on user-defined criteria and applying to them using LinkedIn's Easy Apply feature. It helps job seekers save time by automating repetitive application tasks.

## Features

- **Automated Job Search**: Search for jobs based on keywords, location, and other filters
- **Easy Apply Automation**: Automatically fill out application forms
- **Multiple Profile Support**: Configure and use different candidate profiles
- **Application Tracking**: Save application data for future reference
- **Customizable Settings**: Configure search parameters, application preferences, and more

## Project Structure

```
linkedin_bot/
├── main.py                 # Entry point
├── configs/                # User-configurable parameters
│   ├── settings.yaml       # User-configurable parameters (e.g. John Doe.yaml)
│   └── constants.py        # Static constants, selectors, etc.
├── utils/                  # Utility modules
│   ├── __init__.py         # Logging setup
│   ├── logger.py           # Logging setup
│   ├── file_utils.py       # Read/write CSV, YAML, resume paths, etc.
│   ├── browser_manager.py  # Selenium setup, Chrome driver wrapper
│   ├── linkedin_utils.py   # Login, page navigation, element helpers
│   ├── resume_parser.py    # Resume metadata parsing
│   └── candidate_selector.py # Candidate/position filtering logic
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── job_search.py       # Search logic, filtering by role/location
│   ├── easy_apply.py       # EasyApply flow
│   ├── position_role.py    # Job position definitions
│   └── interrupter.py      # Keyboard interrupt graceful close
├── resumes/                # Resume files
│   └── sample_resume.pdf
├── output/                 # Output files
│   ├── applications/       # Application data
│   └── logs/               # Log files
├── tests/                  # Test files
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd linkedin_bot
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure your settings:
   - Copy a sample config file from the `configs` directory
   - Update with your LinkedIn credentials and job preferences

## Usage

1. Run the main script:
```
python main.py
```

2. Select a candidate profile when prompted
3. The bot will:
   - Log in to LinkedIn (if not already logged in)
   - Search for jobs based on your criteria
   - Apply to jobs using Easy Apply
   - Save application data to the output directory

## Configuration

Create a YAML file in the `configs` directory with your information:

```yaml
username: your.email@example.com
password: your_password
phone_number: "1234567890"
profile_path: "path/to/profile"
role_type: "Software Engineer"
positions:
  - "Software Engineer"
  - "Full Stack Developer"
locations:
  - "New York, NY"
  - "Remote"
roletype: "onsite" # onsite/remote/hybrid
salary: "100000"
rate: "hourly" # hourly/yearly
uploads:
  resume: "resumes/your_resume.pdf"
gender: "male" # male/female/other
output_filename: "your_applications.csv"
blacklist:
  - "Company to avoid"
```

## Dependencies

- Python 3.8+
- Selenium
- Chrome WebDriver
- PyYAML
- pandas
- beautifulsoup4
- lxml
- psutil

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Use at your own risk. Automated interactions with websites may violate terms of service.