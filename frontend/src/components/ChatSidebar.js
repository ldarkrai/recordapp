import React, { useState, useEffect } from 'react';
import { Search, Upload, MoreVertical, Moon, Sun, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { chatAPI } from '../services/api';
import FileUpload from './FileUpload';

const ChatSidebar = ({ selectedChatId, onChatSelect, onChatsUpdate }) => {
  const [chats, setChats] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [showUpload, setShowUpload] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { toast } = useToast();

  // Load chats on component mount
  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      setLoading(true);
      const response = await chatAPI.getChats();
      setChats(response.data);
      
      // Notify parent component about chats update
      if (onChatsUpdate) {
        onChatsUpdate(response.data);
      }
    } catch (error) {
      console.error('Error loading chats:', error);
      toast({
        title: "Error al cargar chats",
        description: "No se pudieron cargar las conversaciones",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredChats = chats.filter(chat =>
    chat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (chat.lastMessage && chat.lastMessage.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' });
    }
  };

  const handleUploadSuccess = (uploadResult) => {
    toast({
      title: "¡Chat importado exitosamente!",
      description: `Se procesaron ${uploadResult.stats.totalMessages} mensajes`,
    });
    
    // Reload chats to show the new one
    loadChats();
    
    // Select the new chat
    if (uploadResult.chatId) {
      onChatSelect(uploadResult.chatId);
    }
  };

  return (
    <>
      <div className="w-80 bg-background border-r border-border flex flex-col h-screen">
        {/* Header */}
        <div className="p-4 bg-muted/50">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">WhatsApp Viewer</h1>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="h-8 w-8 p-0"
              >
                {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowUpload(true)}
                className="h-8 w-8 p-0"
              >
                <Upload className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder="Buscar conversaciones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Cargando chats...</p>
              </div>
            </div>
          ) : filteredChats.length === 0 ? (
            <div className="flex items-center justify-center p-8">
              <div className="text-center">
                <p className="text-muted-foreground mb-4">
                  {chats.length === 0 ? 'No hay chats disponibles' : 'No se encontraron chats'}
                </p>
                {chats.length === 0 && (
                  <Button onClick={() => setShowUpload(true)} variant="outline" size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Importar Chat
                  </Button>
                )}
              </div>
            </div>
          ) : (
            filteredChats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onChatSelect(chat.id)}
                className={`p-3 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors ${
                  selectedChatId === chat.id ? 'bg-muted' : ''
                }`}
              >
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={chat.avatar} alt={chat.name} />
                    <AvatarFallback>
                      {chat.name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium truncate">{chat.name}</h3>
                      <span className="text-xs text-muted-foreground">
                        {formatTime(chat.timestamp)}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-sm text-muted-foreground truncate flex-1">
                        {chat.lastMessage || 'Sin mensajes'}
                      </p>
                      {chat.unreadCount > 0 && (
                        <Badge variant="default" className="ml-2 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center bg-green-500 hover:bg-green-500">
                          {chat.unreadCount}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* File Upload Dialog */}
      <FileUpload
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </>
  );
};

export default ChatSidebar;