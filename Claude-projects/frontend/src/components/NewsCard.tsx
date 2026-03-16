import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { VerificationBadge } from '@/components/VerificationBadge';
import { CredibilityMeter } from '@/components/CredibilityMeter';
import { Badge } from '@/components/ui/badge';
import { ExternalLink, Clock, Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { Article, ArticleCategory } from '@/types/news';

interface NewsCardProps {
  article: Article;
}

const categoryColors: Record<ArticleCategory, string> = {
  news: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  tech: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
  politics: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  business: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  science: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
  health: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
  entertainment: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  sports: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-300',
  world: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
  other: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
};

export function NewsCard({ article }: NewsCardProps) {
  return (
    <Card className="w-full transition-all hover:shadow-lg">
      {article.image_url && (
        <div className="relative h-48 w-full overflow-hidden rounded-t-lg">
          <img
            src={article.image_url}
            alt={article.title}
            className="h-full w-full object-cover"
            loading="lazy"
          />
          <VerificationBadge
            status={article.verification?.status ?? null}
            score={article.verification?.overall_score}
            className="absolute top-2 right-2"
          />
        </div>
      )}

      <CardHeader className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex flex-wrap gap-2">
            <Badge className={categoryColors[article.category]}>
              {article.category}
            </Badge>
            {article.source && (
              <Badge variant="secondary">
                {article.source.name}
              </Badge>
            )}
          </div>
          {!article.image_url && (
            <VerificationBadge
              status={article.verification?.status ?? null}
              score={article.verification?.overall_score}
            />
          )}
        </div>

        <h3 className="text-xl font-semibold leading-tight line-clamp-2">
          {article.title}
        </h3>

        <p className="text-sm text-muted-foreground line-clamp-3">
          {article.summary || article.content}
        </p>
      </CardHeader>

      <CardContent>
        {article.verification && (
          <div className="mb-3">
            <CredibilityMeter score={article.verification.credibility_score} />
          </div>
        )}
      </CardContent>

      <CardFooter className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Clock size={14} />
            {formatDistanceToNow(new Date(article.published_at), {
              addSuffix: true,
            })}
          </div>
          <div className="flex items-center gap-1">
            <Eye size={14} />
            {article.views}
          </div>
        </div>

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
        >
          Read more
          <ExternalLink size={14} />
        </a>
      </CardFooter>
    </Card>
  );
}