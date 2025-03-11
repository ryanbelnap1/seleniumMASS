export interface ImageResult {
  id: string;
  url: string;
  thumb: string;
  title: string;
  photographer: string;
  source: 'unsplash' | 'pexels';
  downloadUrl?: string;
}

export interface SearchResults {
  images: ImageResult[];
  hasMore: boolean;
  error?: string;
}