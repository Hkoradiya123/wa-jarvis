import React, { useEffect, useState } from 'react';
import { Users, UserPlus, Trash2, Shield, RefreshCw } from 'lucide-react';

interface UserManagementProps {
  username: string;
  password: string;
}

export const UserManagement = ({ username, password }: UserManagementProps) => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'user' });
  const [status, setStatus] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/users', {
        headers: { 'X-Username': username, 'X-Password': password }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data);
      } else {
        setStatus(`FAILED_TO_FETCH: ${res.status}`);
      }
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
    setLoading(false);
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("PROVISIONING_USER...");
    try {
      const res = await fetch('/api/users', {
        method: 'POST',
        headers: { 
          'X-Username': username, 
          'X-Password': password,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });
      if (res.ok) {
        setStatus("USER_PROVISIONED_SUCCESSFULLY");
        setNewUser({ username: '', password: '', role: 'user' });
        fetchUsers();
      } else {
        const data = await res.json();
        setStatus(`PROVISIONING_FAILED: ${data.detail}`);
      }
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  const handleDeleteUser = async (targetUser: string) => {
    if (!confirm(`Confirm termination of session for ${targetUser}?`)) return;
    setStatus(`TERMINATING_${targetUser}...`);
    try {
      const res = await fetch(`/api/users/${targetUser}`, {
        method: 'DELETE',
        headers: { 'X-Username': username, 'X-Password': password }
      });
      if (res.ok) {
        setStatus("USER_TERMINATED");
        fetchUsers();
      } else {
        const data = await res.json();
        setStatus(`TERMINATION_FAILED: ${data.detail}`);
      }
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  return (
    <div className="space-y-6 font-mono">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-2 text-blue-500">
          <Users size={14} />
          <h3 className="text-xs font-bold uppercase tracking-widest">User_Management_Matrix</h3>
        </div>
        <button onClick={fetchUsers} className="text-gray-500 hover:text-white transition-colors">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User List */}
        <div className="lg:col-span-2 bg-black/20 border border-gray-800 rounded overflow-hidden">
          <table className="w-full text-left text-[11px] border-collapse">
            <thead>
              <tr className="bg-gray-900/50 border-b border-gray-800 text-gray-500 uppercase">
                <th className="py-2 px-4">Ident_ID</th>
                <th className="py-2 px-4">Clearance</th>
                <th className="py-2 px-4">Created_At</th>
                <th className="py-2 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u: any) => (
                <tr key={u.username} className="border-b border-gray-900 hover:bg-gray-800/30 transition-colors">
                  <td className="py-3 px-4 font-bold text-blue-400">{u.username}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] border ${
                      u.role === 'admin' ? 'text-red-500 border-red-900/50 bg-red-900/10' : 'text-green-500 border-green-900/50 bg-green-900/10'
                    }`}>
                      {u.role.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-500">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="py-3 px-4 text-right">
                    {u.username !== 'admin' && (
                      <button 
                        onClick={() => handleDeleteUser(u.username)}
                        className="text-red-900 hover:text-red-500 transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Provision Form */}
        <div className="bg-[#161b22] border border-gray-800 rounded p-4 space-y-4">
          <div className="flex items-center space-x-2 text-gray-400 mb-2">
            <UserPlus size={14} />
            <span className="text-[10px] font-bold uppercase tracking-widest">Provision_New_User</span>
          </div>
          
          <form onSubmit={handleAddUser} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[9px] text-gray-500 uppercase">Ident_ID</label>
              <input 
                type="text"
                required
                value={newUser.username}
                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                className="w-full bg-black border border-gray-800 rounded px-3 py-2 text-xs focus:outline-none focus:border-blue-500/50"
                placeholder="USERNAME..."
              />
            </div>
            <div className="space-y-1">
              <label className="text-[9px] text-gray-500 uppercase">Access_Key</label>
              <input 
                type="password"
                required
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                className="w-full bg-black border border-gray-800 rounded px-3 py-2 text-xs focus:outline-none focus:border-blue-500/50"
                placeholder="PASSWORD..."
              />
            </div>
            <div className="space-y-1">
              <label className="text-[9px] text-gray-500 uppercase">Clearance_Level</label>
              <select 
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                className="w-full bg-black border border-gray-800 rounded px-3 py-2 text-xs focus:outline-none focus:border-blue-500/50"
              >
                <option value="user">USER</option>
                <option value="admin">ADMIN</option>
              </select>
            </div>
            <button 
              type="submit"
              className="w-full bg-blue-600/10 hover:bg-blue-600/20 text-blue-500 border border-blue-600/50 py-2 text-[10px] font-bold uppercase tracking-widest transition-all"
            >
              Authorize_Provision
            </button>
          </form>

          {status && (
            <div className="mt-4 p-2 bg-black/50 border border-gray-800 rounded text-[9px] text-gray-500 break-all font-mono">
              {`> ${status}`}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};