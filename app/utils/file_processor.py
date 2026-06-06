import os
import csv
from typing import Tuple
from pathlib import Path
import PyPDF2
from docx import Document


class FileProcessor:
    """Utility class for processing uploaded files"""
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from a .txt file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    @staticmethod
    def extract_text_from_csv(file_path: str) -> str:
        """Extract text from a .csv file"""
        text_content = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                text_content.append(' '.join(row))
        return '\n'.join(text_content)
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a .pdf file"""
        text_content = []
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
        return '\n'.join(text_content)
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from a .docx file"""
        try:
            doc = Document(file_path)
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            return '\n'.join(text_content)
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, str]:
        """
        Extract text from a file based on its extension
        Returns: (extracted_text, file_type)
        """
        file_extension = Path(file_path).suffix.lower()
        
        extractors = {
            '.txt': FileProcessor.extract_text_from_txt,
            '.csv': FileProcessor.extract_text_from_csv,
            '.pdf': FileProcessor.extract_text_from_pdf,
            '.docx': FileProcessor.extract_text_from_docx,
        }
        
        extractor = extractors.get(file_extension)
        if not extractor:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        text = extractor(file_path)
        return text, file_extension[1:]  # Remove the dot from extension

# Made with Bob
