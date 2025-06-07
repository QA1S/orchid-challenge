"use client";

import React, { useState } from 'react';
import Image from "next/image";

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [clonedHtml, setClonedHtml] = useState('');
  const [error, setError] = useState('');

  const handleClone = async () => {
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      setError('Please enter a valid URL (including https://)');
      return;
    }

    setLoading(true);
    setError('');
    setClonedHtml('');

    try {
      const response = await fetch('http://localhost:8000/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setClonedHtml(data.html);
    } catch (err: any) {
      setError(`Failed to clone website: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const downloadHtml = () => {
    if (!clonedHtml) return;
    
    const blob = new Blob([clonedHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cloned-website.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="text-4xl">🌸</div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Orchids AI mini
            </h1>
          </div>
          <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
            AI Website Cloner
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-lg max-w-2xl mx-auto">
            Transform any website into a beautiful clone using advanced AI. 
            Simply paste a URL and watch our AI recreate the design aesthetics.
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 mb-8 border border-gray-200 dark:border-slate-700">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Website URL
              </label>
              <input
                id="url-input"
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-4 py-3 border border-gray-300 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-lg bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100 transition-all"
                disabled={loading}
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleClone}
                disabled={loading || !url.trim()}
                className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed font-semibold text-lg transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 shadow-lg"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Cloning...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <span>🎨</span>
                    <span>Clone Website</span>
                  </div>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <div className="flex items-center gap-2">
                <span className="text-red-500 text-xl">⚠️</span>
                <p className="text-red-700 dark:text-red-400 font-medium">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Results Section */}
        {clonedHtml && (
          <div className="space-y-8">
            {/* Preview Section */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              {/* Original Website */}
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-slate-700">
                <div className="bg-gray-50 dark:bg-slate-700 px-6 py-4 border-b border-gray-200 dark:border-slate-600">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <span>🌐</span>
                    Original Website
                  </h3>
                </div>
                <div className="p-6">
                  <div className="bg-gray-100 dark:bg-slate-600 rounded-xl overflow-hidden">
                    <iframe
                      src={url}
                      className="w-full h-96 border-0"
                      title="Original Website"
                      sandbox="allow-same-origin allow-scripts"
                    />
                  </div>
                </div>
              </div>

              {/* Cloned Website */}
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-slate-700">
                <div className="bg-gray-50 dark:bg-slate-700 px-6 py-4 border-b border-gray-200 dark:border-slate-600 flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                    <span>🤖</span>
                    AI Generated Clone
                  </h3>
                  <button
                    onClick={downloadHtml}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                  >
                    <span>📥</span>
                    Download
                  </button>
                </div>
                <div className="p-6">
                  <div className="bg-gray-100 dark:bg-slate-600 rounded-xl overflow-hidden">
                    <iframe
                      srcDoc={clonedHtml}
                      className="w-full h-96 border-0"
                      title="Cloned Website"
                      sandbox="allow-same-origin"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Code Section */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-gray-200 dark:border-slate-700">
              <div className="bg-gray-50 dark:bg-slate-700 px-6 py-4 border-b border-gray-200 dark:border-slate-600 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 flex items-center gap-2">
                  <span>💻</span>
                  Generated HTML Code
                </h3>
                <button
                  onClick={() => navigator.clipboard.writeText(clonedHtml)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                >
                  <span>📋</span>
                  Copy Code
                </button>
              </div>
              <div className="p-6">
                <div className="bg-gray-900 rounded-xl overflow-hidden">
                  <pre className="p-4 overflow-x-auto text-sm">
                    <code className="text-gray-100 font-mono">
                      {clonedHtml}
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 dark:text-gray-400">
          <p className="flex items-center justify-center gap-2">
            <span>Powered by</span>
            <span className="font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Orchids AI mini
            </span>
            <span>🌸</span>
          </p>
        </footer>
      </div>
    </div>
  );
}