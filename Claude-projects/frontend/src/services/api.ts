import axios from 'axios';
import type {
  Article,
  ArticleListResponse,
  NewsQueryParams,
  RefreshResponse,
  Source,
  VerificationStats,
} from '@/types/news';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// News API
export const newsApi = {
  // Get news articles
  getNews: async (params?: NewsQueryParams) => {
    const response = await api.get<ArticleListResponse>('/news', { params });
    return response.data;
  },

  // Get single article
  getArticle: async (id: number) => {
    const response = await api.get<Article>(`/news/${id}`);
    return response.data;
  },

  // Get trending news
  getTrending: async (limit = 10, hours = 24) => {
    const response = await api.get<Article[]>('/news/trending', {
      params: { limit, hours },
    });
    return response.data;
  },

  // Search news
  searchNews: async (query: string, params?: Omit<NewsQueryParams, 'search'>) => {
    const response = await api.get<ArticleListResponse>('/news/search', {
      params: { q: query, ...params },
    });
    return response.data;
  },

  // Get sources
  getSources: async (typeFilter?: string) => {
    const response = await api.get<Source[]>('/news/sources', {
      params: { type: typeFilter },
    });
    return response.data;
  },

  // Get categories
  getCategories: async () => {
    const response = await api.get<string[]>('/news/categories');
    return response.data;
  },

  // Refresh news (trigger aggregation)
  refreshNews: async () => {
    const response = await api.post<RefreshResponse>('/news/refresh');
    return response.data;
  },

  // Get news stats
  getNewsStats: async () => {
    const response = await api.get('/news/stats');
    return response.data;
  },
};

// Verification API
export const verificationApi = {
  // Verify an article
  verifyArticle: async (articleId: number) => {
    const response = await api.post(`/verification/verify/${articleId}`);
    return response.data;
  },

  // Get verification stats
  getStats: async () => {
    const response = await api.get<VerificationStats>('/verification/stats');
    return response.data;
  },

  // Batch verify articles
  batchVerify: async (limit = 50) => {
    const response = await api.post('/verification/batch-verify', null, {
      params: { limit },
    });
    return response.data;
  },

  // Update source scores
  updateSourceScores: async () => {
    const response = await api.post('/verification/update-sources');
    return response.data;
  },
};

export default api;