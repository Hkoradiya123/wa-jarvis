import React from 'react';
import { Terminal, Database, Clock, Activity, Settings, Shield, Users, MessageSquare, Bot } from 'lucide-react';

const navItems = [
  { id: 'logs', label: 'LIVE_LOGS', icon: Activity },
  { id: 'ai-chat', label: 'AI_CHAT', icon: Bot },
  { id: 'conversations', label: 'CONVERSATIONS', icon: MessageSquare },
  { id: 'memory', label: 'MEMORY_VAULT', icon: Database },
  { id: 'reminders', label: 'REMINDERS', icon: Clock },
  { id: 'prompts', label: 'PROMPT_MANAGER', icon: Settings },
  { id: 'status', label: 'SYSTEM_STATUS', icon: Shield },
  { id: 'users', label: 'USER_MANAGEMENT', icon: Users },
  { id: 'console', label: 'DIRECT_CONSOLE', icon: Terminal },
];

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => (
  <div className="w-64 border-r border-gray-800 h-screen flex flex-col bg-[#0d1117]">
    <div className="p-4 border-b border-gray-800 font-bold text-sm tracking-widest text-blue-400">
      JARVIS_OS
    </div>
    <nav className="flex-1 p-2 space-y-1">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => setActiveTab(item.id)}
          className={`w-full flex items-center space-x-3 px-3 py-2 text-xs rounded transition-colors ${
            activeTab === item.id ? 'bg-gray-800 text-white' : 'text-gray-500 hover:text-gray-300'     
          }`}
        >
          <item.icon size={14} />
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-gray-800 text-[10px] text-gray-600">
      STATUS: CONNECTED
    </div>
  </div>
);
