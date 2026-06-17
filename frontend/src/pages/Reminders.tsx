import React, { useEffect, useState } from 'react';
import { Clock } from 'lucide-react';

export const Reminders = ({ password }: { password: string }) => {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReminders = async () => {
    try {
      const res = await fetch('/api/reminders', {
        headers: { 'X-Password': password }
      });
      const data = await res.json();
      setReminders(data);
    } catch (e) { 
      console.error("Failed to fetch reminders:", e); 
    }
    setLoading(false);
  };

  useEffect(() => { fetchReminders(); }, []);

  return (
    <div className="space-y-4 font-mono">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center space-x-2 text-blue-500">
          <Clock size={14} />
          <h3 className="text-xs font-bold uppercase tracking-tighter">Active_Reminders</h3>
        </div>
        <button onClick={fetchReminders} className="text-[10px] text-blue-500 hover:underline">REFRESH_DATA</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500 uppercase text-[10px]">
              <th className="py-2 px-4">Task</th>
              <th className="py-2 px-4">Due_Date</th>
              <th className="py-2 px-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {reminders.map((r: any) => (
              <tr key={r._id} className="border-b border-gray-900 hover:bg-gray-800/30 transition-colors">
                <td className="py-3 px-4 text-blue-400">{r.task}</td>
                <td className="py-3 px-4 text-gray-400">{new Date(r.due_date).toLocaleString()}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded-full bg-blue-900/20 text-blue-500 border border-blue-900/50 text-[10px]">
                    PENDING
                  </span>
                </td>
              </tr>
            ))}
            {reminders.length === 0 && !loading && (
              <tr>
                <td colSpan={3} className="py-8 text-center text-gray-600 uppercase tracking-widest text-[10px]">
                  No_active_reminders_found
                </td>
              </tr>
            )}
            {loading && (
              <tr>
                <td colSpan={3} className="py-8 text-center text-blue-500 animate-pulse uppercase tracking-widest text-[10px]">
                  Loading_data...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
