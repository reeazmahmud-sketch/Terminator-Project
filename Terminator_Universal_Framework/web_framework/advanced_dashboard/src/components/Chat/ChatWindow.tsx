import { useState, useRef, useEffect } from 'react';
import { Loader2, Download } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  streamingContent: string;
  onExport: () => void;
}

export function ChatWindow({ messages, isLoading, streamingContent, onExport }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <h1 className="text-xl font-semibold text-gray-800">Conversation</h1>
        {messages.length > 0 && (
          <button
            onClick={onExport}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <p className="text-lg font-medium">No messages yet</p>
              <p className="text-sm mt-2">Open the sidebar to start chatting</p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-800 shadow-sm border border-gray-200'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap break-words">{message.content}</div>
              <div
                className={`text-xs mt-2 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}
              >
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && streamingContent && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg p-4 bg-white text-gray-800 shadow-sm border border-gray-200">
              <div className="text-sm whitespace-pre-wrap break-words">{streamingContent}</div>
              <div className="flex items-center gap-1 text-xs text-gray-500 mt-2">
                <Loader2 className="w-3 h-3 animate-spin" />
                Generating...
              </div>
            </div>
          </div>
        )}

        {isLoading && !streamingContent && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg p-4 bg-white text-gray-800 shadow-sm border border-gray-200">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                Thinking...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
