# WhatsApp Viewer - API Contracts y Backend Integration

## 1. Datos Actualmente Mockeados (mock/chatData.js)

### Chats Mock:
```javascript
mockChats = [
  {
    id: 1,
    name: "Familia 👨‍👩‍👧‍👦",
    lastMessage: "Mamá: Recuerden la cena de mañana",
    timestamp: "2024-01-15 18:30",
    unread: 2,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=familia"
  }
]
```

### Mensajes Mock:
```javascript
mockMessages = {
  1: [
    {
      id: 1,
      sender: "Mamá",
      message: "Hola familia, ¿cómo están todos?",
      timestamp: "2024-01-15 10:00",
      isMe: false,
      type: "text"
    }
  ]
}
```

## 2. API Contracts para Backend

### 2.1 Chat Management

#### GET /api/chats
- **Propósito**: Obtener lista de chats del usuario
- **Response**: 
```json
[
  {
    "id": "chat_uuid",
    "name": "Familia",
    "lastMessage": "Último mensaje...",
    "timestamp": "2024-01-15T18:30:00Z",
    "unreadCount": 2,
    "avatar": "avatar_url",
    "participantCount": 4
  }
]
```

#### GET /api/chats/{chat_id}/messages
- **Propósito**: Obtener mensajes de un chat específico
- **Query params**: `?page=1&limit=50`
- **Response**:
```json
{
  "messages": [
    {
      "id": "msg_uuid",
      "chatId": "chat_uuid",
      "sender": "Nombre del remitente",
      "message": "Contenido del mensaje",
      "timestamp": "2024-01-15T10:00:00Z",
      "isMe": false,
      "type": "text|image|video|audio|document",
      "mediaUrl": "url_if_media"
    }
  ],
  "pagination": {
    "page": 1,
    "totalPages": 10,
    "hasMore": true
  }
}
```

### 2.2 File Upload & Processing

#### POST /api/upload-chat
- **Propósito**: Procesar archivo de chat exportado de WhatsApp
- **Content-Type**: multipart/form-data
- **Body**: 
```
file: archivo .txt de WhatsApp export
```
- **Response**:
```json
{
  "success": true,
  "chatId": "new_chat_uuid",
  "message": "Chat procesado exitosamente",
  "stats": {
    "totalMessages": 150,
    "participants": ["Yo", "Mamá", "Papá"],
    "dateRange": {
      "from": "2024-01-01",
      "to": "2024-01-15"
    }
  }
}
```

#### DELETE /api/chats/{chat_id}
- **Propósito**: Eliminar un chat
- **Response**: `{ "success": true }`

## 3. Modelos de MongoDB

### Chat Collection:
```javascript
{
  _id: ObjectId,
  name: String,
  participants: [String],
  createdAt: Date,
  updatedAt: Date,
  lastMessage: {
    content: String,
    timestamp: Date,
    sender: String
  },
  messageCount: Number,
  unreadCount: { type: Number, default: 0 }
}
```

### Message Collection:
```javascript
{
  _id: ObjectId,
  chatId: ObjectId,
  sender: String,
  content: String,
  timestamp: Date,
  isMe: Boolean,
  type: String, // 'text', 'image', 'video', 'audio', 'document'
  mediaPath: String, // si es archivo multimedia
  originalLine: String // línea original del export para debugging
}
```

## 4. Procesamiento de Archivos WhatsApp

### Formato esperado del archivo .txt:
```
[15/1/24 10:00:35] Mamá: Hola familia, ¿cómo están todos?
[15/1/24 10:05:12] Yo: ¡Hola mamá! Todo bien por aquí
[15/1/24 10:10:25] Papá: Todo perfecto, trabajando desde casa hoy
```

### Regex para parsing:
- `\[(\d{1,2}\/\d{1,2}\/\d{2,4}) (\d{1,2}:\d{2}:\d{2})\] ([^:]+): (.+)`
- Grupos: fecha, hora, remitente, mensaje

## 5. Frontend Integration Changes

### Archivos a modificar:
1. **App.js** - Remover mock imports, agregar API calls
2. **ChatSidebar.js** - Reemplazar `mockChats` con API call
3. **ChatView.js** - Reemplazar `mockMessages` con API call
4. **Crear services/api.js** - Centralizar calls de API

### API Service:
```javascript
// services/api.js
const API_BASE = process.env.REACT_APP_BACKEND_URL + '/api';

export const chatAPI = {
  getChats: () => axios.get(`${API_BASE}/chats`),
  getMessages: (chatId, page = 1) => axios.get(`${API_BASE}/chats/${chatId}/messages?page=${page}`),
  uploadChatFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API_BASE}/upload-chat`, formData);
  },
  deleteChat: (chatId) => axios.delete(`${API_BASE}/chats/${chatId}`)
};
```

## 6. Funcionalidades Backend a Implementar

1. **Parser de archivos WhatsApp** - Extraer mensajes del formato .txt
2. **Almacenamiento en MongoDB** - Guardar chats y mensajes
3. **API CRUD** - Endpoints para gestión de chats
4. **Validación de archivos** - Verificar formato correcto
5. **Paginación** - Para chats con muchos mensajes
6. **Búsqueda** - Filtrado por contenido y remitente
7. **Manejo de errores** - Response consistente para errores

## 7. Próximos Pasos de Implementación

1. Crear modelos Pydantic para Chat y Message
2. Implementar parser de archivos WhatsApp 
3. Crear endpoints CRUD en FastAPI
4. Actualizar frontend para usar APIs reales
5. Testing de funcionalidad completa