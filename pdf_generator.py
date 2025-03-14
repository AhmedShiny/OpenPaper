import re
from datetime import datetime
from fpdf import FPDF
import unicodedata
import os

def normalize_text(text):
    """Replace Unicode characters with ASCII equivalents or remove them if not possible"""
    if not text:
        return ""
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2014': '--',  # em dash
        '\u2013': '-',   # en dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2022': '*',   # bullet
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',    # non-breaking space
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # For any remaining non-ASCII characters, try to normalize or replace them
    return ''.join(c if ord(c) < 128 else unicodedata.normalize('NFKD', c).encode('ascii', 'ignore').decode('ascii', 'ignore') for c in text)

def save_report_as_pdf(result):
    """Save the research paper as a PDF file"""
    try:
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, normalize_text(result["topic"]), ln=True, align="C")
        pdf.ln(10)
        
        # Date
        pdf.set_font("Arial", "I", 10)
        current_date = datetime.now().strftime("%Y-%m-%d")
        pdf.cell(0, 5, f"Generated on: {current_date}", ln=True)
        pdf.ln(10)
        
        # Outline
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Outline", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        # Split outline into lines and add to PDF
        outline_lines = normalize_text(result["outline"]).split("\n")
        for line in outline_lines:
            # Check for markdown headings (# Heading)
            heading_match = re.match(r'^(#+)\s+(.+)$', line)
            if heading_match:
                # Get heading level (number of #)
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                
                # Apply different formatting based on heading level
                if heading_level == 1:  # H1
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 8, heading_text, ln=True)
                elif heading_level == 2:  # H2
                    pdf.set_font("Arial", "B", 13)
                    pdf.cell(0, 8, heading_text, ln=True)
                else:  # H3 and beyond
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 8, heading_text, ln=True)
                
                pdf.set_font("Arial", "", 12)  # Reset font
            # Check if line is a numbered or Roman numeral heading
            elif re.match(r"^[IVX]+\.|^\d+\.", line.strip()):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, line, ln=True)
                pdf.set_font("Arial", "", 12)
            else:
                pdf.cell(0, 6, line, ln=True)
        
        pdf.ln(10)
        
        # Draft (main content)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Research Paper", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        # Split draft into paragraphs and add to PDF
        paragraphs = re.split(r'\n\s*\n', normalize_text(result["draft"]))
        for paragraph in paragraphs:
            # Check if paragraph is a heading
            lines = paragraph.split("\n")
            for line in lines:
                # Check for markdown headings (# Heading)
                heading_match = re.match(r'^(#+)\s+(.+)$', line)
                if heading_match:
                    # Get heading level (number of #)
                    heading_level = len(heading_match.group(1))
                    heading_text = heading_match.group(2).strip()
                    
                    # Apply different formatting based on heading level
                    if heading_level == 1:  # H1
                        pdf.set_font("Arial", "B", 16)
                        pdf.ln(5)
                        pdf.multi_cell(0, 8, heading_text)
                        pdf.ln(3)
                    elif heading_level == 2:  # H2
                        pdf.set_font("Arial", "B", 14)
                        pdf.ln(4)
                        pdf.multi_cell(0, 8, heading_text)
                        pdf.ln(2)
                    else:  # H3 and beyond
                        pdf.set_font("Arial", "B", 12)
                        pdf.ln(3)
                        pdf.multi_cell(0, 8, heading_text)
                        pdf.ln(2)
                    
                    pdf.set_font("Arial", "", 12)  # Reset font
                # Check for numbered or roman numeral headings
                elif re.match(r"^[IVX]+\.|^\d+\.", line.strip()):
                    pdf.set_font("Arial", "B", 12)
                    pdf.multi_cell(0, 8, line.strip())
                    pdf.ln(2)
                    pdf.set_font("Arial", "", 12)
                else:
                    pdf.multi_cell(0, 6, line)
            pdf.ln(5)
        
        # Sources
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Sources", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 12)
        for i, source in enumerate(result["sources"][:20]):  # Limit to 20 sources
            pdf.multi_cell(0, 6, f"{i+1}. {normalize_text(source)}")
        
        # Generate filename based on topic and date
        safe_topic = re.sub(r'[^\w\s-]', '', result["topic"]).strip().replace(' ', '_')
        
        # Get user's home directory
        home_dir = os.path.expanduser("~")
        # Create a directory for reports if it doesn't exist
        reports_dir = os.path.join(home_dir, "research_papers")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        # Create the full path to the file
        filename = os.path.join(reports_dir, f"research_paper_{safe_topic}_{current_date}.pdf")
        
        # Save PDF
        pdf.output(filename)
        print(f"\nResearch paper saved as PDF: {filename}")
        
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")