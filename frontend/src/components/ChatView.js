import React, { useState, useEffect, useRef } from 'react';
import { MoreVertical, Search, Phone, Video, Loader2, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { Alert, AlertDescription } from './ui/alert';
import { chatAPI } from '../services/api';

const ChatView = ({ selectedChatId, chats }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({});
  const messagesEndRef = useRef(null);

  // Load messages when chat is selected
  useEffect(() => {
    if (selectedChatId) {
      loadMessages(selectedChatId);
    }
  }, [selectedChatId]);

  // Auto-scroll to bottom when new messages load
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async (chatId, page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatAPI.getMessages(chatId, page);
      const { messages: newMessages, pagination: paginationInfo } = response.data;
      
      if (page === 1) {
        setMessages(newMessages);
      } else {
        // For future pagination support
        setMessages(prev => [...prev, ...newMessages]);
      }
      
      setPagination(paginationInfo);
      
    } catch (error) {
      console.error('Error loading messages:', error);
      setError('Error al cargar los mensajes');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedChatId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-64 h-64 mx-auto mb-8 opacity-20">
            <svg viewBox="0 0 303 172" className="w-full h-full">
              <defs>
                <linearGradient id="intro-phone" x1="50%" x2="50%" y1="0%" y2="100%">
                  <stop offset="0%" stopColor="#5BD066"></stop>
                  <stop offset="100%" stopColor="#27B43E"></stop>
                </linearGradient>
              </defs>
              <g fill="none" fillRule="evenodd">
                <rect width="300" height="150" x="1.5" y="21" fill="#F8F9FA" stroke="#DDE1E6" strokeWidth="1" rx="2"></rect>
                <rect width="285" height="135" x="9" y="28.5" fill="#FFFFFF" rx="1"></rect>
                <circle cx="152" cy="96" r="24" fill="url(#intro-phone)"></circle>
                <path fill="#FFFFFF" d="m146 85 8 5.5-8 5.5z"></path>
              </g>
            </svg>
          </div>
          <h2 className="text-2xl font-light text-muted-foreground mb-2">
            Visualizador de WhatsApp
          </h2>
          <p className="text-muted-foreground max-w-md">
            Selecciona una conversación de la lista para comenzar a visualizar tus chats exportados de WhatsApp.
          </p>
        </div>
      </div>
    );
  }

  const selectedChat = chats?.find(chat => chat.id === selectedChatId);

  if (!selectedChat) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">Chat no encontrado</p>
        </div>
      </div>
    );
  }

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDateSeparator = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    const yesterday = new Date(now.setDate(now.getDate() - 1));
    const isYesterday = date.toDateString() === yesterday.toDateString();

    if (isToday) {
      return 'Hoy';
    } else if (isYesterday) {
      return 'Ayer';
    } else {
      return date.toLocaleDateString('es-ES', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    }
  };

  // Group messages by date
  const groupedMessages = messages.reduce((groups, message) => {
    const date = new Date(message.timestamp).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
    return groups;
  }, {});

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Header */}
      <div className="p-4 bg-muted/50 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src={selectedChat.avatar} alt={selectedChat.name} />
            <AvatarFallback>
              {selectedChat.name.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div>
            <h2 className="font-medium">{selectedChat.name}</h2>
            <p className="text-sm text-muted-foreground">
              {selectedChat.participantCount > 1 
                ? `${selectedChat.participantCount} participantes` 
                : 'Chat individual'
              }
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <Video className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <Phone className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <Search className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div 
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3e%3cg fill='none' fill-rule='evenodd'%3e%3cg fill='%23${document.documentElement.classList.contains('dark') ? '1f2937' : 'f3f4f6'}' fill-opacity='0.05'%3e%3ccircle cx='30' cy='30' r='2'/%3e%3c/g%3e%3c/g%3e%3c/svg%3e")`,
        }}
      >
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Cargando mensajes...</p>
            </div>
          </div>
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <p className="text-muted-foreground">No hay mensajes en esta conversación</p>
          </div>
        ) : (
          Object.entries(groupedMessages).map(([date, dateMessages]) => (
            <div key={date}>
              {/* Date separator */}
              <div className="flex justify-center my-6">
                <span className="bg-muted px-3 py-1 rounded-full text-xs text-muted-foreground">
                  {formatDateSeparator(new Date(date))}
                </span>
              </div>
              
              {/* Messages for this date */}
              {dateMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isMe ? 'justify-end' : 'justify-start'} mb-2`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                      message.isMe
                        ? 'bg-green-500 text-white'
                        : 'bg-card border border-border'
                    }`}
                  >
                    {!message.isMe && (
                      <p className="text-xs font-medium text-green-600 dark:text-green-400 mb-1">
                        {message.sender}
                      </p>
                    )}
                    <p className="text-sm break-words whitespace-pre-wrap">{message.message}</p>
                    <p className={`text-xs mt-1 ${
                      message.isMe 
                        ? 'text-green-100' 
                        : 'text-muted-foreground'
                    }`}>
                      {formatMessageTime(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ))
        )}
        
        {/* Pagination info */}
        {pagination.total > 0 && (
          <div className="text-center py-4">
            <p className="text-xs text-muted-foreground">
              Mostrando {messages.length} de {pagination.total} mensajes
            </p>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatView;