import re
from datetime import datetime
from typing import List, Tuple, Dict, Any
from models import Message, MessageType
import logging

logger = logging.getLogger(__name__)

class WhatsAppParser:
    def __init__(self):
        # Regex patterns for different WhatsApp export formats
        self.patterns = [
            # Format: [15/1/24, 10:00:35] Sender: Message
            r'\[(\d{1,2}\/\d{1,2}\/\d{2,4}),?\s+(\d{1,2}:\d{2}:\d{2})\]\s+([^:]+):\s+(.*)',
            # Format: [15/1/24 10:00:35] Sender: Message  
            r'\[(\d{1,2}\/\d{1,2}\/\d{2,4})\s+(\d{1,2}:\d{2}:\d{2})\]\s+([^:]+):\s+(.*)',
            # Format: 15/1/24, 10:00 - Sender: Message
            r'(\d{1,2}\/\d{1,2}\/\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s+(.*)',
            # Format: 1/15/24, 10:00 AM - Sender: Message (US format)
            r'(\d{1,2}\/\d{1,2}\/\d{2,4}),?\s+(\d{1,2}:\d{2}\s+(?:AM|PM))\s+-\s+([^:]+):\s+(.*)'
        ]
        
    def parse_file(self, file_content: str, chat_id: str) -> Tuple[List[Message], Dict[str, Any]]:
        """
        Parse WhatsApp chat export file and return messages and stats
        """
        lines = file_content.strip().split('\n')
        messages = []
        participants = set()
        date_range = {'from': None, 'to': None}
        
        current_message = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Try to match message pattern
            parsed = self._parse_message_line(line)
            
            if parsed:
                # If we have a previous message being built, save it
                if current_message:
                    messages.append(current_message)
                
                date_str, time_str, sender, content = parsed
                timestamp = self._parse_datetime(date_str, time_str)
                
                if timestamp:
                    # Update date range
                    if not date_range['from'] or timestamp < datetime.fromisoformat(date_range['from']):
                        date_range['from'] = timestamp.isoformat()
                    if not date_range['to'] or timestamp > datetime.fromisoformat(date_range['to']):
                        date_range['to'] = timestamp.isoformat()
                    
                    # Clean sender name
                    sender = sender.strip()
                    participants.add(sender)
                    
                    # Determine message type
                    msg_type = self._determine_message_type(content)
                    
                    # Create new message
                    current_message = Message(
                        chatId=chat_id,
                        sender=sender,
                        content=content,
                        timestamp=timestamp,
                        isMe=self._is_me(sender),
                        type=msg_type,
                        originalLine=line
                    )
                else:
                    logger.warning(f"Could not parse timestamp on line {line_num}: {line}")
            else:
                # This might be a continuation of previous message (multiline)
                if current_message and line:
                    current_message.content += "\n" + line
        
        # Don't forget the last message
        if current_message:
            messages.append(current_message)
        
        stats = {
            'totalMessages': len(messages),
            'participants': list(participants),
            'dateRange': date_range
        }
        
        logger.info(f"Parsed {len(messages)} messages from {len(participants)} participants")
        return messages, stats
    
    def _parse_message_line(self, line: str) -> Tuple[str, str, str, str] | None:
        """
        Try to parse a message line with different regex patterns
        Returns (date, time, sender, content) or None
        """
        for pattern in self.patterns:
            match = re.match(pattern, line)
            if match:
                return match.groups()
        return None
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime | None:
        """
        Parse date and time strings into datetime object
        """
        try:
            # Handle different date formats
            date_formats = [
                "%d/%m/%y",   # 15/1/24
                "%d/%m/%Y",   # 15/1/2024  
                "%m/%d/%y",   # 1/15/24 (US format)
                "%m/%d/%Y"    # 1/15/2024 (US format)
            ]
            
            # Handle different time formats
            time_formats = [
                "%H:%M:%S",      # 10:00:35
                "%H:%M",         # 10:00
                "%I:%M %p",      # 10:00 AM
                "%I:%M:%S %p"    # 10:00:35 AM
            ]
            
            parsed_date = None
            for date_fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, date_fmt).date()
                    break
                except ValueError:
                    continue
            
            if not parsed_date:
                return None
                
            parsed_time = None
            for time_fmt in time_formats:
                try:
                    parsed_time = datetime.strptime(time_str, time_fmt).time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                return None
                
            return datetime.combine(parsed_date, parsed_time)
            
        except Exception as e:
            logger.error(f"Error parsing datetime '{date_str} {time_str}': {e}")
            return None
    
    def _determine_message_type(self, content: str) -> MessageType:
        """
        Determine message type based on content
        """
        content_lower = content.lower()
        
        # Check for media indicators in WhatsApp exports
        if any(indicator in content_lower for indicator in ['<media omitted>', '<multimedia omitido>', 'image omitted', 'video omitted']):
            if 'video' in content_lower:
                return MessageType.VIDEO
            elif 'audio' in content_lower or 'ptt' in content_lower:
                return MessageType.AUDIO
            elif 'document' in content_lower or 'archivo' in content_lower:
                return MessageType.DOCUMENT
            else:
                return MessageType.IMAGE
        
        return MessageType.TEXT
    
    def _is_me(self, sender: str) -> bool:
        """
        Determine if the sender is the user who exported the chat
        Common indicators: "You", "Tú", or phone numbers
        """
        sender_lower = sender.lower().strip()
        me_indicators = ['you', 'tú', 'tu', 'yo']
        
        # Check if sender is "You" or similar
        if sender_lower in me_indicators:
            return True
            
        # Check if sender looks like a phone number (exported by user)
        if re.match(r'^\+?\d+$', sender.strip()):
            return True
            
        return False

    def extract_chat_name(self, file_content: str, participants: List[str]) -> str:
        """
        Extract or generate a chat name
        """
        lines = file_content.strip().split('\n')
        
        # Look for chat name in first few lines
        for line in lines[:5]:
            if 'chat with' in line.lower() or 'conversación con' in line.lower():
                # Extract name after "chat with" or similar
                parts = re.split(r'chat with|conversación con', line, flags=re.IGNORECASE)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # Generate name based on participants
        if len(participants) == 1:
            return participants[0]
        elif len(participants) == 2:
            non_me_participants = [p for p in participants if not self._is_me(p)]
            if non_me_participants:
                return non_me_participants[0]
            return participants[0]
        else:
            # Group chat - use first few participants
            non_me_participants = [p for p in participants if not self._is_me(p)][:3]
            if non_me_participants:
                return f"Grupo: {', '.join(non_me_participants)}"
            return f"Grupo de {len(participants)} personas"