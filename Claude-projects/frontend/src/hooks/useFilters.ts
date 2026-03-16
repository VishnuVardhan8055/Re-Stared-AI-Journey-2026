import { create } from 'zustand';
import type { ArticleCategory, VerificationStatus, SourceType } from '@/types/news';

interface FilterState {
  // Source filters
  selectedSourceIds: number[];
  setSelectedSourceIds: (ids: number[]) => void;
  toggleSourceId: (id: number) => void;

  // Category filter
  selectedCategory: ArticleCategory | null;
  setSelectedCategory: (category: ArticleCategory | null) => void;

  // Status filter
  selectedStatus: VerificationStatus | null;
  setSelectedStatus: (status: VerificationStatus | null) => void;

  // Source type filter
  selectedSourceType: SourceType | null;
  setSelectedSourceType: (type: SourceType | null) => void;

  // Score filter
  minScore: number;
  setMinScore: (score: number) => void;

  // Search query
  searchQuery: string;
  setSearchQuery: (query: string) => void;

  // Sorting
  sortBy: 'published_at' | 'created_at' | 'overall_score' | 'views';
  setSortBy: (sort: 'published_at' | 'created_at' | 'overall_score' | 'views') => void;
  sortOrder: 'asc' | 'desc';
  setSortOrder: (order: 'asc' | 'desc') => void;

  // Reset all filters
  resetFilters: () => void;

  // Check if any filters are active
  hasActiveFilters: () => boolean;
}

export const useFilters = create<FilterState>((set, get) => ({
  // Source filters
  selectedSourceIds: [],
  setSelectedSourceIds: (ids) => set({ selectedSourceIds: ids }),
  toggleSourceId: (id) =>
    set((state) => ({
      selectedSourceIds: state.selectedSourceIds.includes(id)
        ? state.selectedSourceIds.filter((sid) => sid !== id)
        : [...state.selectedSourceIds, id],
    })),

  // Category filter
  selectedCategory: null,
  setSelectedCategory: (category) => set({ selectedCategory: category }),

  // Status filter
  selectedStatus: null,
  setSelectedStatus: (status) => set({ selectedStatus: status }),

  // Source type filter
  selectedSourceType: null,
  setSelectedSourceType: (type) => set({ selectedSourceType: type }),

  // Score filter
  minScore: 0,
  setMinScore: (score) => set({ minScore: score }),

  // Search query
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),

  // Sorting
  sortBy: 'published_at',
  setSortBy: (sortBy) => set({ sortBy }),
  sortOrder: 'desc',
  setSortOrder: (sortOrder) => set({ sortOrder }),

  // Reset all filters
  resetFilters: () =>
    set({
      selectedSourceIds: [],
      selectedCategory: null,
      selectedStatus: null,
      selectedSourceType: null,
      minScore: 0,
      searchQuery: '',
      sortBy: 'published_at',
      sortOrder: 'desc',
    }),

  // Check if any filters are active
  hasActiveFilters: () => {
    const state = get();
    return (
      state.selectedSourceIds.length > 0 ||
      state.selectedCategory !== null ||
      state.selectedStatus !== null ||
      state.selectedSourceType !== null ||
      state.minScore > 0 ||
      state.searchQuery.length > 0
    );
  },
}));