import React, { useState, useEffect, useCallback } from 'react';
import { Search, Image, Loader2, Download } from 'lucide-react';
import { searchImages } from './api';
import type { ImageResult } from './types';

function App() {
  const [query, setQuery] = useState('');
  const [images, setImages] = useState<ImageResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);

  const fetchImages = useCallback(async (searchQuery: string, pageNum: number) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const results = await searchImages(searchQuery, pageNum);
      
      if (results.error) {
        setError(results.error);
      } else {
        setImages(prev => pageNum === 1 ? results.images : [...prev, ...results.images]);
      }
    } catch (err) {
      setError('An error occurred while fetching images.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (query) {
      fetchImages(query, page);
    }
  }, [query, page, fetchImages]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    const formData = new FormData(e.target as HTMLFormElement);
    const searchQuery = formData.get('search') as string;
    setQuery(searchQuery);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Image className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Image Search</h1>
            </div>
            <form onSubmit={handleSearch} className="flex-1 max-w-2xl mx-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="search"
                  name="search"
                  placeholder="Search for images..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </form>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image) => (
            <div key={`${image.source}-${image.id}`} className="group relative bg-white rounded-lg shadow-md overflow-hidden">
              <img
                src={image.url}
                alt={image.title}
                className="w-full h-64 object-cover"
              />
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-opacity duration-200" />
              <div className="absolute inset-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex flex-col justify-end">
                <h3 className="text-white font-medium truncate">{image.title}</h3>
                <p className="text-gray-200 text-sm">by {image.photographer}</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-white text-xs bg-black bg-opacity-50 px-2 py-1 rounded">
                    {image.source}
                  </span>
                  {image.downloadUrl && (
                    <a
                      href={image.downloadUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-white hover:text-indigo-200"
                    >
                      <Download className="h-5 w-5" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center mt-8">
            <Loader2 className="h-8 w-8 text-indigo-600 animate-spin" />
          </div>
        )}

        {images.length > 0 && !loading && (
          <div className="flex justify-center mt-8">
            <button
              onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
              Load More
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;