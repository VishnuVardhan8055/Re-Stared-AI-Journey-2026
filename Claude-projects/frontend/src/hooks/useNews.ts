import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { newsApi, verificationApi } from '@/services/api';
import type { Article, ArticleListResponse, NewsQueryParams } from '@/types/news';

const NEWS_QUERY_KEY = 'news';
const ARTICLE_QUERY_KEY = 'article';
const SOURCES_QUERY_KEY = 'sources';
const VERIFICATION_STATS_KEY = 'verification-stats';

export function useNews(params?: NewsQueryParams, enabled = true) {
  return useQuery({
    queryKey: [NEWS_QUERY_KEY, params],
    queryFn: () => newsApi.getNews(params),
    enabled,
    refetchOnWindowFocus: false,
  });
}

export function useArticle(id: number, enabled = true) {
  return useQuery({
    queryKey: [ARTICLE_QUERY_KEY, id],
    queryFn: () => newsApi.getArticle(id),
    enabled,
    refetchOnWindowFocus: false,
  });
}

export function useTrendingNews(limit = 10, hours = 24) {
  return useQuery({
    queryKey: ['trending', limit, hours],
    queryFn: () => newsApi.getTrending(limit, hours),
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  });
}

export function useSearchNews(query: string, params?: Omit<NewsQueryParams, 'search'>) {
  return useQuery({
    queryKey: ['search', query, params],
    queryFn: () => newsApi.searchNews(query, params),
    enabled: query.length > 0,
  });
}

export function useSources(typeFilter?: string) {
  return useQuery({
    queryKey: [SOURCES_QUERY_KEY, typeFilter],
    queryFn: () => newsApi.getSources(typeFilter),
  });
}

export function useRefreshNews() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => newsApi.refreshNews(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NEWS_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: ['trending'] });
    },
  });
}

export function useVerifyArticle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (articleId: number) => verificationApi.verifyArticle(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ARTICLE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [NEWS_QUERY_KEY] });
    },
  });
}

export function useVerificationStats() {
  return useQuery({
    queryKey: [VERIFICATION_STATS_KEY],
    queryFn: () => verificationApi.getStats(),
    refetchInterval: 60 * 1000, // Refresh every minute
  });
}

export function useBatchVerify() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (limit = 50) => verificationApi.batchVerify(limit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VERIFICATION_STATS_KEY] });
      queryClient.invalidateQueries({ queryKey: [ARTICLE_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [NEWS_QUERY_KEY] });
    },
  });
}