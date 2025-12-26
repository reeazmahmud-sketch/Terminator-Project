import { useState, useEffect } from 'react';
import { LogOut, User as UserIcon, Shield } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { ChatSidebar } from './Chat/ChatSidebar';
import { ChatWindow } from './Chat/ChatWindow';
import { ModelSelector } from './Chat/ModelSelector';
import { ProfilePage } from './Profile/ProfilePage';
import { AdminPanel } from './Admin/AdminPanel';
import { supabase } from '../lib/supabase';
import { streamChat, uploadFile, ChatMessage } from '../lib/api';
import { decryptAPIKey } from '../lib/crypto';

type View = 'chat' | 'profile' | 'admin';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function MainApp() {
  const { user, profile, signOut } = useAuth();
  const [view, setView] = useState<View>('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');
  const [apiKeys, setApiKeys] = useState<Array<{ provider: string; key_name: string; encrypted_key: string }>>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>();

  useEffect(() => {
    loadAPIKeys();
  }, []);

  useEffect(() => {
    if (apiKeys.length > 0) {
      const firstProvider = apiKeys[0].provider;
      setSelectedProvider(firstProvider);
      if (firstProvider === 'openai') {
        setSelectedModel('gpt-3.5-turbo');
      } else if (firstProvider === 'anthropic') {
        setSelectedModel('claude-3-haiku-20240307');
      }
    }
  }, [apiKeys]);

  async function loadAPIKeys() {
    try {
      const { data, error } = await supabase
        .from('api_keys')
        .select('provider, key_name, encrypted_key')
        .eq('is_active', true);

      if (error) throw error;
      setApiKeys(data || []);
    } catch (error) {
      console.error('Error loading API keys:', error);
    }
  }

  async function handleSendMessage(message: string, context?: any) {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamingContent('');

    try {
      const apiKey = apiKeys.find((key) => key.provider === selectedProvider);
      if (!apiKey) {
        throw new Error('No API key found for selected provider');
      }

      const decryptedKey = await decryptAPIKey(apiKey.encrypted_key);

      let contextData = context;
      if (context?.type === 'file') {
        const file = context.data.file;
        const extractedText = await uploadFile(file);
        contextData = { type: 'file', data: { filename: file.name, text: extractedText } };
      }

      const chatMessages: ChatMessage[] = [
        ...messages.map((m) => ({ role: m.role, content: m.content })),
        { role: 'user', content: message },
      ];

      await streamChat(
        {
          messages: chatMessages,
          model: selectedModel,
          provider: selectedProvider,
          apiKey: decryptedKey,
          conversationId: currentConversationId,
          context: contextData,
        },
        (chunk) => {
          setStreamingContent((prev) => prev + chunk);
        },
        (fullText) => {
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: fullText,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setStreamingContent('');
          setIsLoading(false);
        },
        (error) => {
          console.error('Chat error:', error);
          setStreamingContent('');
          setIsLoading(false);
          alert(`Error: ${error}`);
        }
      );
    } catch (error: any) {
      console.error('Error sending message:', error);
      setIsLoading(false);
      alert(`Error: ${error.message}`);
    }
  }

  function exportConversation() {
    const exportData = {
      exported_at: new Date().toISOString(),
      messages: messages.map((m) => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp.toISOString(),
      })),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-gray-800">Sider Clone</h1>
            <nav className="flex gap-2">
              <button
                onClick={() => setView('chat')}
                className={`px-3 py-1.5 rounded transition-colors ${
                  view === 'chat'
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => setView('profile')}
                className={`px-3 py-1.5 rounded transition-colors ${
                  view === 'profile'
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Profile
              </button>
              {profile?.is_admin && (
                <button
                  onClick={() => setView('admin')}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded transition-colors ${
                    view === 'admin'
                      ? 'bg-blue-100 text-blue-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  Admin
                </button>
              )}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">{profile?.email}</span>
            <button
              onClick={signOut}
              className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        {view === 'chat' && (
          <div className="h-full flex">
            <ChatSidebar
              isOpen={isSidebarOpen}
              onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
              onSendMessage={handleSendMessage}
              selectedModel={selectedModel}
              selectedProvider={selectedProvider}
            />
            <div className="flex-1 flex flex-col lg:flex-row gap-6 p-6">
              <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <ChatWindow
                  messages={messages}
                  isLoading={isLoading}
                  streamingContent={streamingContent}
                  onExport={exportConversation}
                />
              </div>
              <div className="lg:w-80">
                <ModelSelector
                  selectedProvider={selectedProvider}
                  selectedModel={selectedModel}
                  onProviderChange={setSelectedProvider}
                  onModelChange={setSelectedModel}
                  apiKeys={apiKeys}
                />
              </div>
            </div>
          </div>
        )}

        {view === 'profile' && <ProfilePage />}
        {view === 'admin' && <AdminPanel />}
      </main>
    </div>
  );
}
