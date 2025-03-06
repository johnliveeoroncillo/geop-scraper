# GeoOp Scraper: Detailed Project Description

## Project Overview

GeoOp Scraper is a specialized web scraping tool designed to extract job-related data, notes, and images from the GeoOp platform (a field service management system). The scraper automates the process of logging in, navigating through job records, and downloading associated images and information, organizing them into a structured directory system.

## Core Functionality

1. **Authentication**: 
   - Securely logs into the GeoOp platform using stored credentials
   - Implements cookie management to bypass 2FA after initial login
   - Saves authentication cookies for future sessions

2. **Job Data Extraction**:
   - Processes a predefined list of job URLs from the configuration file
   - Extracts key job information (client name, service name, job ID, date)
   - Navigates through job details pages

3. **Image & Document Downloading**:
   - Identifies and downloads images from the "Notes & Documents" tab for each job
   - Organizes downloaded content into a hierarchical folder structure
   - Handles proper file naming and path sanitization for compatibility

4. **Error Handling & Logging**:
   - Tracks failed URL scraping attempts in a CSV file for retry
   - Implements exception handling for various failure scenarios
   - Includes detailed logging of the scraping process

## Project Structure

```
geop-scraper/
├── scraper.py                  # Main script with entry point and job processing logic
├── config_geoop.py             # Configuration for GeoOp credentials and job URLs
├── config_zoho.py              # Configuration for Zoho integration (secondary platform)
├── requirements.txt            # Python dependencies
├── cookies.json                # Stored authentication cookies
├── cookies.txt                 # Alternative cookie storage format
├── failed_urls.csv             # Tracking file for URLs that failed to process
├── pages/                      # Page object models for web interaction
│   ├── __init__.py
│   ├── geoop_login_page.py     # Login page interactions
│   ├── job_list_page.py        # Job listing page interactions
│   ├── job_page.py             # Individual job page interactions
│   ├── notes_documents_page.py # Notes & Documents tab interactions
│   ├── zoho_crm.py             # Zoho CRM integration (not primary focus)
│   └── zoho_login_page.py      # Zoho login handling (not primary focus)
├── utils/                      # Utility functions and helpers
│   ├── __init__.py
│   ├── file_manager.py         # File system operations helper
│   └── image_wait.py           # Angular-specific wait functions for images
├── logs/                       # Directory for log files
└── output/                     # [Generated] Output directory for downloaded data
    └── {client_name}/          # Client-specific folders
        └── #{job_id}_{service}_{date}/ # Job-specific folders
            └── {date_text}/    # Date-specific folders with images
```

## Technical Specifications

### Dependencies

The project relies on the following Python packages:
- `selenium`: Web browser automation
- `beautifulsoup4`: HTML parsing (supplementary to Selenium)
- `requests`: HTTP requests for downloading images
- `tqdm`: Progress bar functionality

### Architecture

The project follows a Page Object Model (POM) design pattern for web scraping:
- **Page Objects**: Encapsulate the structure and interactions with specific web pages
- **Main Script**: Orchestrates the overall scraping process
- **Utilities**: Provide helper functions for common operations
- **Configuration Files**: Store environment-specific settings and credentials

### Data Flow

1. The scraper initializes a Chrome WebDriver instance
2. It loads stored cookies or performs a fresh login to GeoOp
3. For each job URL in the configuration:
   - The scraper navigates to the job page
   - Extracts job metadata (client, service, ID, date)
   - Navigates to the Notes & Documents tab
   - Downloads all available images
   - Organizes them into the appropriate folder structure
4. Failed URLs are logged for later retry

## Setup & Usage

### Prerequisites

- Python 3.6+
- Chrome browser
- ChromeDriver matching your Chrome version

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### Configuration

1. Update `config_geoop.py` with your GeoOp credentials
2. Modify the `JOB_URLS_LIST` in `config_geoop.py` to include the job URLs you want to scrape

### Running the Scraper

Execute the main script:
```
python scraper.py
```

The script will:
1. Log in to GeoOp (using stored cookies if available)
2. Process each job URL
3. Download images and organize them in the output directory
4. Log any failed URLs for later retry

## Common Issues & Troubleshooting

- **Authentication Failures**: If login fails, delete `cookies.json` and try again with a fresh login
- **Element Not Found Errors**: The GeoOp interface may have changed; update the XPath selectors in the page objects
- **Image Download Issues**: Check network connectivity and ensure the URLs are accessible
- **Failed URL Processing**: Review `failed_urls.csv` and investigate specific URLs that failed

## Security Considerations

- Credentials are stored in plain text in `config_geoop.py` - consider implementing a more secure credential management approach
- Authentication cookies are stored locally in `cookies.json` - ensure this file is properly secured

## Future Enhancements

- Implement parallel processing for faster scraping
- Add a user interface for easier configuration and monitoring
- Improve error handling and recovery mechanisms
- Integrate with cloud storage for direct uploading of extracted data

## Maintenance Notes

- Regularly check for changes in the GeoOp interface that might break the scraper
- Update selectors and interaction patterns as needed
- Monitor for rate limiting or blocking mechanisms implemented by GeoOp
