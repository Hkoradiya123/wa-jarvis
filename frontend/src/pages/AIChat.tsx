import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, Copy, Plus, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import rehypeRaw from 'rehype-raw';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// --- Interfaces and Helper Functions ---
interface AIChatProps {
  username: string;
  password: string;
}
interface Message {
  role: 'user' | 'assistant';
  content: string;
}
interface Session {
  session_id: string;
  first_message: string;
  last_message_time: string;
}
const cn = (...inputs: any[]) => twMerge(clsx(inputs));

// --- CodeBlock Component (from previous implementation, no changes) ---
const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
  const match = /language-(\w+)/.exec(className || '');
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(String(children));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return !inline && match ? (
    <div className="relative my-4 rounded-md bg-gray-900">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <span className="text-xs text-gray-400">{match[1]}</span>
        <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-white">{copied ? 'Copied!' : <Copy size={14} />}</button>
      </div>
      <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>{String(children).trimEnd()}</SyntaxHighlighter>
    </div>
  ) : (
    <code className={className} {...props}>{children}</code>
  );
};

// --- Main AIChat Component ---
export const AIChat = ({ username, password }: AIChatProps) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // --- Data Fetching Hooks ---
  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (currentSessionId) {
      fetchHistory(currentSessionId);
    } else {
      setMessages([]);
    }
  }, [currentSessionId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // --- API Functions ---
  const fetchSessions = async () => {
    const res = await fetch('/api/ai_chat/sessions', { headers: { 'X-Username': username, 'X-Password': password } });
    const data = await res.json();
    setSessions(data);
  };

  const fetchHistory = async (sessionId: string) => {
    setLoading(true);
    const res = await fetch(`/api/ai_chat/sessions/${sessionId}`, { headers: { 'X-Username': username, 'X-Password': password } });
    const data = await res.json();
    setMessages(data);
    setLoading(false);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/ai_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Username': username, 'X-Password': password },
        body: JSON.stringify({ message: input, session_id: currentSessionId }),
      });
      const data = await res.json();
      
      const aiMessage: Message = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMessage]);

      if (!currentSessionId) {
        setCurrentSessionId(data.session_id);
        fetchSessions(); // Refresh session list
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
    }
    setLoading(false);
  };

  // --- Render Method ---
  return (
    <div className="flex h-[calc(100vh-160px)]">
      {/* Left Sidebar: Session List */}
      <div className="w-1/3 border-r border-gray-800 flex flex-col">
        <div className="p-2 border-b border-gray-800 flex justify-between items-center">
          <h2 className="text-sm font-bold flex items-center p-2"><MessageSquare size={16} className="mr-2" />AI Chat Sessions</h2>
          <button onClick={() => setCurrentSessionId(null)} className="p-2 hover:bg-gray-700 rounded-md"><Plus size={16} /></button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ul>
            {sessions.map((session) => (
              <li key={session.session_id} onClick={() => setCurrentSessionId(session.session_id)}
                className={cn("p-4 border-b border-gray-800 cursor-pointer hover:bg-gray-800/50", currentSessionId === session.session_id && "bg-blue-900/30")}>
                <p className="font-bold text-xs text-blue-400 truncate">{session.first_message}</p>
                <span className="text-[10px] text-gray-500">{new Date(session.last_message_time).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right Column: Chat View */}
      <div className="w-2/3 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-6" ref={chatEndRef}>
          {messages.map((msg, index) => (
            <div key={index} className="flex items-start space-x-4">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-600'}`}>
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="flex-1 text-sm text-gray-200">
                <ReactMarkdown rehypePlugins={[rehypeRaw]} components={{ code: CodeBlock }}>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          {loading && <div className="flex justify-center"><Loader2 className="animate-spin text-gray-400" /></div>}
        </div>
        <div className="p-4 border-t border-gray-800">
          <div className="relative">
            <textarea value={input} onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
              placeholder="Type your message..." rows={1}
              className="w-full bg-gray-900 rounded-md p-3 pr-12 text-sm resize-none focus:outline-none"
            />
            <button onClick={sendMessage} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white" disabled={loading}>
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
