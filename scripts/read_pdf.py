import PyPDF2
import sys

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for num, page in enumerate(reader.pages):
                text += f"\n--- PAGE {num+1} ---\n"
                text += page.extract_text()
        with open('pdf_output.txt', 'w', encoding='utf-8') as out:
            out.write(text)
        print("PDF extraction complete.")
    except Exception as e:
        print(f"Error parsing PDF: {e}")

if __name__ == "__main__":
    read_pdf("assignment1.pdf")
