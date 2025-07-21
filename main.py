from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.resume_generator import generate_resume_file
from utils.resume_parser import parse_resume
import os
import shutil
import json
import datetime
from typing import Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Redirect root path to form
@app.get("/", include_in_schema=False)
def redirect_to_form():
    return RedirectResponse("/form")

# Serve the form
@app.get("/form", response_class=HTMLResponse)
def serve_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Parse uploaded resume
@app.post("/parse-resume")
async def parse_uploaded_resume(resume: UploadFile = File(...)):
    try:
        # Check if file is a supported format
        if not resume.filename.lower().endswith(('.docx', '.pdf', '.doc')):
            return JSONResponse(
                content={"error": "Unsupported file format. Please upload a DOCX, DOC, or PDF file."},
                status_code=400
            )
            
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file temporarily
        temp_file_path = f"uploads/temp_{resume.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        
        # Parse the resume
        parsed_data = parse_resume(temp_file_path)
        
        # Validate and clean parsed data
        for key, value in parsed_data.items():
            # Ensure all values are strings
            if value is None:
                parsed_data[key] = ""
            elif not isinstance(value, str):
                parsed_data[key] = str(value)
                
            # Ensure values are not too long
            if isinstance(parsed_data[key], str) and len(parsed_data[key]) > 10000:
                parsed_data[key] = parsed_data[key][:10000] + "..."
        
        # Log parsed data for debugging
        print("\n===== PARSED RESUME DATA =====\n")
        for key, value in parsed_data.items():
            print(f"{key}: {value}")
        print("\n=============================\n")
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        # Add debug info to response
        parsed_data['_debug_info'] = {
            'file_name': resume.filename,
            'file_size': resume.size,
            'content_type': resume.content_type,
            'timestamp': str(datetime.datetime.now())
        }
        
        # Ensure all required fields are present
        required_fields = ['full_name', 'email', 'phone', 'location', 'summary', 'skills', 
                          'experience', 'education', 'field_of_work', 'experience_level', 
                          'years_of_experience', 'certifications']
        
        for field in required_fields:
            if field not in parsed_data or not parsed_data[field]:
                # Add placeholder for missing fields
                if field == 'full_name':
                    parsed_data[field] = "Your Name"
                elif field == 'email':
                    parsed_data[field] = "your.email@example.com"
                elif field == 'phone':
                    parsed_data[field] = "+1 (555) 123-4567"
                elif field == 'location':
                    parsed_data[field] = "City, State, Country"
                elif field == 'summary':
                    parsed_data[field] = "Professional summary extracted from your resume."
                elif field == 'skills':
                    parsed_data[field] = "Skill 1, Skill 2, Skill 3"
                elif field == 'experience':
                    parsed_data[field] = "Company, Position, Description"
                elif field == 'education':
                    parsed_data[field] = "Degree, Institution, Year"
                elif field == 'field_of_work':
                    parsed_data[field] = "Full-Stack Developer"
                elif field == 'experience_level':
                    parsed_data[field] = "Mid-Level"
                elif field == 'years_of_experience':
                    parsed_data[field] = "3"
                elif field == 'certifications':
                    parsed_data[field] = "Certification 1, Certification 2"
        
        return JSONResponse(content=parsed_data)
    except Exception as e:
        return JSONResponse(content={"error": f"Error parsing resume: {str(e)}"}, status_code=500)

# For backward compatibility, also serve the form at root
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate")
async def generate(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    summary: str = Form(...),
    field_of_work: str = Form(None),
    experience_level: str = Form(...),
    years_of_experience: str = Form(...),
    skills: str = Form(...),
    experience: str = Form(...),
    education: str = Form(...),
    projects: str = Form(None),
    website: str = Form(None),
    blog: str = Form(None),
    youtube: str = Form(None),
    linkedin: str = Form(None),
    certifications: str = Form(None),
    languages: str = Form(None),
    output_format: str = Form(...),
    # field_selection_type parameter is no longer needed
    manual_field_value: str = Form(None),
    existing_resume: UploadFile = File(None)
):
    try:
        # Use other field value if "other" option was selected
        if field_of_work == "other" and manual_field_value:
            field_of_work = manual_field_value
        
        # Handle uploaded resume if provided
        uploaded_resume_path = None
        if existing_resume and existing_resume.filename:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Save the uploaded file
            file_extension = existing_resume.filename.split('.')[-1]
            uploaded_resume_path = f"uploads/{full_name.replace(' ', '_')}_uploaded.{file_extension}"
            
            with open(uploaded_resume_path, "wb") as buffer:
                shutil.copyfileobj(existing_resume.file, buffer)
            
        data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "summary": summary,
            "field_of_work": field_of_work,
            "experience_level": experience_level,
            "years_of_experience": years_of_experience,
            "skills": skills,
            "experience": experience,
            "education": education,
            "projects": projects,
            "website": website,
            "blog": blog,
            "youtube": youtube,
            "certifications": certifications,
            "languages": languages,
            "output_format": output_format,
            "uploaded_resume_path": uploaded_resume_path
        }
        
        resume_path = generate_resume_file(data)
        filename = f"resume_{full_name.replace(' ', '_')}.{output_format}"
        
        # Create a download URL
        download_url = f"/download/{os.path.basename(resume_path)}"
        
        # Return the success template with download information
        return templates.TemplateResponse(
            "success.html", 
            {
                "request": request,
                "full_name": full_name,
                "field_of_work": field_of_work,
                "output_format": output_format,
                "download_url": download_url,
                "uploaded_resume": True if uploaded_resume_path else False
            }
        )
    except Exception as e:
        return HTMLResponse(f"Internal Error: {str(e)}", status_code=500)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"resumes/{filename}"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )