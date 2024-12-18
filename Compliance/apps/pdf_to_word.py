import PyPDF2
from docx import Document

def convert_pdf_to_word(pdf_file_path, word_file_path):
    """
    Convert a PDF file to a Word document.

    :param pdf_file_path: The path to the input PDF file.
    :param word_file_path: The path where the output Word document will be saved.
    """
    # Read the PDF file
    pdf_file = open(pdf_file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)  # Updated to use PdfReader

    # Create a new Word document
    word_document = Document()

    # Iterate through each page of the PDF
    for page in pdf_reader.pages:  # Updated to use .pages
        text = page.extract_text()  # Updated to use extract_text()

        # Add the text to the Word document
        word_document.add_paragraph(text)

    # Save the Word document
    word_document.save(word_file_path)

    # Close the PDF file
    pdf_file.close()

# Example usage:
pdf_path  = 'C:/Prudential/Code/PROUD_Automation/Different_client_input/usecase_two/AR1 1.pdf'
word_path  = 'C:/Prudential/Code/PROUD_Automation/Different_client_input/usecase_two/AR1 1.docx'
# ret_val = convert_pdf_to_word(pdf_path, word_path)
# print(ret_val)