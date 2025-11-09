from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Float, Text, Table
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database.dbconnection import Base

class DigitalAsset(Base):
    __tablename__ = "digital_assets"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    file_path = Column(String(500))
    uploaded_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    source_type = Column(String(50))
    embedding_id = Column(String(100))

    tags = relationship("AssetTag", back_populates="asset")


class AssetTag(Base):
    __tablename__ = "asset_tags"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("digital_assets.id"))
    tag = Column(String(100))

    asset = relationship("DigitalAsset", back_populates="tags")