import PyPDF2
import sys

def search_pdf(pdf_path, keyword):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            print(f"Searching for '{keyword}' in {num_pages} pages...")
            
            found_count = 0
            for i in range(num_pages):
                try:
                    page = reader.pages[i]
                    text = page.extract_text()
                    if keyword.lower() in text.lower():
                        print(f"--- Found in Page {i+1} ---")
                        # Print a snippet around the keyword
                        lower_text = text.lower()
                        start_idx = lower_text.find(keyword.lower())
                        snippet_start = max(0, start_idx - 100)
                        snippet_end = min(len(text), start_idx + 300)
                        print(text[snippet_start:snippet_end].replace('\n', ' '))
                        print("...\n")
                        found_count += 1
                        if found_count >= 5: # Limit to first 5 matches to avoid huge output
                             print("Found 5 matches, stopping search.")
                             break
                except Exception as e:
                    # ignore page extraction errors
                    pass
            
            if found_count == 0:
                print(f"Keyword '{keyword}' not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_pdf('/Users/lenovo/tmp/mql5book.pdf', 'Python')
