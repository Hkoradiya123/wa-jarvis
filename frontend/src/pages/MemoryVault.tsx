import React, { useEffect, useState } from 'react';
import { Trash2, Search } from 'lucide-react';

interface MemoryVaultProps {
  username: string;
  password?: string;
}

export const MemoryVault = ({ username, password }: MemoryVaultProps) => {
  const [memories, setMemories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMemories = async () => {
    const res = await fetch('/api/memories', {
      headers: { 'X-Username': username, 'X-Password': password }
    });
    const data = await res.json();
    setMemories(data);
    setLoading(false);
  };

  const deleteMemory = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    await fetch(`/api/memories/${id}`, { 
      method: 'DELETE',
      headers: { 'X-Username': username, 'X-Password': password }
    });
    fetchMemories();
  };

  useEffect(() => { fetchMemories(); }, []);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 text-gray-500" size={14} />
          <input
            type="text"
            placeholder="Search memories..."
            className="bg-black border border-gray-800 rounded pl-8 pr-3 py-1.5 text-xs w-64 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button onClick={fetchMemories} className="text-[10px] text-blue-500 hover:underline">REFRESH_DATA</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500 uppercase text-[10px]">
              <th className="py-2 px-4">Category</th>
              <th className="py-2 px-4">Content</th>
              <th className="py-2 px-4">Timestamp</th>
              <th className="py-2 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {memories.map((m: any) => (
              <tr key={m._id} className="border-b border-gray-900 hover:bg-gray-800/30 transition-colors">
                <td className="py-3 px-4 text-blue-400">{m.category}</td>
                <td className="py-3 px-4">{m.value || m.content}</td>
                <td className="py-3 px-4 text-gray-600">{new Date(m.timestamp).toLocaleString()}</td>
                <td className="py-3 px-4 text-right">
                  <button onClick={() => deleteMemory(m._id)} className="text-red-900 hover:text-red-500">
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
