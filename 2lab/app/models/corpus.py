from sqlalchemy import Column, Integer, String, Text
from app.models import Base

class Corpus(Base):
    __tablename__ = "corpuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    text = Column(Text, nullable=False)
