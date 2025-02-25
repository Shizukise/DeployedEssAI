import fitz  

# Standard dimensions in points for A-series paper sizes
PAPER_SIZES = {
    "A4": (595, 842),
    "A3": (842, 1191),
    "A2": (1191, 1684),
    "A1": (1684, 2384),
    "A0": (2384, 3370)
}

PLAN_TYPES = set(["INTERVENTION", "EVACUATION", "CONSIGNE DE CHAMBRE"])

class FileOperator:
    """Class to call for file operation methods"""

    def get_format(self, filepath):
        """
            input : PDF file
            output : str - Format
            This works on a single file to retrieve its format 
        """
        try:
            # Open the PDF file
            pdf_document = fitz.open(filepath)
            page_formats = []

            # Iterate through each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                width, height = page.rect.width, page.rect.height
                matched_format = "Unknown"

                # Compare dimensions to standard paper sizes
                for paper_name, (w, h) in PAPER_SIZES.items():
                    if (round(width), round(height)) == (w, h) or (round(height), round(width)) == (w, h):
                        matched_format = paper_name
                        break

                page_formats.append(f"{matched_format}")
            
            pdf_document.close()
            return page_formats[0]
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def get_type(self,filepath):
        
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            for type in PLAN_TYPES:
                text_instances = page.search_for(type)
                for _ in text_instances:
                    return type
        doc.close()

    
    