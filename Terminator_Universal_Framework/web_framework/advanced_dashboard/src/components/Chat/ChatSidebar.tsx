import { useState, useRef } from 'react';
import {
  MessageSquare,
  X,
  Link as LinkIcon,
  FileText,
  Upload,
  Send,
  ChevronRight,
  ChevronLeft,
} from 'lucide-react';

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onSendMessage: (message: string, context?: any) => void;
  selectedModel: string;
  selectedProvider: string;
}

type InputMode = 'url' | 'text' | 'file';

export function ChatSidebar({
  isOpen,
  onToggle,
  onSendMessage,
  selectedModel,
  selectedProvider,
}: ChatSidebarProps) {
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [message, setMessage] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSend() {
    if (!message.trim()) return;

    let context;
    if (inputMode === 'url' && urlInput) {
      context = { type: 'url', data: { url: urlInput } };
    } else if (inputMode === 'file' && uploadedFile) {
      context = { type: 'file', data: { filename: uploadedFile.name } };
    }

    onSendMessage(message, context);
    setMessage('');
    setUrlInput('');
    setUploadedFile(null);
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  }

  return (
    <>
      <button
        onClick={onToggle}
        className={`fixed left-4 top-4 z-50 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-all ${
          isOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <MessageSquare className="w-5 h-5" />
      </button>

      <div
        className={`fixed left-0 top-0 h-full bg-white shadow-2xl transition-all duration-300 z-40 ${
          isOpen ? 'w-96 translate-x-0' : 'w-96 -translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              <h2 className="font-semibold">Chat Assistant</h2>
            </div>
            <button
              onClick={onToggle}
              className="p-1 hover:bg-blue-500 rounded transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 border-b bg-gray-50">
            <div className="text-xs text-gray-600 mb-2">Context Source</div>
            <div className="flex gap-2">
              <button
                onClick={() => setInputMode('text')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded transition-colors ${
                  inputMode === 'text'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span className="text-sm">Text</span>
              </button>
              <button
                onClick={() => setInputMode('url')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded transition-colors ${
                  inputMode === 'url'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <LinkIcon className="w-4 h-4" />
                <span className="text-sm">URL</span>
              </button>
              <button
                onClick={() => {
                  setInputMode('file');
                  fileInputRef.current?.click();
                }}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded transition-colors ${
                  inputMode === 'file'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Upload className="w-4 h-4" />
                <span className="text-sm">File</span>
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {inputMode === 'url' && (
            <div className="p-4 border-b bg-blue-50">
              <label className="block text-xs font-medium text-gray-700 mb-2">
                Page URL
              </label>
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
          )}

          {inputMode === 'file' && uploadedFile && (
            <div className="p-4 border-b bg-green-50">
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <FileText className="w-4 h-4 text-green-600" />
                <span className="flex-1 truncate">{uploadedFile.name}</span>
                <button
                  onClick={() => setUploadedFile(null)}
                  className="p-1 hover:bg-green-100 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-3">
              <div className="text-xs text-gray-500 text-center py-4">
                Start a conversation below
              </div>
            </div>
          </div>

          <div className="p-4 border-t bg-gray-50">
            <div className="flex gap-2">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm"
                rows={3}
              />
              <button
                onClick={handleSend}
                disabled={!message.trim()}
                className="px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Using: {selectedProvider} / {selectedModel}
            </div>
          </div>
        </div>
      </div>

      {isOpen && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-black bg-opacity-20 z-30 transition-opacity"
        />
      )}
    </>
  );
}
