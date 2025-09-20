import PyPDF2
import docx
import os
from typing import Dict, List, Any
import aiofiles

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and extract text content"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            filename = os.path.basename(file_path)
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if file_extension == '.pdf':
                return await self._process_pdf(file_path, filename)
            elif file_extension == '.docx':
                return await self._process_docx(file_path, filename)
            elif file_extension == '.txt':
                return await self._process_txt(file_path, filename)
            
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            raise
    
    async def _process_pdf(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process PDF document"""
        pages = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        pages.append({
                            "page_number": page_num + 1,
                            "content": text.strip(),
                            "word_count": len(text.split())
                        })
                    print(text)
                except Exception as e:
                    print(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
        
        return {
            "filename": filename,
            "type": "pdf",
            "total_pages": len(pages),
            "pages": pages,
            "total_words": sum(page["word_count"] for page in pages)
        }
    
    async def _process_docx(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process DOCX document"""
        pages = []
        
        try:
            doc = docx.Document(file_path)
            
            # DOCX doesn't have explicit pages, so we'll split by paragraphs
            # and group them into logical "pages"
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Group paragraphs into pages (roughly 500 words per page)
            current_page = []
            current_word_count = 0
            page_num = 1
            
            for paragraph in paragraphs:
                word_count = len(paragraph.split())
                
                if current_word_count + word_count > 500 and current_page:
                    # Start new page
                    pages.append({
                        "page_number": page_num,
                        "content": "\n".join(current_page),
                        "word_count": current_word_count
                    })
                    current_page = [paragraph]
                    current_word_count = word_count
                    page_num += 1
                else:
                    current_page.append(paragraph)
                    current_word_count += word_count
            
            # Add the last page
            if current_page:
                pages.append({
                    "page_number": page_num,
                    "content": "\n".join(current_page),
                    "word_count": current_word_count
                })
        
        except Exception as e:
            print(f"Error processing DOCX file: {e}")
            raise
        
        return {
            "filename": filename,
            "type": "docx",
            "total_pages": len(pages),
            "pages": pages,
            "total_words": sum(page["word_count"] for page in pages)
        }
    
    async def _process_txt(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Process TXT document"""
        pages = []
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            
            # Split text into pages (roughly 500 words per page)
            words = content.split()
            words_per_page = 500
            
            for i in range(0, len(words), words_per_page):
                page_words = words[i:i + words_per_page]
                page_content = " ".join(page_words)
                
                pages.append({
                    "page_number": (i // words_per_page) + 1,
                    "content": page_content,
                    "word_count": len(page_words)
                })
        
        except Exception as e:
            print(f"Error processing TXT file: {e}")
            raise
        
        return {
            "filename": filename,
            "type": "txt",
            "total_pages": len(pages),
            "pages": pages,
            "total_words": sum(page["word_count"] for page in pages)
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.supported_formats

