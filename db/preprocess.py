from db.extract import daconCustomExtractor
from langchain.schema import Document
import fitz  # PyMuPDF

def process_pdf(file_path):
    # 1.Extract pages from the PDF
    doc = fitz.open(file_path)
    chunk_temp = []
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        
        #2. Extract tables per page 
        tables = page.find_tables()
        raw_text_list = []
        for table in tables:
            #Calculate the bounding box surrounding the table
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')
            
            for cell in table.cells:
                x0, y0, x1, y1 = cell[:4]  #Extract cell coordinates
                min_x = min(min_x, x0)
                min_y = min(min_y, y0)
                max_x = max(max_x, x1)
                max_y = max(max_y, y1)
            #1) Bounding box of the detected table
            table_rect = fitz.Rect(min_x, min_y, max_x, max_y)
            #2) Table text in structured (row/column) format
            table_text = "\n"
            for row in table.extract():
                table_text += str(row)
                table_text += "\n"
            #3) Raw text inside the detected table area
            clipped_text = page.get_text("text", clip=table_rect)
            
            #4) Replace raw text with structured table text
            raw_text_list.append((clipped_text, table_text))
            
        #2. Extract images per page       
        extractor = daconCustomExtractor(page)
        bboxes = extractor.detect_svg_contours(page_number+1, min_svg_gap_dx=25.0, min_svg_gap_dy=25.0, min_w=2.0, min_h=2.0)

                
        #3. Extract text per image/section
        for i, bbox in enumerate(bboxes):
            x0, y0, x1, y1 = bbox 
            
            full_text = page.get_text("text", clip=fitz.Rect(x0, y0, x1, y1))
            for clipped_text, table_text in raw_text_list:
                if clipped_text in full_text:
                    full_text = full_text.replace(clipped_text, table_text)
                    
            chunk_temp.append(full_text)
            
    #Wrap extracted text chunks into LangChain Document objects        
    chunks = [Document(page_content=t) for t in chunk_temp]
    return chunks