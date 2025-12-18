from pdf2docx import Converter
from docx import Document

def pdf_to_docx(input_path, output_path):
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

def txt_to_docx(input_path, output_path):
    doc = Document()
    with open(input_path) as f:
        doc.add_paragraph(f.read())
    doc.save(output_path)