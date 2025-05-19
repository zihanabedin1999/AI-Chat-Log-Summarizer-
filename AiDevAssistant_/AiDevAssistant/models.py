from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatAnalysis(db.Model):
    __tablename__ = 'chat_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    total_messages = db.Column(db.Integer, nullable=False)
    user_message_count = db.Column(db.Integer, nullable=False)
    ai_message_count = db.Column(db.Integer, nullable=False)
    exchanges = db.Column(db.Integer, nullable=False)
    conversation_nature = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Store the keywords as a relationship
    keywords = db.relationship('Keyword', backref='analysis', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ChatAnalysis {self.filename} - {self.created_at}>'
    
    @property
    def formatted_date(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'total_messages': self.total_messages,
            'user_message_count': self.user_message_count,
            'ai_message_count': self.ai_message_count,
            'exchanges': self.exchanges,
            'conversation_nature': self.conversation_nature,
            'keywords': [keyword.word for keyword in self.keywords],
            'created_at': self.formatted_date
        }
    
    # Helper method to create from analysis results
    @classmethod
    def from_analysis_results(cls, filename, results):
        analysis = cls(
            filename=filename,
            total_messages=results['total_messages'],
            user_message_count=results['user_message_count'],
            ai_message_count=results['ai_message_count'],
            exchanges=results['exchanges'],
            conversation_nature=results['conversation_nature']
        )
        return analysis

class Keyword(db.Model):
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('chat_analyses.id'), nullable=False)
    
    def __repr__(self):
        return f'<Keyword {self.word}>'