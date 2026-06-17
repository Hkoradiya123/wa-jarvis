import React, { useState } from 'react';
import { Layout } from './components/Layout';

function App() {
  const [activeTab, setActiveTab] = useState('logs');

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      <header className="mb-6">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-tighter">
          Root / {activeTab}
        </h2>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <div>Log Stream Component Placeholder</div>}
        {activeTab === 'memory' && <div>Memory Vault Component Placeholder</div>}
        {activeTab === 'reminders' && <div>Reminder Grid Component Placeholder</div>}
        {activeTab === 'console' && <div>Direct Console Component Placeholder</div>}
      </div>
    </Layout>
  );
}

export default App;
