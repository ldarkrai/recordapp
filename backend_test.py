#!/usr/bin/env python3
"""
Backend Test Suite for WhatsApp Viewer API
Tests all backend endpoints with realistic WhatsApp chat data
"""

import requests
import json
import os
from io import BytesIO
import time

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://whatsapp-viewer-6.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class WhatsAppViewerTester:
    def __init__(self):
        self.session = requests.Session()
        self.chat_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
        
    def test_health_check(self):
        """Test 1: API Health Check - GET /api/"""
        try:
            response = self.session.get(f"{API_BASE}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "WhatsApp Viewer API" in data["message"]:
                    self.log_test("Health Check", True, "API is running correctly")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response format: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_empty_chats_list(self):
        """Test 2: List empty chats - GET /api/chats"""
        try:
            response = self.session.get(f"{API_BASE}/chats")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Empty Chats List", True, f"Returned empty array with {len(data)} chats")
                    return True
                else:
                    self.log_test("Empty Chats List", False, f"Expected array, got: {type(data)}")
                    return False
            else:
                self.log_test("Empty Chats List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Empty Chats List", False, f"Request error: {str(e)}")
            return False
    
    def create_whatsapp_chat_file(self):
        """Create a realistic WhatsApp chat file for testing"""
        chat_content = """[15/1/24, 10:00:35] Mamá: Hola familia, ¿cómo están todos?
[15/1/24, 10:05:12] Yo: ¡Hola mamá! Todo bien por aquí
[15/1/24, 10:10:25] Papá: Todo perfecto, trabajando desde casa hoy
[15/1/24, 10:15:30] Mamá: Me alegra saber que están bien
[15/1/24, 10:20:45] Ana: ¡Buenos días familia! Recién me levanto 😴
[15/1/24, 10:25:15] Yo: Jajaja Ana siempre la dormilona
[15/1/24, 10:30:20] Papá: Ana, no olvides que hoy tenemos reunión familiar
[15/1/24, 18:30:00] Mamá: Recuerden que mañana es la cena familiar
[15/1/24, 18:35:12] Ana: ¡Por supuesto! ¿A qué hora?
[15/1/24, 18:40:25] Mamá: A las 7:00 PM como siempre
[15/1/24, 18:45:30] Yo: Perfecto, ahí estaremos
[15/1/24, 18:50:15] Papá: Excelente, nos vemos mañana entonces
[15/1/24, 19:00:00] Mamá: Los amo mucho familia ❤️
[15/1/24, 19:05:10] Ana: Nosotros también te amamos mamá 💕
[15/1/24, 19:10:20] Yo: ¡La mejor familia del mundo! 🥰"""
        
        return chat_content.encode('utf-8')
    
    def test_upload_chat_file(self):
        """Test 3: Upload WhatsApp chat file - POST /api/upload-chat"""
        try:
            # Create test file
            file_content = self.create_whatsapp_chat_file()
            
            # Prepare multipart form data
            files = {
                'file': ('familia_chat.txt', BytesIO(file_content), 'text/plain')
            }
            
            response = self.session.post(f"{API_BASE}/upload-chat", files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['success', 'chatId', 'message', 'stats']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Upload Chat File", False, f"Missing fields: {missing_fields}")
                    return False
                
                if data['success'] and data['chatId']:
                    self.chat_id = data['chatId']  # Store for later tests
                    stats = data['stats']
                    
                    # Validate stats
                    if (stats.get('totalMessages', 0) > 0 and 
                        len(stats.get('participants', [])) > 0):
                        
                        self.log_test("Upload Chat File", True, 
                                    f"Chat uploaded successfully. ID: {self.chat_id}, "
                                    f"Messages: {stats['totalMessages']}, "
                                    f"Participants: {len(stats['participants'])}")
                        return True
                    else:
                        self.log_test("Upload Chat File", False, f"Invalid stats: {stats}")
                        return False
                else:
                    self.log_test("Upload Chat File", False, f"Upload failed: {data}")
                    return False
            else:
                self.log_test("Upload Chat File", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Upload Chat File", False, f"Upload error: {str(e)}")
            return False
    
    def test_chats_after_upload(self):
        """Test 4: Verify chat appears in list after upload - GET /api/chats"""
        try:
            response = self.session.get(f"{API_BASE}/chats")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    # Find our uploaded chat
                    uploaded_chat = None
                    for chat in data:
                        if chat.get('id') == self.chat_id:
                            uploaded_chat = chat
                            break
                    
                    if uploaded_chat:
                        # Validate chat structure
                        required_fields = ['id', 'name', 'participantCount']
                        missing_fields = [field for field in required_fields if field not in uploaded_chat]
                        
                        if missing_fields:
                            self.log_test("Chats After Upload", False, f"Missing chat fields: {missing_fields}")
                            return False
                        
                        self.log_test("Chats After Upload", True, 
                                    f"Chat found in list: '{uploaded_chat['name']}' "
                                    f"with {uploaded_chat['participantCount']} participants")
                        return True
                    else:
                        self.log_test("Chats After Upload", False, f"Uploaded chat not found in list")
                        return False
                else:
                    self.log_test("Chats After Upload", False, f"Expected non-empty array, got: {data}")
                    return False
            else:
                self.log_test("Chats After Upload", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Chats After Upload", False, f"Request error: {str(e)}")
            return False
    
    def test_get_messages(self):
        """Test 5: Get messages from uploaded chat - GET /api/chats/{chat_id}/messages"""
        if not self.chat_id:
            self.log_test("Get Messages", False, "No chat_id available (upload test failed)")
            return False
            
        try:
            response = self.session.get(f"{API_BASE}/chats/{self.chat_id}/messages")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'messages' not in data or 'pagination' not in data:
                    self.log_test("Get Messages", False, f"Invalid response structure: {data.keys()}")
                    return False
                
                messages = data['messages']
                pagination = data['pagination']
                
                if len(messages) > 0:
                    # Validate first message structure
                    first_msg = messages[0]
                    required_fields = ['id', 'chatId', 'sender', 'message', 'timestamp', 'isMe', 'type']
                    missing_fields = [field for field in required_fields if field not in first_msg]
                    
                    if missing_fields:
                        self.log_test("Get Messages", False, f"Missing message fields: {missing_fields}")
                        return False
                    
                    # Validate pagination
                    pagination_fields = ['page', 'totalPages', 'hasMore', 'total']
                    missing_pagination = [field for field in pagination_fields if field not in pagination]
                    
                    if missing_pagination:
                        self.log_test("Get Messages", False, f"Missing pagination fields: {missing_pagination}")
                        return False
                    
                    # Check if messages were parsed correctly
                    family_senders = ['Mamá', 'Yo', 'Papá', 'Ana']
                    parsed_senders = set(msg['sender'] for msg in messages)
                    
                    if any(sender in parsed_senders for sender in family_senders):
                        self.log_test("Get Messages", True, 
                                    f"Retrieved {len(messages)} messages correctly parsed. "
                                    f"Senders: {list(parsed_senders)}")
                        return True
                    else:
                        self.log_test("Get Messages", False, 
                                    f"Messages not parsed correctly. Senders: {list(parsed_senders)}")
                        return False
                else:
                    self.log_test("Get Messages", False, "No messages found in chat")
                    return False
            else:
                self.log_test("Get Messages", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Messages", False, f"Request error: {str(e)}")
            return False
    
    def test_delete_chat(self):
        """Test 6: Delete chat - DELETE /api/chats/{chat_id}"""
        if not self.chat_id:
            self.log_test("Delete Chat", False, "No chat_id available (upload test failed)")
            return False
            
        try:
            response = self.session.delete(f"{API_BASE}/chats/{self.chat_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'deleted successfully' in data.get('message', '').lower():
                    self.log_test("Delete Chat", True, "Chat deleted successfully")
                    
                    # Verify chat is actually deleted by checking chats list
                    time.sleep(1)  # Brief pause to ensure deletion is processed
                    verify_response = self.session.get(f"{API_BASE}/chats")
                    
                    if verify_response.status_code == 200:
                        chats = verify_response.json()
                        deleted_chat_exists = any(chat.get('id') == self.chat_id for chat in chats)
                        
                        if not deleted_chat_exists:
                            self.log_test("Delete Chat Verification", True, "Chat successfully removed from list")
                            return True
                        else:
                            self.log_test("Delete Chat Verification", False, "Chat still appears in list after deletion")
                            return False
                    else:
                        self.log_test("Delete Chat Verification", False, "Could not verify deletion")
                        return False
                else:
                    self.log_test("Delete Chat", False, f"Deletion failed: {data}")
                    return False
            else:
                self.log_test("Delete Chat", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Chat", False, f"Request error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print(f"🚀 Starting WhatsApp Viewer Backend Tests")
        print(f"📡 Testing API at: {API_BASE}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_empty_chats_list,
            self.test_upload_chat_file,
            self.test_chats_after_upload,
            self.test_get_messages,
            self.test_delete_chat
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests PASSED! Backend is working correctly.")
        else:
            print(f"⚠️  {total - passed} tests FAILED. Check the details above.")
            
        return passed == total

def main():
    """Main test execution"""
    print("WhatsApp Viewer Backend Test Suite")
    print("=" * 60)
    
    tester = WhatsAppViewerTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())