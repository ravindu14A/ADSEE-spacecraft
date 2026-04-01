import sys

def read_pdf(file_path):
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except ImportError:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            return "ERROR: Neither PyMuPDF nor PyPDF2 is installed."

if __name__ == "__main__":
    report_text = read_pdf('ADSEE_Aircraft.pdf')
    with open('report_text.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
        
    tutorial_text = read_pdf('AE3211-I  Aircraft Homework Tutorial - 2026 Regular Session (1).pdf')
    with open('tutorial_text.txt', 'w', encoding='utf-8') as f:
        f.write(tutorial_text)
        
    print("PDFs extracted successfully.")
