from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Import our custom modules
from models import (
    Chat, ChatCreate, ChatResponse, Message, MessageResponse, 
    MessagesResponse, UploadResponse, ChatStats
)
from database import DatabaseManager
from whatsapp_parser import WhatsAppParser

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize database manager and parser
db_manager = DatabaseManager(db)
whatsapp_parser = WhatsAppParser()

# Create the main app without a prefix
app = FastAPI(title="WhatsApp Viewer API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Startup event to create indexes
@app.on_event("startup")
async def startup_event():
    await db_manager.create_indexes()
    logger.info("WhatsApp Viewer API started successfully")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "WhatsApp Viewer API is running"}

@api_router.get("/chats", response_model=List[ChatResponse])
async def get_chats():
    """Get all chats"""
    try:
        chats = await db_manager.get_chats()
        
        chat_responses = []
        for chat in chats:
            chat_resp = ChatResponse(
                id=chat.id,
                name=chat.name,
                lastMessage=chat.lastMessage.content if chat.lastMessage else None,
                timestamp=chat.lastMessage.timestamp.isoformat() if chat.lastMessage else chat.updatedAt.isoformat(),
                unreadCount=chat.unreadCount,
                avatar=chat.avatar,
                participantCount=len(chat.participants)
            )
            chat_responses.append(chat_resp)
            
        return chat_responses
    except Exception as e:
        logger.error(f"Error getting chats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chats")

@api_router.get("/chats/{chat_id}/messages", response_model=MessagesResponse)
async def get_chat_messages(
    chat_id: str, 
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """Get messages for a specific chat with pagination"""
    try:
        result = await db_manager.get_messages(chat_id, page, limit)
        
        message_responses = []
        for msg in result["messages"]:
            msg_resp = MessageResponse(
                id=msg.id,
                chatId=msg.chatId,
                sender=msg.sender,
                message=msg.content,
                timestamp=msg.timestamp.isoformat(),
                isMe=msg.isMe,
                type=msg.type.value,
                mediaUrl=msg.mediaPath
            )
            message_responses.append(msg_resp)
        
        return MessagesResponse(
            messages=message_responses,
            pagination=result["pagination"]
        )
        
    except Exception as e:
        logger.error(f"Error getting messages for chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving messages")

@api_router.post("/upload-chat", response_model=UploadResponse)
async def upload_chat_file(file: UploadFile = File(...)):
    """Upload and process WhatsApp chat export file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.txt', '.zip')):
            raise HTTPException(
                status_code=400, 
                detail="Only .txt and .zip files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Handle encoding
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                file_content = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Could not decode file. Please ensure it's a valid text file."
                )
        
        # Parse the chat file
        messages, stats = whatsapp_parser.parse_file(file_content, "temp_id")
        
        if not messages:
            raise HTTPException(
                status_code=400,
                detail="No messages found in the file. Please check the file format."
            )
        
        # Extract chat name
        chat_name = whatsapp_parser.extract_chat_name(file_content, stats['participants'])
        
        # Create chat
        chat_create = ChatCreate(
            name=chat_name,
            participants=stats['participants']
        )
        chat = await db_manager.create_chat(chat_create)
        
        # Update messages with correct chat_id
        for msg in messages:
            msg.chatId = chat.id
        
        # Bulk insert messages
        inserted_count = await db_manager.bulk_create_messages(messages, chat.id)
        
        # Prepare response
        response_stats = ChatStats(
            totalMessages=stats['totalMessages'],
            participants=stats['participants'],
            dateRange=stats['dateRange']
        )
        
        return UploadResponse(
            success=True,
            chatId=chat.id,
            message=f"Chat '{chat_name}' processed successfully with {inserted_count} messages",
            stats=response_stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@api_router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and all its messages"""
    try:
        success = await db_manager.delete_chat(chat_id)
        
        if success:
            return {"success": True, "message": "Chat deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Chat not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting chat")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
