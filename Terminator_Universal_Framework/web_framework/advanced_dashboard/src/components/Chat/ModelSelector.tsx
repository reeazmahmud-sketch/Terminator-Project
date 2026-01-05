import { Settings } from 'lucide-react';

interface ModelSelectorProps {
  selectedProvider: string;
  selectedModel: string;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
  apiKeys: Array<{ provider: string; key_name: string }>;
}

const PROVIDERS = {
  openai: {
    name: 'OpenAI',
    models: ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'],
  },
  anthropic: {
    name: 'Anthropic',
    models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
  },
};

export function ModelSelector({
  selectedProvider,
  selectedModel,
  onProviderChange,
  onModelChange,
  apiKeys,
}: ModelSelectorProps) {
  const availableProviders = Object.keys(PROVIDERS).filter((provider) =>
    apiKeys.some((key) => key.provider === provider && key.provider)
  );

  const availableModels = PROVIDERS[selectedProvider as keyof typeof PROVIDERS]?.models || [];

  function handleProviderChange(provider: string) {
    onProviderChange(provider);
    const models = PROVIDERS[provider as keyof typeof PROVIDERS]?.models || [];
    if (models.length > 0) {
      onModelChange(models[0]);
    }
  }

  if (availableProviders.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
        <div className="flex items-center gap-2 mb-2">
          <Settings className="w-4 h-4" />
          <span className="font-medium">No API Keys Configured</span>
        </div>
        <p>Please add your API keys in the Profile page to start using the chat.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Settings className="w-4 h-4 text-gray-600" />
        <h3 className="font-medium text-gray-800">Model Settings</h3>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            AI Provider
          </label>
          <select
            value={selectedProvider}
            onChange={(e) => handleProviderChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {availableProviders.map((provider) => (
              <option key={provider} value={provider}>
                {PROVIDERS[provider as keyof typeof PROVIDERS].name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
