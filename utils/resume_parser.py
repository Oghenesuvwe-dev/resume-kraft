import os
import re
import docx
import io

# Add PDF parsing capability
try:
    from pdfminer.high_level import extract_text as extract_text_from_pdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PDF parsing not available. Install pdfminer.six for PDF support.")


def parse_resume(file_path):
    """
    Resume parser that extracts text from DOCX and PDF files
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        dict: Extracted information from the resume
    """
    try:
        # Extract text based on file type
        if file_path.lower().endswith('.docx'):
            text = extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.pdf') and PDF_SUPPORT:
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.pdf'):
            # PDF support not available
            return {"error": "PDF parsing requires pdfminer.six library. Please install it or use DOCX format."}
        else:
            # Unsupported format
            return {"error": "Unsupported file format. Please use DOCX or PDF."}
        
        # Check if text extraction was successful
        if not text or len(text.strip()) < 10:
            return {"error": "Could not extract text from the file. Please check the file format or content."}
        
        # Extract basic information using regex patterns
        email = extract_email(text)
        phone = extract_phone(text)
        
        # Extract skills first as they help determine field of work
        skills = extract_skills(text)
        
        # Try to guess field of work using both text and skills
        field_of_work = extract_field_of_work(text, skills)
        
        # Extract experience information
        experience_level, years_of_experience = extract_experience_info(text)
        
        # Extract work experience
        experience = extract_experience(text)
        
        # Create a simple data structure
        # Extract social media and website links
        linkedin = extract_linkedin(text)
        website = extract_website(text)
        blog = extract_blog(text)
        youtube = extract_youtube(text)
        
        data = {
            "full_name": extract_name(text),
            "email": email,
            "phone": phone,
            "location": extract_location(text),
            "linkedin": linkedin,
            "summary": extract_summary(text),
            "skills": skills,
            "experience": experience,
            "education": extract_education(text),
            "projects": extract_projects(text),
            "website": website,
            "blog": blog,
            "youtube": youtube,
            "certifications": extract_certifications(text),
            "languages": extract_languages(text),
            "field_of_work": field_of_work,
            "experience_level": experience_level,
            "years_of_experience": years_of_experience
        }
        
        return data
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {}

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file"""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_email(text):
    """Extract email using regex"""
    email_pattern = r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""

def extract_phone(text):
    """Extract phone number using regex"""
    phone_pattern = r'(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else ""

def extract_summary(text):
    """Extract a potential summary (first paragraph with substantial text)"""
    paragraphs = text.split('\n')
    for para in paragraphs:
        if len(para) > 50:  # Assume a summary is at least 50 chars
            return para
    return ""

def extract_name(text):
    """Extract a potential name from the resume"""
    # Look for patterns like "Name: John Doe" or just a name at the beginning
    name_patterns = [
        r'(?:name|Name)[,:]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)[\.,]?',  # Name, John Doe. or Name: John Doe
        r'(?:name:|^)\s*([A-Z][a-z]+(\s[A-Z][a-z]+)+)',  # Standard name format
        r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$',  # Name at beginning of line
        r'^([A-Z][A-Z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$',  # ALL CAPS first name
        r'(?:name:|resume of:|cv of:|curriculum vitae:|profile:)\s*([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # After keywords
        r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)'  # Name with middle initial
    ]
    
    # Try each pattern
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    
    # If no match found, try to find the first line that looks like a name
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        # Look for "Name, John Doe" format
        name_match = re.match(r'Name[,:]\s*(.+?)[\.,]?$', line, re.IGNORECASE)
        if name_match:
            return name_match.group(1).strip()
        
        # Look for lines that look like names
        if len(line) > 0 and len(line.split()) <= 4 and all(word[0].isupper() for word in line.split() if word):
            return line
            
    return ""

def extract_location(text):
    """Extract location information"""
    # Look for common location patterns
    location_patterns = [
        r'(?:location|address|city|state):\s*([^\n,]+(?:,\s*[^\n]+){0,2})',  # After keywords
        r'([A-Z][a-z]+(?:,\s*[A-Z]{2})(?:,\s*\d{5})?)',  # City, State ZIP
        r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+))',  # City, Country
        r'([A-Z][a-z]+(?:,\s*[A-Z]{2}))',  # City, State
        r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Region
        r'(?:located in|based in|living in)\s+([A-Z][a-z]+(?:[,\s]+[A-Z][a-z]+)*)',  # After phrases
        r'(?:^|\n)([A-Z][a-z]+(?:[,\s]+[A-Z][a-z]+){1,2})(?:$|\n)'  # Location on its own line
    ]
    
    # Try each pattern
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Verify it's not part of a name
            if not re.search(r'(?:name:|resume of:|cv of:|curriculum vitae:|profile:)\s*' + re.escape(location), text, re.IGNORECASE):
                return location
    
    # Look for common city names near contact info
    contact_section = re.search(r'(?:contact|email|phone|tel|mobile)[^\n]{0,50}', text, re.IGNORECASE)
    if contact_section:
        contact_text = text[max(0, contact_section.start() - 100):contact_section.end() + 100]
        common_cities = r'(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|San Francisco|Charlotte|Indianapolis|Seattle|Denver|Washington|Boston|El Paso|Nashville|Detroit|Portland|Las Vegas|Memphis|Louisville|Baltimore|Milwaukee|Albuquerque|Tucson|Fresno|Sacramento|Long Beach|Kansas City|Mesa|Atlanta|Colorado Springs|Raleigh|Omaha|Miami|Oakland|Minneapolis|Tulsa|Cleveland|Wichita|Arlington|New Orleans|Bakersfield|Tampa|Honolulu|Aurora|Anaheim|Santa Ana|St. Louis|Riverside|Corpus Christi|Lexington|Pittsburgh|Anchorage|Stockton|Cincinnati|Saint Paul|Toledo|Newark|Greensboro|Plano|Henderson|Lincoln|Buffalo|Fort Wayne|Jersey City|Chula Vista|Orlando|St. Petersburg|Norfolk|Chandler|Laredo|Madison|Durham|Lubbock|Winston-Salem|Garland|Glendale|Hialeah|Reno|Baton Rouge|Irvine|Chesapeake|Irving|Scottsdale|North Las Vegas|Fremont|Gilbert|San Bernardino|Boise|Birmingham)'
        city_match = re.search(common_cities, contact_text, re.IGNORECASE)
        if city_match:
            return city_match.group(0)
    
    return ""

def extract_skills(text):
    """Extract potential skills based on common tech keywords"""
    common_skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "PHP", "Swift", 
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", 
        "SQL", "MongoDB", "AWS", "Azure", "Docker", "Kubernetes", "Git",
        "HTML", "CSS", "TypeScript", "REST API", "GraphQL", "Redux", "Express",
        "TensorFlow", "PyTorch", "Machine Learning", "Data Science", "Agile",
        "Scrum", "DevOps", "CI/CD", "Testing", "Debugging", "Problem Solving"
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    
    return ", ".join(found_skills)

def extract_experience(text):
    """Extract work experience information"""
    # Look for sections that might contain work experience
    exp_section_patterns = [
        r'(?:work\s*experience|employment|professional\s*experience).*?(?=education|skills|projects|$)',
        r'(?:experience|work history|employment history).*?(?=education|skills|projects|$)',
        r'(?:career|professional background).*?(?=education|skills|projects|$)'
    ]
    
    exp_text = ""
    for pattern in exp_section_patterns:
        exp_section_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if exp_section_match:
            exp_text = exp_section_match.group(0)
            break
    
    if not exp_text:  # If no section found, use the whole text
        exp_text = text
    
    # Try to find company-position pairs
    # Look for patterns like "Company Name - Position" or "Position at Company Name"
    company_position_patterns = [
        # Company - Position pattern
        r'([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)\s*[-–—]\s*([A-Za-z0-9\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect|Administrator|Programmer|Scientist|Officer|Coordinator|Associate)[^\n]*)',
        # Position at Company pattern
        r'([A-Za-z0-9\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect|Administrator|Programmer|Scientist|Officer|Coordinator|Associate)[^\n]*)\s+(?:at|@|for|with)\s+([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)',
        # Company (newline) Position pattern
        r'([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)\s*[\n\r]+\s*([A-Za-z0-9\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect|Administrator|Programmer|Scientist|Officer|Coordinator|Associate)[^\n]*)',
        # Date range followed by Company and/or Position
        r'(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4}-\d{1,2}|\d{4})\s*(?:to|-)\s*(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4}-\d{1,2}|\d{4}|Present|Current)\s*([A-Z][A-Za-z0-9\s&.,]+)\s*([A-Za-z0-9\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist)[^\n]*)?',
        # Position, Company pattern
        r'([A-Za-z0-9\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect|Administrator|Programmer|Scientist|Officer|Coordinator|Associate)[^\n]*),\s*([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)',
        # Company followed by date range
        r'([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)\s*(?:\(|\[)?(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4}-\d{1,2}|\d{4})\s*(?:to|-)\s*(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}|\d{4}-\d{1,2}|\d{4}|Present|Current)'
    ]
    
    # Extract bullet points or descriptions
    description_pattern = r'(?:•|-|\*)\s*([^\n•-\*]+)'  # Bullet points
    descriptions = re.findall(description_pattern, exp_text)
    
    experiences = []
    
    # Try each pattern
    for pattern in company_position_patterns:
        matches = re.findall(pattern, exp_text, re.IGNORECASE)
        for match in matches:
            if pattern == company_position_patterns[1] or pattern == company_position_patterns[4]:  # Position at/with Company or Position, Company
                company = match[1].strip()
                position = match[0].strip()
            else:  # Other patterns
                company = match[0].strip()
                position = match[1].strip() if len(match) > 1 and match[1].strip() else "Position not specified"
            
            # Add a description if available, otherwise use generic
            if descriptions:
                # Use the first 2 bullet points as description
                desc_text = " ".join(descriptions[:2])
                if len(desc_text) > 100:  # Truncate if too long
                    desc_text = desc_text[:97] + "..."
                description = desc_text
            else:
                description = f"Worked on various projects and initiatives at {company}"
            
            # Create the experience entry
            exp_entry = f"{company}, {position}, {description}"
            if exp_entry not in experiences:  # Avoid duplicates
                experiences.append(exp_entry)
    
    # If we found experiences, join them with the separator
    if experiences:
        return " | ".join(experiences)
    
    # Fallback: try to extract companies and positions separately
    companies = re.findall(r'([A-Z][A-Za-z\s&.,]+(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)?)', exp_text)
    positions = re.findall(r'([A-Za-z\s&.,]+(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect|Administrator|Programmer|Scientist|Officer|Coordinator|Associate))', exp_text)
    
    if companies and positions:
        # Create experiences from all combinations
        experiences = []
        for i, company in enumerate(companies[:3]):  # Limit to first 3 companies
            position = positions[i] if i < len(positions) else "Position not specified"
            description = f"Worked on various projects and initiatives at {company.strip()}"
            exp_entry = f"{company.strip()}, {position.strip()}, {description}"
            if exp_entry not in experiences:  # Avoid duplicates
                experiences.append(exp_entry)
        
        return " | ".join(experiences)
    
    # Last resort: just extract any company names and make generic entries
    if companies:
        experiences = []
        for company in companies[:3]:  # Limit to first 3 companies
            description = f"Worked at {company.strip()}"
            exp_entry = f"{company.strip()}, Professional, {description}"
            if exp_entry not in experiences:  # Avoid duplicates
                experiences.append(exp_entry)
        
        return " | ".join(experiences)
    
    return ""

def extract_education(text):
    """Extract education information"""
    # Look for sections that might contain education
    edu_section_patterns = [
        r'(?:education|academic|qualification).*?(?=experience|skills|projects|$)',
        r'(?:education|academic background|academic history).*?(?=experience|skills|projects|$)',
        r'(?:degree|university|college).*?(?=experience|skills|projects|$)'
    ]
    
    edu_text = ""
    for pattern in edu_section_patterns:
        edu_section_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if edu_section_match:
            edu_text = edu_section_match.group(0)
            break
    
    if not edu_text:  # If no section found, use the whole text
        edu_text = text
    
    # Try to extract degree and institution with more comprehensive patterns
    degree_patterns = [
        r'(Bachelor|Master|PhD|Doctorate|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.E\.|M\.E\.|B\.Tech|M\.Tech|B\.Sc|M\.Sc|B\.Com|M\.Com|B\.B\.A|M\.B\.A)[^\n]*',
        r'(Bachelor[^\n]*?|Master[^\n]*?|Doctor[^\n]*?|Ph\.?D\.?)[^\n]*?(?:in|of)[^\n]*?([A-Za-z\s]+)',
        r'([A-Za-z]+\s+(?:in|of)\s+[A-Za-z\s]+)',  # Degree in/of Subject
        r'([A-Za-z]+\s+[A-Za-z]+\s+Degree)'  # Any degree mention
    ]
    
    institution_patterns = [
        r'(University|College|Institute|School)\s+of\s+[A-Za-z\s]+',
        r'([A-Z][A-Za-z]+\s+(?:University|College|Institute|School))',
        r'([A-Z][A-Za-z\s]+\s+(?:University|College|Institute|School))',
        r'([A-Z][A-Za-z\s&\.,-]+)'  # Any capitalized name that might be an institution
    ]
    
    year_patterns = [
        r'(20\d{2}|19\d{2})',  # Standard year format
        r'(\d{2}/\d{2})',  # MM/YY format
        r'(\d{2}-\d{2})',  # MM-YY format
        r'(?:in|year|graduated)\s+(\d{4})'  # Year with context
    ]
    
    # Extract all matches
    degrees = []
    for pattern in degree_patterns:
        matches = re.findall(pattern, edu_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                degrees.append(match[0].strip())
            else:
                degrees.append(match.strip())
    
    institutions = []
    for pattern in institution_patterns:
        matches = re.findall(pattern, edu_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                institutions.append(match[0].strip())
            else:
                institutions.append(match.strip())
    
    years = []
    for pattern in year_patterns:
        matches = re.findall(pattern, edu_text, re.IGNORECASE)
        for match in matches:
            years.append(match.strip())
    
    # Filter out institutions that are likely not educational institutions
    filtered_institutions = []
    for inst in institutions:
        # Skip if it's likely a company name
        if re.search(r'(?:Inc|LLC|Ltd|Corp|Corporation|Technologies|Solutions|Group|Systems)', inst, re.IGNORECASE):
            continue
        # Skip if it's too short
        if len(inst) < 5:
            continue
        filtered_institutions.append(inst)
    
    institutions = filtered_institutions if filtered_institutions else institutions
    
    # Create education entries
    education_entries = []
    
    # If we have degrees and institutions, create entries
    if degrees and institutions:
        for i in range(min(len(degrees), len(institutions))):
            degree = degrees[i]
            institution = institutions[i]
            year = years[i] if i < len(years) else (years[0] if years else "Present")
            education_entries.append(f"{degree}, {institution}, {year}")
    
    # If we only have institutions, create entries with generic degrees
    elif institutions:
        for i, institution in enumerate(institutions[:2]):  # Limit to first 2 institutions
            year = years[i] if i < len(years) else (years[0] if years else "Present")
            education_entries.append(f"Degree, {institution}, {year}")
    
    # If we only have degrees, create entries with generic institutions
    elif degrees:
        for i, degree in enumerate(degrees[:2]):  # Limit to first 2 degrees
            year = years[i] if i < len(years) else (years[0] if years else "Present")
            education_entries.append(f"{degree}, University, {year}")
    
    # Join entries with separator
    if education_entries:
        return " | ".join(education_entries)
    
    return ""

def extract_projects(text):
    """Extract project information"""
    # Look for sections that might contain projects
    proj_section_patterns = [
        r'(?:projects|personal\s*projects).*?(?=experience|education|skills|$)',
        r'(?:portfolio|selected\s*projects|key\s*projects).*?(?=experience|education|skills|$)',
        r'(?:github|repositories|open\s*source).*?(?=experience|education|skills|$)'
    ]
    
    proj_text = ""
    for pattern in proj_section_patterns:
        proj_section_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if proj_section_match:
            proj_text = proj_section_match.group(0)
            break
    
    if not proj_text:  # If no section found, return empty
        return ""
    
    # Try different patterns to extract project information
    project_patterns = [
        r'([A-Z][A-Za-z0-9\s]+)(?::|-)([^\n]+)',  # Project: Description or Project - Description
        r'([A-Z][A-Za-z0-9\s]+)\s*\(([^\)]+)\)',  # Project (Description)
        r'(?:•|\*|-)\s*([A-Z][A-Za-z0-9\s]+)(?::|-)([^\n]+)',  # • Project: Description
        r'(?:•|\*|-)\s*([A-Z][A-Za-z0-9\s]+)\s*\(([^\)]+)\)',  # • Project (Description)
        r'(?:•|\*|-)\s*([A-Z][A-Za-z0-9\s]+)[^\n]*'  # • Project with no clear description
    ]
    
    all_projects = []
    
    # Try each pattern
    for pattern in project_patterns:
        projects = re.findall(pattern, proj_text, re.MULTILINE)
        
        for project in projects:
            if isinstance(project, tuple) and len(project) >= 2:
                project_name = project[0].strip()
                project_desc = project[1].strip()
                all_projects.append(f"{project_name}, {project_desc}")
            elif isinstance(project, tuple) and len(project) == 1:
                project_name = project[0].strip()
                all_projects.append(f"{project_name}, A project in the portfolio")
            elif isinstance(project, str):
                project_name = project.strip()
                all_projects.append(f"{project_name}, A project in the portfolio")
    
    # If we found projects, join them with the separator
    if all_projects:
        # Limit to first 3 projects to avoid overwhelming the form
        return " | ".join(all_projects[:3])
    
    return ""

def extract_certifications(text):
    """Extract certification information"""
    # Look for sections that might contain certifications
    cert_section_patterns = [
        r'(?:certifications|certificates|qualifications).*?(?=experience|education|skills|projects|$)',
        r'(?:professional certifications|technical certifications|credentials).*?(?=experience|education|skills|projects|$)',
        r'(?:licenses|accreditations).*?(?=experience|education|skills|projects|$)'
    ]
    
    cert_text = ""
    for pattern in cert_section_patterns:
        cert_section_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if cert_section_match:
            cert_text = cert_section_match.group(0)
            break
    
    if not cert_text:  # If no section found, search the whole text
        cert_text = text
    
    # Try to extract certification names with more comprehensive patterns
    cert_patterns = [
        r'([A-Za-z][A-Za-z0-9\s\-]+(?:Certification|Certificate|Certified))',  # Standard certification format
        r'([A-Za-z][A-Za-z0-9\s\-]+\s+(?:Professional|Specialist|Expert|Associate|Practitioner))',  # Professional titles
        r'((?:AWS|Azure|Google|Microsoft|Oracle|Cisco|CompTIA|PMI|ITIL|Scrum|SAFe|PMP|CISSP|CISA|CISM|CEH|CCNA|MCSA|MCSE|MCTS|RHCE|RHCSA|Security\+|Network\+|A\+|CAPM|CSM|CSPO|ACP|PgMP|PfMP|PMI-ACP|PMI-PBA|PMI-RMP|PMI-SP)[A-Za-z0-9\s\-]*)',  # Common certification providers
        r'(?:•|-|\*)\s*([A-Za-z][A-Za-z0-9\s\-]{3,}(?:Certification|Certificate|Certified|Professional|Specialist|Expert|Associate|Practitioner))',  # Bullet points
        r'(?:earned|achieved|obtained|received|completed)\s+([A-Za-z][A-Za-z0-9\s\-]+(?:Certification|Certificate|Certified|Professional|Specialist|Expert|Associate|Practitioner))'  # Action verbs
    ]
    
    # Extract all matches
    certs = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, cert_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                certs.append(match[0].strip())
            else:
                certs.append(match.strip())
    
    # Filter out duplicates and very short certifications
    filtered_certs = []
    seen = set()
    for cert in certs:
        if cert.lower() not in seen and len(cert) > 5:
            filtered_certs.append(cert)
            seen.add(cert.lower())
    
    # If we found certifications, join them with commas
    if filtered_certs:
        return ", ".join(filtered_certs)
    
    # If no certifications found, look for common certification keywords
    common_certs = [
        "AWS Certified Solutions Architect",
        "Microsoft Certified Professional",
        "Certified ScrumMaster",
        "Project Management Professional",
        "Certified Information Systems Security Professional",
        "CompTIA Security+",
        "Cisco Certified Network Associate",
        "Google Cloud Professional",
        "Oracle Certified Professional",
        "Certified Kubernetes Administrator"
    ]
    
    for cert in common_certs:
        if re.search(r'\b' + re.escape(cert.split()[0]) + r'\b', text, re.IGNORECASE):
            return cert
    
    return ""

def extract_languages(text):
    """Extract language information"""
    # Common languages with context patterns
    language_patterns = {
        "English": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?English', r'English\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?English'],
        "Spanish": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Spanish', r'Spanish\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Spanish'],
        "French": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?French', r'French\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?French'],
        "German": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?German', r'German\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?German'],
        "Chinese": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?(?:Chinese|Mandarin|Cantonese)', r'(?:Chinese|Mandarin|Cantonese)\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?(?:Chinese|Mandarin|Cantonese)'],
        "Japanese": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Japanese', r'Japanese\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Japanese'],
        "Russian": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Russian', r'Russian\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Russian'],
        "Arabic": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Arabic', r'Arabic\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Arabic'],
        "Portuguese": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Portuguese', r'Portuguese\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Portuguese'],
        "Italian": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Italian', r'Italian\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Italian'],
        "Hindi": [r'(?:speak|know|fluent|native|proficient|advanced|intermediate|basic)\s+(?:in\s+)?Hindi', r'Hindi\s+(?:speaker|language|proficiency|skills?)', r'Languages?[^.]*?Hindi']
    }
    
    # Look for language section
    lang_section_pattern = r'(?:languages?|linguistic skills|communication skills).*?(?=skills|experience|education|$)'
    lang_section_match = re.search(lang_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    lang_text = lang_section_match.group(0) if lang_section_match else text
    
    found_languages = []
    for lang, patterns in language_patterns.items():
        for pattern in patterns:
            if re.search(pattern, lang_text, re.IGNORECASE):
                found_languages.append(lang)
                break
    
    if found_languages:
        return ", ".join(found_languages)
    return ""

def extract_field_of_work(text, skills_text=""):
    """Try to determine the field of work using both resume text and extracted skills"""
    # Define patterns for different fields with more comprehensive keywords
    field_patterns = {
        "Frontend Developer": [r'front[\s\-]?end', r'UI', r'React', r'Angular', r'Vue', r'HTML', r'CSS', r'JavaScript', r'web\s*developer', r'front[\s\-]?end\s*developer', r'UI\s*developer', r'client[\s\-]?side', r'responsive', r'web\s*design'],
        "Backend Developer": [r'back[\s\-]?end', r'server', r'API', r'database', r'Django', r'Flask', r'Express', r'Node\.js', r'back[\s\-]?end\s*developer', r'server[\s\-]?side', r'PHP', r'Ruby', r'Java\s*developer', r'Python\s*developer', r'SQL', r'NoSQL'],
        "Full-Stack Developer": [r'full[\s\-]?stack', r'front[\s\-]?end.*back[\s\-]?end', r'back[\s\-]?end.*front[\s\-]?end', r'full[\s\-]?stack\s*developer', r'MERN', r'MEAN', r'end[\s\-]?to[\s\-]?end', r'client.*server', r'server.*client'],
        "DevOps Engineer": [r'DevOps', r'CI/CD', r'Docker', r'Kubernetes', r'AWS', r'Azure', r'cloud', r'infrastructure', r'deployment', r'automation', r'Jenkins', r'GitLab\s*CI', r'GitHub\s*Actions', r'Terraform', r'Ansible', r'configuration\s*management'],
        "Data Scientist": [r'data\s*scien', r'machine\s*learning', r'AI', r'analytics', r'statistics', r'Python', r'R', r'data\s*analysis', r'big\s*data', r'data\s*mining', r'data\s*visualization', r'predictive\s*modeling', r'statistical\s*analysis', r'pandas', r'numpy'],
        "Machine Learning Engineer": [r'machine\s*learning', r'deep\s*learning', r'neural\s*network', r'TensorFlow', r'PyTorch', r'ML\s*engineer', r'AI\s*engineer', r'computer\s*vision', r'NLP', r'natural\s*language\s*processing', r'reinforcement\s*learning', r'supervised\s*learning', r'unsupervised\s*learning'],
        "UI/UX Designer": [r'UI', r'UX', r'design', r'user\s*experience', r'user\s*interface', r'Figma', r'Sketch', r'Adobe\s*XD', r'wireframe', r'prototype', r'usability', r'interaction\s*design', r'visual\s*design', r'user\s*research', r'user\s*testing'],
        "Product Manager": [r'product\s*manag', r'product\s*owner', r'scrum', r'agile', r'roadmap', r'stakeholder', r'product\s*development', r'product\s*strategy', r'user\s*stories', r'backlog', r'sprint', r'market\s*research', r'customer\s*feedback', r'product\s*requirements'],
        "QA Engineer": [r'QA', r'quality\s*assurance', r'testing', r'test\s*automation', r'Selenium', r'QA\s*engineer', r'test\s*engineer', r'software\s*tester', r'manual\s*testing', r'automated\s*testing', r'test\s*cases', r'test\s*plans', r'regression\s*testing', r'functional\s*testing', r'performance\s*testing']
    }
    
    # Define skill sets for each field
    field_skills = {
        "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue", "TypeScript", "SASS", "LESS", "Bootstrap", "jQuery", "Responsive Design", "Web Design", "UI", "UX", "Webpack", "Babel"],
        "Backend Developer": ["Python", "Java", "C#", "PHP", "Ruby", "Node.js", "Express", "Django", "Flask", "Spring", "Laravel", "SQL", "MySQL", "PostgreSQL", "MongoDB", "API", "REST", "GraphQL", "Microservices"],
        "Full-Stack Developer": ["JavaScript", "TypeScript", "Python", "Java", "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "Spring", "SQL", "NoSQL", "REST API", "GraphQL", "MERN", "MEAN", "Full Stack"],
        "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform", "Ansible", "Puppet", "Chef", "Linux", "Shell Scripting", "Monitoring", "Logging", "Cloud"],
        "Data Scientist": ["Python", "R", "SQL", "Pandas", "NumPy", "SciPy", "Scikit-learn", "TensorFlow", "PyTorch", "Statistics", "Data Analysis", "Data Visualization", "Machine Learning", "Big Data", "Hadoop", "Spark", "Tableau", "Power BI"],
        "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Deep Learning", "Neural Networks", "NLP", "Computer Vision", "Reinforcement Learning", "MLOps", "Feature Engineering", "Model Deployment", "AI"],
        "UI/UX Designer": ["Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator", "InVision", "Wireframing", "Prototyping", "User Research", "Usability Testing", "Interaction Design", "Visual Design", "UI", "UX", "Design Systems"],
        "Product Manager": ["Agile", "Scrum", "Kanban", "Jira", "Confluence", "Product Strategy", "Roadmapping", "User Stories", "Market Research", "Competitive Analysis", "Stakeholder Management", "Product Development", "Product Launch"],
        "QA Engineer": ["Selenium", "Cypress", "Jest", "Mocha", "JUnit", "TestNG", "Manual Testing", "Automated Testing", "Test Plans", "Test Cases", "Bug Tracking", "JIRA", "QA", "Quality Assurance", "Regression Testing"]
    }
    
    # Look for explicit job titles first
    job_title_patterns = {
        "Frontend Developer": [r'front[\s\-]?end\s*developer', r'UI\s*developer', r'JavaScript\s*developer', r'React\s*developer', r'Angular\s*developer', r'Vue\s*developer'],
        "Backend Developer": [r'back[\s\-]?end\s*developer', r'server[\s\-]?side\s*developer', r'API\s*developer', r'Python\s*developer', r'Java\s*developer', r'PHP\s*developer', r'Ruby\s*developer', r'Node\.js\s*developer'],
        "Full-Stack Developer": [r'full[\s\-]?stack\s*developer', r'full[\s\-]?stack\s*engineer', r'software\s*engineer', r'web\s*developer'],
        "DevOps Engineer": [r'DevOps\s*engineer', r'cloud\s*engineer', r'infrastructure\s*engineer', r'site\s*reliability\s*engineer', r'SRE', r'platform\s*engineer'],
        "Data Scientist": [r'data\s*scientist', r'data\s*analyst', r'analytics\s*specialist', r'business\s*intelligence', r'BI\s*developer', r'data\s*engineer'],
        "Machine Learning Engineer": [r'machine\s*learning\s*engineer', r'ML\s*engineer', r'AI\s*engineer', r'deep\s*learning\s*specialist', r'NLP\s*engineer', r'computer\s*vision\s*engineer'],
        "UI/UX Designer": [r'UI\s*designer', r'UX\s*designer', r'UI/UX\s*designer', r'product\s*designer', r'interaction\s*designer', r'visual\s*designer', r'web\s*designer'],
        "Product Manager": [r'product\s*manager', r'product\s*owner', r'program\s*manager', r'project\s*manager', r'scrum\s*master', r'agile\s*coach'],
        "QA Engineer": [r'QA\s*engineer', r'test\s*engineer', r'quality\s*assurance\s*engineer', r'software\s*tester', r'test\s*automation\s*engineer', r'SDET']
    }
    
    # First check for explicit job titles
    for field, patterns in job_title_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return field
    
    # Initialize scores for each field
    field_scores = {field: 0 for field in field_patterns}
    
    # Score based on keyword patterns in the text
    for field, patterns in field_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            field_scores[field] += len(matches)
    
    # Score based on skills mentioned in the resume
    if skills_text:
        skills_list = [skill.strip().lower() for skill in skills_text.split(',')]
        
        for field, skill_set in field_skills.items():
            for skill in skill_set:
                if any(s.lower() == skill.lower() or skill.lower() in s.lower() for s in skills_list):
                    field_scores[field] += 2  # Give more weight to skills matches
    
    # Also analyze work experience for job titles
    exp_section_pattern = r'(?:work\s*experience|employment|professional\s*experience).*?(?=education|skills|projects|$)'
    exp_section_match = re.search(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if exp_section_match:
        exp_text = exp_section_match.group(0)
        for field, patterns in job_title_patterns.items():
            for pattern in patterns:
                if re.search(pattern, exp_text, re.IGNORECASE):
                    field_scores[field] += 3  # Give even more weight to job titles in experience
    
    # Find the field with the highest score
    max_score = 0
    best_field = ""
    for field, score in field_scores.items():
        if score > max_score:
            max_score = score
            best_field = field
    
    return best_field

def extract_linkedin(text):
    """Extract LinkedIn profile URL"""
    linkedin_patterns = [
        r'linkedin\.com/in/([\w-]+)',
        r'linkedin:\s*(https?://[^\s]+)',
        r'linkedin[^\n:]*:\s*([^\s\n]+)'
    ]
    
    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # If it's just the username, construct the full URL
            if not match.group(1).startswith('http'):
                if '/' in match.group(1):
                    return f"https://www.linkedin.com/in/{match.group(1)}"
                else:
                    return f"https://www.linkedin.com/in/{match.group(1)}"
            return match.group(1)
    return ""

def extract_website(text):
    """Extract personal website URL"""
    website_patterns = [
        r'website:\s*(https?://[^\s\n]+)',
        r'personal\s*site:\s*(https?://[^\s\n]+)',
        r'portfolio:\s*(https?://[^\s\n]+)',
        r'(https?://(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    ]
    
    for pattern in website_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_blog(text):
    """Extract blog URL"""
    blog_patterns = [
        r'blog:\s*(https?://[^\s\n]+)',
        r'medium:\s*(https?://[^\s\n]+)',
        r'(https?://(?:www\.)?medium\.com/[^\s\n]+)',
        r'(https?://(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]*\.(?:wordpress|blogspot|tumblr)\.com)'
    ]
    
    for pattern in blog_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_youtube(text):
    """Extract YouTube channel URL"""
    youtube_patterns = [
        r'youtube:\s*(https?://[^\s\n]+)',
        r'youtube\s*channel:\s*(https?://[^\s\n]+)',
        r'(https?://(?:www\.)?youtube\.com/(?:c/|channel/|user/)[^\s\n]+)'
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""

def extract_experience_info(text):
    """Try to determine experience level and years"""
    # Look for years of experience with more comprehensive patterns
    year_patterns = [
        r'(\d+)\+?\s*(?:years|yrs|year)\s*(?:of)?\s*(?:experience|exp)',
        r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs|year)',
        r'(\d+)\+?\s*(?:years|yrs|year)\s*(?:in|of)\s*(?:industry|professional|work)',
        r'(?:professional|work|industry)\s*experience\s*(?:of)?\s*(\d+)\+?\s*(?:years|yrs|year)',
        r'(?:career|work)\s*(?:spanning|of)\s*(\d+)\+?\s*(?:years|yrs|year)'
    ]
    
    years = None
    for pattern in year_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                years = int(match.group(1))
                break
            except (ValueError, IndexError):
                continue
    
    # Count number of work experiences and estimate years if not found directly
    if years is None:
        # Extract work experience section
        exp_section_pattern = r'(?:work\s*experience|employment|professional\s*experience).*?(?=education|skills|projects|$)'
        exp_section_match = re.search(exp_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_section_match:
            exp_text = exp_section_match.group(0)
            # Count number of positions by looking for common job title keywords
            position_count = len(re.findall(r'(?:Developer|Engineer|Manager|Designer|Analyst|Consultant|Director|Specialist|Lead|Architect)', exp_text, re.IGNORECASE))
            # Count date ranges as an indicator of experience
            date_ranges = len(re.findall(r'(?:\d{4}|\d{2})\s*(?:-|to|–)\s*(?:\d{4}|\d{2}|present|current)', exp_text, re.IGNORECASE))
            
            # Estimate years based on positions and date ranges
            if position_count > 0 or date_ranges > 0:
                estimated_years = max(position_count, date_ranges) * 2  # Rough estimate: 2 years per position/date range
                years = min(estimated_years, 15)  # Cap at 15 years to avoid overestimation
    
    # Determine experience level based on years or keywords
    experience_level = ""
    if years is not None:
        if years == 0:
            experience_level = "Intern"
        elif years <= 1:
            experience_level = "Entry Level"
        elif years <= 3:
            experience_level = "Junior"
        elif years <= 6:
            experience_level = "Mid-Level"
        elif years <= 9:
            experience_level = "Senior"
        elif years <= 12:
            experience_level = "Lead"
        else:
            experience_level = "Manager"
    else:
        # Look for keywords indicating experience level with more comprehensive patterns
        level_patterns = {
            "Intern": [r'intern', r'internship', r'trainee', r'student', r'apprentice', r'co-op'],
            "Entry Level": [r'entry[\s\-]?level', r'junior', r'graduate', r'recent\s*graduate', r'fresher', r'beginner', r'novice', r'0-1\s*years?'],
            "Junior": [r'junior', r'jr\.', r'associate', r'1-3\s*years?'],
            "Mid-Level": [r'mid[\s\-]?level', r'intermediate', r'experienced', r'3-5\s*years?', r'4-6\s*years?'],
            "Senior": [r'senior', r'sr\.', r'experienced', r'advanced', r'expert', r'6\+\s*years?', r'7-9\s*years?'],
            "Lead": [r'lead', r'principal', r'architect', r'team\s*lead', r'technical\s*lead', r'10\+\s*years?'],
            "Manager": [r'manager', r'director', r'head\s*of', r'chief', r'vp', r'executive', r'12\+\s*years?']
        }
        
        # Count matches for each level
        level_scores = {level: 0 for level in level_patterns}
        for level, patterns in level_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                level_scores[level] += len(matches)
        
        # Find the level with the highest score
        max_score = 0
        for level, score in level_scores.items():
            if score > max_score:
                max_score = score
                experience_level = level
    
    return experience_level, str(years) if years is not None else ""


# Test function to verify parsing functionality
def test_parser():
    """Test function to verify the resume parsing functionality"""
    print("\n===== TESTING RESUME PARSER =====\n")
    
    # Test data
    test_text = """
    John Doe
    Software Engineer
    john.doe@example.com
    (555) 123-4567
    San Francisco, CA
    
    SUMMARY
    Experienced software engineer with 5 years of experience in full-stack development.
    Proficient in Python, JavaScript, React, and Node.js.
    
    SKILLS
    Python, JavaScript, React, Node.js, MongoDB, SQL, Git, Docker, AWS
    
    WORK EXPERIENCE
    
    Senior Software Engineer
    ABC Tech - 2020 to Present
    - Developed and maintained web applications using React and Node.js
    - Implemented CI/CD pipelines using GitHub Actions
    - Led a team of 3 junior developers
    
    Software Developer
    XYZ Solutions - 2018 to 2020
    - Built RESTful APIs using Python and Flask
    - Worked on database optimization and performance tuning
    - Collaborated with UX designers to implement frontend features
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    University of California, Berkeley - 2018
    
    CERTIFICATIONS
    AWS Certified Developer
    MongoDB Certified Developer
    
    LANGUAGES
    English (Native), Spanish (Intermediate)
    """
    
    # Test extraction functions
    print("Name:", extract_name(test_text))
    print("Email:", extract_email(test_text))
    print("Phone:", extract_phone(test_text))
    print("Location:", extract_location(test_text))
    print("Summary:", extract_summary(test_text))
    print("Skills:", extract_skills(test_text))
    print("Experience:", extract_experience(test_text))
    print("Education:", extract_education(test_text))
    print("Certifications:", extract_certifications(test_text))
    print("Languages:", extract_languages(test_text))
    
    # Test field of work detection
    field_of_work = extract_field_of_work(test_text, extract_skills(test_text))
    print("Field of Work:", field_of_work)
    
    # Test experience level detection
    experience_level, years = extract_experience_info(test_text)
    print("Experience Level:", experience_level)
    print("Years of Experience:", years)
    
    print("\n===== TEST COMPLETE =====\n")


# Uncomment to run the test
# if __name__ == "__main__":
#     test_parser()