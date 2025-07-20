# utils/resume_generator.py
import os
import uuid
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Import docx2pdf conditionally to avoid errors if it's not available
try:
    import docx2pdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def generate_resume_file(data):
    # Create a unique filename
    unique_id = str(uuid.uuid4())
    docx_path = f"resumes/resume_{unique_id}.docx"
    
    # Ensure the resumes directory exists
    os.makedirs("resumes", exist_ok=True)
    
    # Create a new Document
    doc = Document()
    
    # Set up styles
    styles = doc.styles
    
    # Heading style
    heading_style = styles.add_style('ResumeHeading', WD_STYLE_TYPE.PARAGRAPH)
    heading_style.font.name = 'Calibri'
    heading_style.font.size = Pt(16)
    heading_style.font.bold = True
    heading_style.font.color.rgb = RGBColor(0, 0, 0)
    
    # Subheading style
    subheading_style = styles.add_style('ResumeSubheading', WD_STYLE_TYPE.PARAGRAPH)
    subheading_style.font.name = 'Calibri'
    subheading_style.font.size = Pt(14)
    subheading_style.font.bold = True
    subheading_style.font.color.rgb = RGBColor(0, 0, 0)
    
    # Normal text style
    normal_style = styles.add_style('ResumeNormal', WD_STYLE_TYPE.PARAGRAPH)
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    
    # Add name as title
    title = doc.add_paragraph(data.get("full_name", "Unnamed"))
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    
    # Add contact information
    contact_info = doc.add_paragraph()
    contact_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_info.add_run(f"{data.get('email', '')} | {data.get('phone', '')} | {data.get('location', '')}").font.size = Pt(11)
    
    # Add field of work and experience level
    job_title = doc.add_paragraph()
    job_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    job_title.add_run(f"{data.get('field_of_work', '')} - {data.get('experience_level', '')} ({data.get('years_of_experience', '')} years)").font.size = Pt(12)
    job_title.runs[0].font.italic = True
    
    # Add a line separator
    doc.add_paragraph("_" * 80)
    
    # Professional Summary
    doc.add_paragraph("PROFESSIONAL SUMMARY", style='ResumeHeading')
    doc.add_paragraph(data.get("summary", ""), style='ResumeNormal')
    
    # Skills
    doc.add_paragraph("SKILLS", style='ResumeHeading')
    skills_text = data.get("skills", "")
    doc.add_paragraph(skills_text, style='ResumeNormal')
    
    # Work Experience
    doc.add_paragraph("WORK EXPERIENCE", style='ResumeHeading')
    experience_text = data.get("experience", "")
    for exp in experience_text.split("|"):
        if exp.strip():
            parts = exp.split(",", 2)
            if len(parts) >= 2:
                company = parts[0].strip()
                title = parts[1].strip()
                exp_para = doc.add_paragraph(style='ResumeSubheading')
                exp_para.add_run(f"{company} - {title}").font.bold = True
                
                if len(parts) > 2:
                    desc = parts[2].strip()
                    doc.add_paragraph(desc, style='ResumeNormal')
            else:
                doc.add_paragraph(exp.strip(), style='ResumeNormal')
    
    # Education
    doc.add_paragraph("EDUCATION", style='ResumeHeading')
    education_text = data.get("education", "")
    for edu in education_text.split("|"):
        if edu.strip():
            parts = edu.split(",")
            if len(parts) >= 2:
                degree = parts[0].strip()
                institution = parts[1].strip()
                edu_para = doc.add_paragraph(style='ResumeSubheading')
                edu_para.add_run(f"{degree}, {institution}").font.bold = True
                
                if len(parts) > 2:
                    year = parts[2].strip()
                    doc.add_paragraph(f"Graduation Year: {year}", style='ResumeNormal')
            else:
                doc.add_paragraph(edu.strip(), style='ResumeNormal')
    
    # Projects (Optional)
    projects = data.get("projects")
    if projects and projects.strip():
        doc.add_paragraph("PROJECTS", style='ResumeHeading')
        for project in projects.split("|"):
            if project.strip():
                parts = project.split(",", 1)
                if len(parts) >= 1:
                    project_name = parts[0].strip()
                    proj_para = doc.add_paragraph(style='ResumeSubheading')
                    proj_para.add_run(project_name).font.bold = True
                    
                    if len(parts) > 1:
                        desc = parts[1].strip()
                        doc.add_paragraph(desc, style='ResumeNormal')
    
    # Certifications (Optional)
    certifications = data.get("certifications")
    if certifications and certifications.strip():
        doc.add_paragraph("CERTIFICATIONS", style='ResumeHeading')
        for cert in certifications.split(","):
            if cert.strip():
                doc.add_paragraph(cert.strip(), style='ResumeNormal')
    
    # Languages (Optional)
    languages = data.get("languages")
    if languages and languages.strip():
        doc.add_paragraph("LANGUAGES", style='ResumeHeading')
        doc.add_paragraph(languages, style='ResumeNormal')
    
    # Save the document
    doc.save(docx_path)
    
    # Convert to PDF if requested
    if data.get("output_format") == "pdf":
        pdf_path = docx_path.replace(".docx", ".pdf")
        if PDF_AVAILABLE:
            try:
                docx2pdf.convert(docx_path, pdf_path)
                return pdf_path
            except Exception as e:
                print(f"Error converting to PDF: {e}")
                # Return DOCX as fallback
                return docx_path
        else:
            print("PDF conversion not available. docx2pdf module not found or not working.")
            # Return DOCX as fallback
            return docx_path
    
    return docx_path
