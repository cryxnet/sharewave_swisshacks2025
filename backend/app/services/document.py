#app/services/document.py
import os
from fastapi import UploadFile
from app.config import settings
from app.models.schemas import UploadedDocument, DocumentType

class DocumentService:
    @staticmethod
    async def save_document(file: UploadFile, doc_type: DocumentType) -> UploadedDocument:
        content = await file.read()
        
        # Save to uploads directory
        filename = f"{doc_type}_{file.filename}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        return UploadedDocument(
            filename=filename,
            doc_type=doc_type,
            content=content.decode()
        )