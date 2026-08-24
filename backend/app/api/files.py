from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.db.database import get_db
from app.models.models import FileUpload

router = APIRouter()

@router.get("/{file_id}")
def get_file(file_id: str, db: Session = Depends(get_db)):
    file_record = db.query(FileUpload).filter(FileUpload.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
        
    return StreamingResponse(
        io.BytesIO(file_record.data), 
        media_type=file_record.content_type,
        headers={
            "Content-Disposition": f'inline; filename="{file_record.filename.encode("utf-8").decode("latin-1", "ignore")}"'
        }
    )
