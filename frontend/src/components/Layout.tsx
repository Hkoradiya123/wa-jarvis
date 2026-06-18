import React from 'react';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Layout = ({ children, activeTab, setActiveTab }: LayoutProps) => (
  <div className="flex h-screen overflow-hidden">
    <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
    <main className="flex-1 overflow-auto bg-[#0d1117]">
      <div className="p-6">{children}</div>
    </main>
  </div>
);
