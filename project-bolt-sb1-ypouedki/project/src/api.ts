import { createApi } from 'unsplash-js';
import { createClient } from 'pexels';
import type { ImageResult, SearchResults } from './types';

// Note: In a production environment, these should be environment variables
const UNSPLASH_ACCESS_KEY = 'YOUR_UNSPLASH_API_KEY';
const PEXELS_API_KEY = 'YOUR_PEXELS_API_KEY';

const unsplash = createApi({
  accessKey: UNSPLASH_ACCESS_KEY,
});

const pexelsClient = createClient(PEXELS_API_KEY);

export async function searchImages(query: string, page = 1): Promise<SearchResults> {
  try {
    const [unsplashResults, pexelsResults] = await Promise.all([
      unsplash.search.getPhotos({
        query,
        page,
        perPage: 15,
      }),
      pexelsClient.photos.search({ query, page, per_page: 15 })
    ]);

    const images: ImageResult[] = [
      ...unsplashResults.response?.results.map(photo => ({
        id: photo.id,
        url: photo.urls.regular,
        thumb: photo.urls.thumb,
        title: photo.description || photo.alt_description || 'Untitled',
        photographer: photo.user.name,
        source: 'unsplash' as const,
        downloadUrl: photo.links.download
      })) || [],
      ...pexelsResults.photos.map(photo => ({
        id: photo.id.toString(),
        url: photo.src.large,
        thumb: photo.src.small,
        title: photo.alt || 'Untitled',
        photographer: photo.photographer,
        source: 'pexels' as const,
        downloadUrl: photo.src.original
      }))
    ];

    return {
      images,
      hasMore: images.length === 30,
    };
  } catch (error) {
    return {
      images: [],
      hasMore: false,
      error: 'Failed to fetch images. Please try again later.'
    };
  }
}