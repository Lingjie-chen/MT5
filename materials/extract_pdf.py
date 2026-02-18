import PyPDF2
import sys

def extract_text_from_pdf(pdf_path, output_path, max_pages=30):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"Total pages: {num_pages}")
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for i in range(min(num_pages, max_pages)):
                    page = reader.pages[i]
                    text = page.extract_text()
                    out_file.write(f"--- Page {i+1} ---\n")
                    out_file.write(text)
                    out_file.write("\n\n")
            print(f"Extracted first {max_pages} pages to {output_path}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_text_from_pdf('/Users/lenovo/tmp/mql5book.pdf', 'mql5book_toc.txt')
