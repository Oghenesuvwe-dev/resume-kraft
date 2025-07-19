# Resume Kraft

A modern web application that generates professional resumes in DOCX and PDF formats based on user input.

## Features

- **User-friendly Form Interface**: Clean, responsive design with modern styling
- **Multiple Output Formats**: Generate resumes in both DOCX and PDF formats
- **Professional Fields**: Support for various tech roles including Frontend, Backend, Full-Stack, DevOps, and more
- **Experience Levels**: Categorize by Intern, Entry Level, Junior, or Senior experience
- **Customizable Sections**: 
  - Contact Information
  - Professional Summary
  - Skills
  - Work Experience
  - Education
  - Projects (Optional)
  - Certifications (Optional)
  - Languages (Optional)
- **Custom Field Entry**: "Other" option for entering custom job titles

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Document Generation**: python-docx
- **PDF Conversion**: docx2pdf

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Oghenesuvwe-dev/resume-kraft.git
cd resume-kraft
```

2. Create and activate a virtual environment:
```bash
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to:
```
http://127.0.0.1:8000
```

3. Fill out the form and click "Generate Resume" to download your resume in the selected format.

## Requirements

- Python 3.7+
- For PDF conversion: Microsoft Word (Windows) or LibreOffice (Linux/macOS)

## Recent Updates

- Added support for PDF output format
- Implemented field of work selection with various tech roles
- Added "Other" option with manual entry for custom job titles
- Enhanced UI with modern styling and Google Fonts
- Added placeholder text for all form fields
- Improved form organization with clear sections
- Added support for "Unavailable" or "In Review" options for education and certifications

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.