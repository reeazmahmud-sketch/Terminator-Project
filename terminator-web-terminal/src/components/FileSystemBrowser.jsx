import React, { useState, useEffect } from 'react';

const FileSystemBrowser = () => {
  const [path, setPath] = useState('.');
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFiles(path);
  }, [path]);

  const fetchFiles = async (currentPath) => {
    try {
      const response = await fetch(`/api/files?path=${encodeURIComponent(currentPath)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setItems(data.files);
      setError(null);
    } catch (e) {
      setError(e.message);
      setItems([]);
    }
  };

  const handleItemClick = (item) => {
    if (item.type === 'directory') {
      setPath(item.path);
    }
  };

  const handleBackClick = () => {
    const parentPath = path.substring(0, path.lastIndexOf('/'));
    setPath(parentPath || '.');
  }

  return (
    <div className="bg-slate-800/60 backdrop-blur-md border border-terminator-blue/30 rounded-lg p-4 glow-border text-white font-mono text-sm h-full overflow-y-auto">
      <h2 className="text-lg font-display text-terminator-blue mb-2">File System Browser</h2>

      <div className="mb-2">
        <button
          onClick={handleBackClick}
          disabled={path === '.'}
          className="px-2 py-1 bg-slate-700 rounded hover:bg-slate-600 disabled:opacity-50"
        >
          Back
        </button>
        <span className="ml-2 text-gray-400">Current Path: {path}</span>
      </div>

      {error && <div className="text-red-500">Error: {error}</div>}

      <ul>
        {items.map((item) => (
          <li
            key={item.name}
            onClick={() => handleItemClick(item)}
            className={`cursor-pointer hover:bg-slate-700 p-1 rounded ${item.type === 'directory' ? 'text-terminator-blue' : ''}`}
          >
            {item.type === 'directory' ? '📁' : '📄'} {item.name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileSystemBrowser;
