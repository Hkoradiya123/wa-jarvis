import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Copy } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import rehypeRaw from 'rehype-raw';

interface AIChatProps {
  username: string;
  password: string;
}

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

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
        <button onClick={handleCopy} className="text-xs text-gray-400 hover:text-white">
          {copied ? 'Copied!' : <Copy size={14} />}
        </button>
      </div>
      <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
        {String(children).replace(/
$/, '')}
      </SyntaxHighlighter>
    </div>
  ) : (
    <code className={className} {...props}>
      {children}
    </code>
  );
};

export const AIChat = ({ username, password }: AIChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages: Message[] = [...messages, { id: Date.now(), role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Username': username,
          'X-Password': password,
        },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages([...newMessages, { id: Date.now() + 1, role: 'assistant', content: data.response }]);
    } catch (e) {
      setMessages([...newMessages, { id: Date.now() + 1, role: 'assistant', content: 'Sorry, I encountered an error.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-160px)]">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className="flex items-start space-x-4">
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-600'}`}>
              {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className="flex-1">
              <ReactMarkdown
                rehypePlugins={[rehypeRaw]}
                components={{ code: CodeBlock }}
              >
                {msg.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && <Loader2 className="animate-spin" />}
        <div ref={chatEndRef} />
      </div>
      <div className="p-4 border-t border-gray-800">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Type your message..."
            rows={1}
            className="w-full bg-gray-900 rounded-md p-3 pr-12 text-sm resize-none focus:outline-none"
          />
          <button onClick={sendMessage} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};
