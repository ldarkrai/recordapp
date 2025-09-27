// Mock data for WhatsApp chat visualization

export const mockChats = [
  {
    id: 1,
    name: "Familia 👨‍👩‍👧‍👦",
    lastMessage: "Mamá: Recuerden la cena de mañana",
    timestamp: "2024-01-15 18:30",
    unread: 2,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=familia"
  },
  {
    id: 2,
    name: "Trabajo - Equipo",
    lastMessage: "Carlos: La reunión se cambió a las 3pm",
    timestamp: "2024-01-15 15:45",
    unread: 0,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=trabajo"
  },
  {
    id: 3,
    name: "Ana García",
    lastMessage: "¡Felicidades por el ascenso!",
    timestamp: "2024-01-15 12:20",
    unread: 1,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=ana"
  },
  {
    id: 4,
    name: "Amigos del gym",
    lastMessage: "Pedro: ¿Nos vemos mañana a las 7?",
    timestamp: "2024-01-14 20:15",
    unread: 0,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=gym"
  },
  {
    id: 5,
    name: "María López",
    lastMessage: "Nos vemos en el café",
    timestamp: "2024-01-14 16:30",
    unread: 0,
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=maria"
  }
];

export const mockMessages = {
  1: [
    {
      id: 1,
      sender: "Mamá",
      message: "Hola familia, ¿cómo están todos?",
      timestamp: "2024-01-15 10:00",
      isMe: false,
      type: "text"
    },
    {
      id: 2,
      sender: "Yo",
      message: "¡Hola mamá! Todo bien por aquí",
      timestamp: "2024-01-15 10:05",
      isMe: true,
      type: "text"
    },
    {
      id: 3,
      sender: "Papá",
      message: "Todo perfecto, trabajando desde casa hoy",
      timestamp: "2024-01-15 10:10",
      isMe: false,
      type: "text"
    },
    {
      id: 4,
      sender: "Hermana",
      message: "Yo también bien, estudiando para los exámenes",
      timestamp: "2024-01-15 10:15",
      isMe: false,
      type: "text"
    },
    {
      id: 5,
      sender: "Mamá",
      message: "Recuerden que mañana es la cena familiar a las 8pm",
      timestamp: "2024-01-15 18:30",
      isMe: false,
      type: "text"
    },
    {
      id: 6,
      sender: "Yo",
      message: "¡Perfecto! Ahí estaré",
      timestamp: "2024-01-15 18:32",
      isMe: true,
      type: "text"
    }
  ],
  2: [
    {
      id: 1,
      sender: "Carlos",
      message: "Buenos días equipo",
      timestamp: "2024-01-15 09:00",
      isMe: false,
      type: "text"
    },
    {
      id: 2,
      sender: "Yo",
      message: "Buenos días Carlos",
      timestamp: "2024-01-15 09:02",
      isMe: true,
      type: "text"
    },
    {
      id: 3,
      sender: "Laura",
      message: "¡Hola a todos!",
      timestamp: "2024-01-15 09:05",
      isMe: false,
      type: "text"
    },
    {
      id: 4,
      sender: "Carlos",
      message: "Tengo que cambiar la reunión de hoy",
      timestamp: "2024-01-15 15:40",
      isMe: false,
      type: "text"
    },
    {
      id: 5,
      sender: "Carlos",
      message: "La reunión se cambió a las 3pm en lugar de las 2pm",
      timestamp: "2024-01-15 15:45",
      isMe: false,
      type: "text"
    },
    {
      id: 6,
      sender: "Laura",
      message: "Perfecto, me viene mejor",
      timestamp: "2024-01-15 15:46",
      isMe: false,
      type: "text"
    }
  ],
  3: [
    {
      id: 1,
      sender: "Ana García",
      message: "¡Hola! ¿Cómo estás?",
      timestamp: "2024-01-15 11:00",
      isMe: false,
      type: "text"
    },
    {
      id: 2,
      sender: "Yo",
      message: "¡Hola Ana! Muy bien, gracias",
      timestamp: "2024-01-15 11:05",
      isMe: true,
      type: "text"
    },
    {
      id: 3,
      sender: "Ana García",
      message: "Me enteré de tu ascenso en el trabajo",
      timestamp: "2024-01-15 12:15",
      isMe: false,
      type: "text"
    },
    {
      id: 4,
      sender: "Ana García",
      message: "¡Felicidades por el ascenso!",
      timestamp: "2024-01-15 12:20",
      isMe: false,
      type: "text"
    },
    {
      id: 5,
      sender: "Yo",
      message: "¡Muchas gracias Ana! Estoy muy emocionado",
      timestamp: "2024-01-15 12:25",
      isMe: true,
      type: "text"
    }
  ]
};