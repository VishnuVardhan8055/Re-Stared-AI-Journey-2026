import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { X, ChevronDown, ChevronUp } from 'lucide-react';
import { useSources } from '@/hooks/useNews';
import type { SourceType } from '@/types/news';

interface SourceFilterProps {
  selectedIds: number[];
  onToggle: (id: number) => void;
  onClear: () => void;
}

export function SourceFilter({ selectedIds, onToggle, onClear }: SourceFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [typeFilter, setTypeFilter] = useState<SourceType | null>(null);
  const { data: sources, isLoading } = useSources(typeFilter ?? undefined);

  const typeColors: Record<SourceType, string> = {
    twitter: 'bg-blue-500',
    rss: 'bg-green-500',
    scraper: 'bg-purple-500',
    api: 'bg-orange-500',
  };

  const filteredSources = sources?.filter(
    (s) => !typeFilter || s.type === typeFilter
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Filter by Source</CardTitle>
          <div className="flex items-center gap-2">
            {selectedIds.length > 0 && (
              <Button variant="outline" size="sm" onClick={onClear}>
                <X size={14} className="mr-1" />
                Clear ({selectedIds.length})
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp size={16} />
              ) : (
                <ChevronDown size={16} />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent>
          {/* Source type filter */}
          <div className="flex gap-2 mb-4">
            <Button
              variant={typeFilter === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTypeFilter(null)}
            >
              All
            </Button>
            <Button
              variant={typeFilter === 'twitter' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTypeFilter('twitter')}
            >
              Twitter
            </Button>
            <Button
              variant={typeFilter === 'rss' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTypeFilter('rss')}
            >
              RSS
            </Button>
            <Button
              variant={typeFilter === 'scraper' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTypeFilter('scraper')}
            >
              Web
            </Button>
            <Button
              variant={typeFilter === 'api' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTypeFilter('api')}
            >
              API
            </Button>
          </div>

          {/* Source list */}
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Loading sources...</div>
          ) : filteredSources && filteredSources.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {filteredSources.map((source) => (
                <Badge
                  key={source.id}
                  variant={selectedIds.includes(source.id) ? 'default' : 'outline'}
                  className="cursor-pointer"
                  onClick={() => onToggle(source.id)}
                >
                  <div
                    className={`w-2 h-2 rounded-full ${typeColors[source.type]} mr-2`}
                  />
                  {source.name}
                  {source.is_verified && (
                    <span className="ml-1 text-yellow-400">✓</span>
                  )}
                </Badge>
              ))}
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">No sources found</div>
          )}
        </CardContent>
      )}
    </Card>
  );
}