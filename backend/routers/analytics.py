from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import DetectionRecord

router = APIRouter()

@router.get("/history")
def get_history_limit(db: Session = Depends(get_db)):
    """返回最近 10 条"""
    return db.query(DetectionRecord).order_by(DetectionRecord.id.desc()).limit(10).all()

@router.get("/analytics")
def get_analytics_all(db: Session = Depends(get_db)):
    """返回所有数据用于大屏分析"""
    return db.query(DetectionRecord).all()