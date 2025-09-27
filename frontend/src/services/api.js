import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const chatAPI = {
  // Get all chats
  getChats: () => api.get('/chats'),
  
  // Get messages for a specific chat with pagination
  getMessages: (chatId, page = 1, limit = 50) => 
    api.get(`/chats/${chatId}/messages?page=${page}&limit=${limit}`),
  
  // Upload WhatsApp chat file
  uploadChatFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/upload-chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // Longer timeout for file uploads
    });
  },
  
  // Delete a chat
  deleteChat: (chatId) => api.delete(`/chats/${chatId}`),
  
  // Health check
  healthCheck: () => api.get('/'),
};

export default chatAPI;