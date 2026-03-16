// Source types
export type SourceType = 'twitter' | 'rss' | 'scraper' | 'api';

export interface Source {
  id: number;
  name: string;
  url: string;
  type: SourceType;
  credibility_score: number;
  is_verified: boolean;
  description: string | null;
  domain: string | null;
  last_fetched_at: string | null;
  created_at: string;
  updated_at: string | null;
}

// Article types
export type ArticleCategory = 'news' | 'tech' | 'politics' | 'business' | 'science' | 'health' | 'entertainment' | 'sports' | 'world' | 'other';

export type VerificationStatus = 'verified' | 'needs_review' | 'unverified' | 'misleading';

export interface VerificationDetail {
  cross_check_score: number;
  cross_check_count: number;
  credibility_score: number;
  ai_analysis: Record<string, unknown> | null;
  ai_sentiment: string | null;
  fact_check_result: Record<string, unknown> | null;
  fact_check_rating: string | null;
  overall_score: number;
  status: VerificationStatus;
  verified_at: string | null;
}

export interface Article {
  id: number;
  title: string;
  content: string;
  summary: string | null;
  url: string;
  published_at: string;
  source_id: number;
  category: ArticleCategory;
  author: string | null;
  image_url: string | null;
  views: number;
  created_at: string;
  updated_at: string | null;
  source: Source | null;
  verification: VerificationDetail | null;
}

// API Response types
export interface ArticleListResponse {
  articles: Article[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface NewsQueryParams {
  page?: number;
  per_page?: number;
  source_id?: number;
  category?: ArticleCategory;
  status?: VerificationStatus;
  search?: string;
  min_score?: number;
  sort_by?: 'published_at' | 'created_at' | 'overall_score' | 'views';
  sort_order?: 'asc' | 'desc';
}

export interface RefreshResponse {
  message: string;
  articles_added: number;
  articles_updated: number;
  sources_processed: number;
}

export interface VerificationStats {
  total_articles: number;
  verified: number;
  needs_review: number;
  unverified: number;
  misleading: number;
  average_score: number;
}