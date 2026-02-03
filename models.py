# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class VideoTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    start_time = db.Column(db.Integer)
    status = db.Column(db.String(50), default='processing') # 작업 상태
    ai_subtitles = db.Column(db.Text)   # AI가 다듬은 자막
    ai_narration = db.Column(db.Text)   # AI 나레이션 대본
    created_at = db.Column(db.DateTime, server_default=db.func.now())