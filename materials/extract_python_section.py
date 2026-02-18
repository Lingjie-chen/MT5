import PyPDF2
import sys

def extract_pages(pdf_path, output_path, start_page, end_page):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"Total pages: {num_pages}")
            
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for i in range(start_page - 1, min(num_pages, end_page)):
                    page = reader.pages[i]
                    text = page.extract_text()
                    out_file.write(f"--- Page {i+1} ---\n")
                    out_file.write(text)
                    out_file.write("\n\n")
            print(f"Extracted pages {start_page} to {end_page} to {output_path}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_pages('/Users/lenovo/tmp/mql5book.pdf', 'mql5book_python.txt', 1990, 2047)
