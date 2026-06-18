import React, { useEffect, useState } from 'react';
import { Save, RefreshCw } from 'lucide-react';

interface PromptManagerProps {
  username: string;
  password: string;
}

export const PromptManager = ({ username, password }: PromptManagerProps) => {
  const [prompts, setPrompts] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);

  const fetchPrompts = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/prompts', {
        headers: { 'X-Username': username, 'X-Password': password }
      });
      const data = await res.json();
      setPrompts(data);
    } catch (e) {
      console.error("Failed to fetch prompts:", e);
    }
    setLoading(false);
  };

  const savePrompt = async (name: string, content: string) => {
    setSaving(name);
    try {
      await fetch(`/api/prompts/${name}`, {
        method: 'POST',
        headers: { 
          'X-Username': username,
          'X-Password': password,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
      });
    } catch (e) {
      console.error(`Failed to save prompt ${name}:`, e);
    }
    setSaving(null);
  };

  useEffect(() => { fetchPrompts(); }, []);

  if (loading) {
    return <div className="text-gray-500 animate-pulse">Loading core directives...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xs font-bold text-blue-500 uppercase tracking-widest flex items-center space-x-2">
          <Save size={14} />
          <span>Core_Directives_Editor</span>
        </h3>
        <button onClick={fetchPrompts} className="text-gray-500 hover:text-white transition-colors">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {Object.entries(prompts).map(([name, content]) => (
          <div key={name} className="bg-black/20 border border-gray-800 rounded p-4 group">
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-gray-500 uppercase tracking-tighter">
                Directive: {name}
              </span>
              {saving === name && (
                <span className="text-[10px] text-yellow-500 animate-pulse">SAVING_CHANGES...</span>
              )}
            </div>
            <textarea
              defaultValue={content}
              onBlur={(e) => {
                if (e.target.value !== content) {
                  savePrompt(name, e.target.value);
                }
              }}
              className="w-full bg-black/40 border border-gray-800 rounded p-3 text-xs font-mono text-gray-300 h-32 focus:outline-none focus:border-blue-500/50 resize-none transition-colors"
              spellCheck={false}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
