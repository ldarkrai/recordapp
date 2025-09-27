from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image" 
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

class ChatStats(BaseModel):
    totalMessages: int
    participants: List[str]
    dateRange: Dict[str, str]

class UploadResponse(BaseModel):
    success: bool
    chatId: str
    message: str
    stats: ChatStats

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chatId: str
    sender: str
    content: str
    timestamp: datetime
    isMe: bool
    type: MessageType = MessageType.TEXT
    mediaPath: Optional[str] = None
    originalLine: Optional[str] = None

class MessageCreate(BaseModel):
    chatId: str
    sender: str
    content: str
    timestamp: datetime
    isMe: bool
    type: MessageType = MessageType.TEXT
    mediaPath: Optional[str] = None
    originalLine: Optional[str] = None

class LastMessage(BaseModel):
    content: str
    timestamp: datetime
    sender: str

class Chat(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    participants: List[str]
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastMessage: Optional[LastMessage] = None
    messageCount: int = 0
    unreadCount: int = 0
    avatar: Optional[str] = None

class ChatCreate(BaseModel):
    name: str
    participants: List[str]

class ChatResponse(BaseModel):
    id: str
    name: str
    lastMessage: Optional[str] = None
    timestamp: Optional[str] = None
    unreadCount: int = 0
    avatar: Optional[str] = None
    participantCount: int = 0

class MessageResponse(BaseModel):
    id: str
    chatId: str
    sender: str
    message: str
    timestamp: str
    isMe: bool
    type: str
    mediaUrl: Optional[str] = None

class PaginationInfo(BaseModel):
    page: int
    totalPages: int
    hasMore: bool
    total: int

class MessagesResponse(BaseModel):
    messages: List[MessageResponse]
    pagination: PaginationInfo