import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Try 3 methods in order: pymupdf (best), pdfplumber, PyPDF2.
    Works with government PDFs, complex layouts, and most UGC/AICTE files.
    """
    file_bytes = uploaded_file.read()

    
    try:
        import fitz  
        doc = fitz.open(stream=file_bytes, filetype='pdf')
        pages = []
        for page in doc:
            text = page.get_text()
            if text and text.strip():
                pages.append(text.strip())
        doc.close()
        result = '\n\n'.join(pages).strip()
        if result and len(result) > 50:
            return result
    except Exception:
        pass

    
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text and text.strip():
                    pages.append(text.strip())
        result = '\n\n'.join(pages).strip()
        if result and len(result) > 50:
            return result
    except Exception:
        pass

    
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
        result = '\n\n'.join(pages).strip()
        if result and len(result) > 50:
            return result
    except Exception:
        pass

    return ''
