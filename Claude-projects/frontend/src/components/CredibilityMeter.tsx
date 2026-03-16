import { cn } from '@/lib/utils';

interface CredibilityMeterProps {
  score: number;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function CredibilityMeter({
  score,
  showLabel = true,
  size = 'md',
}: CredibilityMeterProps) {
  const height = {
    sm: 4,
    md: 6,
    lg: 8,
  };

  const getColor = (s: number) => {
    if (s >= 70) return 'bg-green-500';
    if (s >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      {showLabel && (
        <span className="text-sm font-medium text-muted-foreground">
          Credibility
        </span>
      )}
      <div className="flex-1">
        <div
          className={cn(
            'h-full rounded-full bg-muted',
            `h-${height[size]}`
          )}
        >
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500',
              getColor(score)
            )}
            style={{ width: `${score}%` }}
          />
        </div>
      </div>
      <span className={cn(
        'font-bold',
        {
          'text-green-500': score >= 70,
          'text-yellow-500': score >= 40 && score < 70,
          'text-red-500': score < 40,
        }
      )}>
        {score.toFixed(0)}%
      </span>
    </div>
  );
}