from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.schemas import ChatRequest
from app.db.session import get_db
from app.services.chat_service import answer_question

router = APIRouter()

@router.post("")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    return answer_question(db, scan_run_id=payload.scan_run_id, question=payload.question, include_sql=payload.include_sql)
