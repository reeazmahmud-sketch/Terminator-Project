import { useState, useEffect } from 'react';
import { Activity, Users, MessageSquare, AlertCircle, TrendingUp } from 'lucide-react';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../contexts/AuthContext';

interface UsageLog {
  id: string;
  user_id: string;
  action: string;
  provider: string | null;
  model: string | null;
  tokens_used: number;
  response_time_ms: number | null;
  status: string;
  error_message: string | null;
  created_at: string;
}

interface Stats {
  totalUsers: number;
  totalConversations: number;
  totalMessages: number;
  totalTokens: number;
  errorRate: number;
}

export function AdminPanel() {
  const { profile } = useAuth();
  const [logs, setLogs] = useState<UsageLog[]>([]);
  const [stats, setStats] = useState<Stats>({
    totalUsers: 0,
    totalConversations: 0,
    totalMessages: 0,
    totalTokens: 0,
    errorRate: 0,
  });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'success' | 'error'>('all');

  useEffect(() => {
    if (profile?.is_admin) {
      loadData();
    }
  }, [profile, filter]);

  async function loadData() {
    setLoading(true);
    try {
      const [logsResult, usersResult, convsResult, messagesResult] = await Promise.all([
        supabase
          .from('usage_logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(100),
        supabase.from('profiles').select('id', { count: 'exact', head: true }),
        supabase.from('conversations').select('id', { count: 'exact', head: true }),
        supabase.from('messages').select('id, tokens_used', { count: 'exact' }),
      ]);

      if (logsResult.error) throw logsResult.error;

      let filteredLogs = logsResult.data || [];
      if (filter !== 'all') {
        filteredLogs = filteredLogs.filter((log) => log.status === filter);
      }

      setLogs(filteredLogs);

      const totalTokens = (messagesResult.data || []).reduce(
        (sum, msg) => sum + (msg.tokens_used || 0),
        0
      );

      const totalLogs = logsResult.data?.length || 1;
      const errorLogs = logsResult.data?.filter((log) => log.status === 'error').length || 0;

      setStats({
        totalUsers: usersResult.count || 0,
        totalConversations: convsResult.count || 0,
        totalMessages: messagesResult.count || 0,
        totalTokens,
        errorRate: (errorLogs / totalLogs) * 100,
      });
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (!profile?.is_admin) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-red-800 mb-2">Access Denied</h2>
          <p className="text-red-700">You do not have admin privileges.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-gray-500">Loading admin data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Users</p>
              <p className="text-2xl font-bold text-gray-800">{stats.totalUsers}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Conversations</p>
              <p className="text-2xl font-bold text-gray-800">{stats.totalConversations}</p>
            </div>
            <MessageSquare className="w-8 h-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Tokens</p>
              <p className="text-2xl font-bold text-gray-800">{stats.totalTokens.toLocaleString()}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-yellow-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Error Rate</p>
              <p className="text-2xl font-bold text-gray-800">{stats.errorRate.toFixed(1)}%</p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">Usage Logs</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-1.5 text-sm rounded transition-colors ${
                  filter === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter('success')}
                className={`px-3 py-1.5 text-sm rounded transition-colors ${
                  filter === 'success'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Success
              </button>
              <button
                onClick={() => setFilter('error')}
                className={`px-3 py-1.5 text-sm rounded transition-colors ${
                  filter === 'error'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Errors
              </button>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Provider
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Tokens
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Time (ms)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-800">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">{log.action}</td>
                  <td className="px-6 py-4 text-sm text-gray-800">{log.provider || '-'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                    {log.model || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-800">{log.tokens_used}</td>
                  <td className="px-6 py-4 text-sm text-gray-800">{log.response_time_ms || '-'}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        log.status === 'success'
                          ? 'bg-green-100 text-green-800'
                          : log.status === 'error'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {logs.length === 0 && (
            <div className="text-center py-12 text-gray-500">No logs found</div>
          )}
        </div>
      </div>
    </div>
  );
}
