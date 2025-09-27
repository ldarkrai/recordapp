import React, { useState, useEffect } from 'react';
import './App.css';
import { ThemeProvider } from './contexts/ThemeContext';
import ChatSidebar from './components/ChatSidebar';
import ChatView from './components/ChatView';
import { Toaster } from './components/ui/toaster';
import { useToast } from './hooks/use-toast';
import { chatAPI } from './services/api';

function AppContent() {
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const { toast } = useToast();

  // Health check on app start
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      await chatAPI.healthCheck();
      console.log('✅ Backend connection successful');
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      toast({
        title: "Error de conexión",
        description: "No se pudo conectar al servidor backend",
        variant: "destructive",
      });
    }
  };

  const handleChatSelect = (chatId) => {
    setSelectedChatId(chatId);
  };

  const handleChatsUpdate = (updatedChats) => {
    setChats(updatedChats);
  };

  return (
    <div className="h-screen flex bg-background text-foreground">
      <ChatSidebar
        selectedChatId={selectedChatId}
        onChatSelect={handleChatSelect}
        onChatsUpdate={handleChatsUpdate}
      />
      <ChatView 
        selectedChatId={selectedChatId}
        chats={chats}
      />
      <Toaster />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;