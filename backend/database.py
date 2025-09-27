from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
import os
from models import Chat, Message, ChatCreate, MessageCreate
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.chats_collection = db.chats
        self.messages_collection = db.messages
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Chat indexes
            await self.chats_collection.create_index([("updatedAt", DESCENDING)])
            
            # Message indexes  
            await self.messages_collection.create_index([
                ("chatId", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            await self.messages_collection.create_index([("timestamp", DESCENDING)])
            await self.messages_collection.create_index([("chatId", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # Chat operations
    async def create_chat(self, chat_data: ChatCreate) -> Chat:
        """Create a new chat"""
        chat = Chat(**chat_data.dict())
        chat.avatar = self._generate_avatar_url(chat.name)
        
        result = await self.chats_collection.insert_one(chat.dict())
        chat.id = str(result.inserted_id)
        
        logger.info(f"Created chat: {chat.name} with ID: {chat.id}")
        return chat
    
    async def get_chats(self) -> List[Chat]:
        """Get all chats ordered by last update"""
        cursor = self.chats_collection.find().sort("updatedAt", DESCENDING)
        chats_data = await cursor.to_list(length=None)
        
        chats = []
        for chat_data in chats_data:
            chat_data['id'] = str(chat_data.pop('_id'))
            chats.append(Chat(**chat_data))
        
        return chats
    
    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get a specific chat by ID"""
        try:
            from bson import ObjectId
            chat_data = await self.chats_collection.find_one({"_id": ObjectId(chat_id)})
            
            if chat_data:
                chat_data['id'] = str(chat_data.pop('_id'))
                return Chat(**chat_data)
            return None
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    async def update_chat_last_message(self, chat_id: str, last_message: Dict[str, Any]):
        """Update the last message of a chat"""
        try:
            from bson import ObjectId
            await self.chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "lastMessage": last_message,
                        "updatedAt": datetime.utcnow()
                    },
                    "$inc": {"messageCount": 1}
                }
            )
        except Exception as e:
            logger.error(f"Error updating chat last message: {e}")
    
    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all its messages"""
        try:
            from bson import ObjectId
            
            # Delete all messages first
            await self.messages_collection.delete_many({"chatId": chat_id})
            
            # Delete the chat
            result = await self.chats_collection.delete_one({"_id": ObjectId(chat_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted chat {chat_id} and its messages")
            
            return success
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return False
    
    # Message operations
    async def create_message(self, message_data: MessageCreate) -> Message:
        """Create a new message"""
        message = Message(**message_data.dict())
        
        result = await self.messages_collection.insert_one(message.dict())
        message.id = str(result.inserted_id)
        
        return message
    
    async def bulk_create_messages(self, messages: List[Message], chat_id: str) -> int:
        """Bulk create messages for better performance"""
        try:
            if not messages:
                return 0
                
            # Convert messages to dict format for insertion
            message_docs = [msg.dict() for msg in messages]
            
            # Insert all messages
            result = await self.messages_collection.insert_many(message_docs)
            inserted_count = len(result.inserted_ids)
            
            # Update chat with last message info
            if messages:
                last_msg = max(messages, key=lambda m: m.timestamp)
                await self.update_chat_last_message(chat_id, {
                    "content": last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content,
                    "timestamp": last_msg.timestamp,
                    "sender": last_msg.sender
                })
                
                # Update message count
                from bson import ObjectId
                await self.chats_collection.update_one(
                    {"_id": ObjectId(chat_id)},
                    {"$set": {"messageCount": inserted_count}}
                )
            
            logger.info(f"Bulk created {inserted_count} messages for chat {chat_id}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error bulk creating messages: {e}")
            return 0
    
    async def get_messages(self, chat_id: str, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get paginated messages for a chat"""
        try:
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.messages_collection.count_documents({"chatId": chat_id})
            
            # Get messages with pagination
            cursor = self.messages_collection.find({"chatId": chat_id}).sort("timestamp", ASCENDING).skip(skip).limit(limit)
            messages_data = await cursor.to_list(length=limit)
            
            messages = []
            for msg_data in messages_data:
                msg_data['id'] = str(msg_data.pop('_id'))
                messages.append(Message(**msg_data))
            
            # Calculate pagination info
            total_pages = math.ceil(total / limit) if total > 0 else 1
            has_more = page < total_pages
            
            return {
                "messages": messages,
                "pagination": {
                    "page": page,
                    "totalPages": total_pages,
                    "hasMore": has_more,
                    "total": total
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return {
                "messages": [],
                "pagination": {
                    "page": page,
                    "totalPages": 1,
                    "hasMore": False,
                    "total": 0
                }
            }
    
    def _generate_avatar_url(self, name: str) -> str:
        """Generate avatar URL using the name as seed"""
        import urllib.parse
        seed = urllib.parse.quote(name.lower().replace(' ', ''))
        return f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}"