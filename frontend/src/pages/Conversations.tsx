import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface ConversationsProps {
  username: string;
  password: string;
}

interface ConversationSummary {
  user_id: string;
  last_message_time: string;
  last_message_content: string;
  message_count: number;
}

interface Message {
  _id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const cn = (...inputs: any[]) => twMerge(clsx(inputs));

export const Conversations = ({ username, password }: ConversationsProps) => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<Message[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    setLoadingList(true);
    const res = await fetch('/api/conversations', {
      headers: { 'X-Username': username, 'X-Password': password }
    });
    const data = await res.json();
    setConversations(data);
    setLoadingList(false);
  };

  const fetchHistory = async (userId: string) => {
    setLoadingHistory(true);
    setSelectedHistory([]);
    const res = await fetch(`/api/conversations/${userId}`, {
      headers: { 'X-Username': username, 'X-Password': password }
    });
    const data = await res.json();
    setSelectedHistory(data);
    setLoadingHistory(false);
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      fetchHistory(selectedUserId);
    }
  }, [selectedUserId]);
  
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [selectedHistory]);

  return (
    <div className="flex h-[calc(100vh-160px)]">
      {/* Left Column: Conversation List */}
      <div className="w-1/3 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-sm font-bold flex items-center">
            <MessageSquare size={16} className="mr-2" />
            Conversations
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto">
          {loadingList ? (
            <div className="flex justify-center items-center h-full">
              <Loader2 size={24} className="animate-spin text-gray-500" />
            </div>
          ) : (
            <ul>
              {conversations.map((convo) => (
                <li
                  key={convo.user_id}
                  onClick={() => setSelectedUserId(convo.user_id)}
                  className={cn(
                    "p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800/50 transition-colors",
                    selectedUserId === convo.user_id && "bg-blue-900/30"
                  )}
                >
                  <div className="flex justify-between items-center mb-1">
                    <p className="font-bold text-xs text-blue-400">{convo.user_id}</p>
                    <span className="text-[10px] text-gray-500">{new Date(convo.last_message_time).toLocaleDateString()}</span>
                  </div>
                  <p className="text-xs text-gray-400 truncate">{convo.last_message_content}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Right Column: Chat View */}
      <div className="w-2/3 flex flex-col">
        {loadingHistory ? (
          <div className="flex justify-center items-center h-full">
            <Loader2 size={32} className="animate-spin text-gray-400" />
          </div>
        ) : selectedUserId ? (
          <div className="flex-1 flex flex-col h-full">
            <div className="p-4 border-b border-gray-800">
              <h3 className="font-bold text-sm text-gray-300">{selectedUserId}</h3>
            </div>
            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
              {selectedHistory.map((msg) => (
                <div
                  key={msg._id}
                  className={cn("flex", { "justify-end": msg.role === 'assistant', "justify-start": msg.role === 'user' })}
                >
                  <div
                    className={cn("max-w-xl rounded-lg px-4 py-2", {
                      "bg-blue-800 text-white": msg.role === 'assistant',
                      "bg-gray-700 text-gray-200": msg.role === 'user',
                    })}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <p className="text-[10px] text-right mt-1 opacity-50">{new Date(msg.timestamp).toLocaleTimeString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex justify-center items-center h-full text-gray-500">
            <p>Select a conversation to view chat history.</p>
          </div>
        )}
      </div>
    </div>
  );
};
