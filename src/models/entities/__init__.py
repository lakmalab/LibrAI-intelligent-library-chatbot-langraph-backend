# This file ensures all models are imported and registered properly
from src.models.entities.session import Session
from src.models.entities.conversation import Conversation
from src.models.entities.chat_message import ChatMessage
from src.models.entities.catalog import Author, Publisher, Book
from src.models.entities.chat import StaffRole, Staff, ChatSession, HITLReview
from src.models.entities.events import Event, MaintenanceLog
from src.models.entities.membership import Member, Loan, Fine, Reservation, Review
from src.models.entities.network import Chain, Branch, Section, Shelf
from src.models.entities.rag_assets import DigitalAsset, AssetTag

__all__ = [
    "Session", "Conversation", "ChatMessage",
    "Author", "Publisher", "Book",
    "StaffRole", "Staff", "ChatSession", "HITLReview",
    "Event", "MaintenanceLog",
    "Member", "Loan", "Fine", "Reservation", "Review",
    "Chain", "Branch", "Section", "Shelf",
    "DigitalAsset", "AssetTag"
]