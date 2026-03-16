import { useState } from 'react';
import { NewsCard } from './NewsCard';
import { SourceFilter } from './SourceFilter';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { useNews, useRefreshNews } from '@/hooks/useNews';
import { useFilters } from '@/hooks/useFilters';
import { Loader2, RefreshCw } from 'lucide-react';
import type { NewsQueryParams } from '@/types/news';

interface NewsFeedProps {
  showFilters?: boolean;
}

export function NewsFeed({ showFilters = true }: NewsFeedProps) {
  const [page, setPage] = useState(1);
  const {
    searchQuery,
    selectedCategory,
    selectedStatus,
    selectedSourceIds,
    minScore,
    sortBy,
    sortOrder,
    hasActiveFilters,
    resetFilters,
  } = useFilters();

  const params: NewsQueryParams = {
    page,
    per_page: 12,
    ...(searchQuery && { search: searchQuery }),
    ...(selectedCategory && { category: selectedCategory }),
    ...(selectedStatus && { status: selectedStatus }),
    ...(selectedSourceIds.length > 0 && {
      source_id: selectedSourceIds[0], // API only supports single source
    }),
    ...(minScore > 0 && { min_score: minScore }),
    sort_by: sortBy,
    sort_order: sortOrder,
  };

  const { data, isLoading, error, refetch } = useNews(params);
  const refreshNews = useRefreshNews();
  const { mutate: refresh, isPending: isRefreshing } = refreshNews;

  const handleRefresh = () => {
    refresh();
    refetch();
  };

  const handleLoadMore = () => {
    if (data && data.page < data.total_pages) {
      setPage((p) => p + 1);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">News Feed</h1>
        <div className="flex items-center gap-2">
          {hasActiveFilters() && (
            <Button variant="outline" onClick={resetFilters}>
              Clear Filters
            </Button>
          )}
          <Button onClick={handleRefresh} disabled={isRefreshing}>
            {isRefreshing ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Source Filter */}
      {showFilters && (
        <SourceFilter
          selectedIds={selectedSourceIds}
          onToggle={(id) => {
            const ids = selectedSourceIds.includes(id)
              ? selectedSourceIds.filter((i) => i !== id)
              : [...selectedSourceIds, id];
            useFilters.getState().setSelectedSourceIds(ids);
            setPage(1);
          }}
          onClear={() => {
            useFilters.getState().setSelectedSourceIds([]);
            setPage(1);
          }}
        />
      )}

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="p-6">
            <p className="text-destructive">Error loading news. Please try again.</p>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {isLoading && page === 1 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : null}

      {/* Empty State */}
      {!isLoading && (!data || data.articles.length === 0) ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-muted-foreground">No articles found.</p>
            {hasActiveFilters() && (
              <p className="text-sm text-muted-foreground mt-2">
                Try adjusting your filters.
              </p>
            )}
          </CardContent>
        </Card>
      ) : null}

      {/* News Cards */}
      {data && data.articles.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.articles.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>

          {/* Load More */}
          {data.page < data.total_pages && (
            <div className="flex justify-center pt-6">
              <Button
                variant="outline"
                onClick={handleLoadMore}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  'Load More'
                )}
              </Button>
            </div>
          )}

          {/* Footer Info */}
          <div className="text-center text-sm text-muted-foreground">
            Showing {data.articles.length} of {data.total} articles
            (Page {data.page} of {data.total_pages})
          </div>
        </>
      )}
    </div>
  );
}