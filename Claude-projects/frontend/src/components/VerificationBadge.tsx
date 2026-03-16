import { Badge } from '@/components/ui/badge';
import { Shield, ShieldAlert, ShieldCheck, ShieldX } from 'lucide-react';
import type { VerificationStatus } from '@/types/news';

interface VerificationBadgeProps {
  status: VerificationStatus | null;
  score?: number;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function VerificationBadge({
  status,
  score,
  showScore = false,
  size = 'md',
}: VerificationBadgeProps) {
  if (!status) {
    return null;
  }

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const iconSize = {
    sm: 12,
    md: 14,
    lg: 16,
  };

  const variants: Record<VerificationStatus, 'verified' | 'needs-review' | 'unverified' | 'misleading'> = {
    verified: 'verified',
    needs_review: 'needs-review',
    unverified: 'unverified',
    misleading: 'misleading',
  };

  const icons: Record<VerificationStatus, React.ReactNode> = {
    verified: <ShieldCheck size={iconSize[size]} className="mr-1" />,
    needs_review: <ShieldAlert size={iconSize[size]} className="mr-1" />,
    unverified: <Shield size={iconSize[size]} className="mr-1" />,
    misleading: <ShieldX size={iconSize[size]} className="mr-1" />,
  };

  const labels: Record<VerificationStatus, string> = {
    verified: 'Verified',
    needs_review: 'Needs Review',
    unverified: 'Unverified',
    misleading: 'Misleading',
  };

  return (
    <Badge variant={variants[status]} className={sizeClasses[size]}>
      {icons[status]}
      {labels[status]}
      {showScore && score !== undefined && ` (${score.toFixed(0)})`}
    </Badge>
  );
}