import { useState } from 'react';
import { NewsFeed } from './components/NewsFeed';
import { Button } from './components/ui/button';
import { Card, CardContent } from './components/ui/card';
import { Search, Shield, TrendingUp, Menu, X } from 'lucide-react';
import { useFilters } from './hooks/useFilters';
import { useVerificationStats } from './hooks/useNews';

function App() {
  const [currentView, setCurrentView] = useState<'feed' | 'trending' | 'about'>('feed');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { searchQuery, setSearchQuery } = useFilters();
  const { data: stats, isLoading: statsLoading } = useVerificationStats();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Search is already handled by the NewsFeed component through useFilters
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold">VerifiedNews</h1>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              <Button
                variant={currentView === 'feed' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('feed');
                  setMobileMenuOpen(false);
                }}
              >
                News Feed
              </Button>
              <Button
                variant={currentView === 'trending' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('trending');
                  setMobileMenuOpen(false);
                }}
              >
                Trending
              </Button>
              <Button
                variant={currentView === 'about' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('about');
                  setMobileMenuOpen(false);
                }}
              >
                About
              </Button>
            </nav>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <nav className="md:hidden mt-4 flex flex-col gap-2">
              <Button
                variant={currentView === 'feed' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('feed');
                  setMobileMenuOpen(false);
                }}
                className="justify-start"
              >
                News Feed
              </Button>
              <Button
                variant={currentView === 'trending' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('trending');
                  setMobileMenuOpen(false);
                }}
                className="justify-start"
              >
                Trending
              </Button>
              <Button
                variant={currentView === 'about' ? 'default' : 'ghost'}
                onClick={() => {
                  setCurrentView('about');
                  setMobileMenuOpen(false);
                }}
                className="justify-start"
              >
                About
              </Button>
            </nav>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search news..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border bg-background px-10 py-3 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </form>

        {/* Stats Bar */}
        {!statsLoading && stats && (
          <div className="mb-8 grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold">{stats.total_articles}</div>
                <div className="text-xs text-muted-foreground">Total Articles</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{stats.verified}</div>
                <div className="text-xs text-muted-foreground">Verified</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.needs_review}</div>
                <div className="text-xs text-muted-foreground">Needs Review</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.unverified}</div>
                <div className="text-xs text-muted-foreground">Unverified</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-red-600">{stats.misleading}</div>
                <div className="text-xs text-muted-foreground">Misleading</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* View Content */}
        {currentView === 'feed' && <NewsFeed />}

        {currentView === 'trending' && (
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              <h2 className="text-2xl font-bold">Trending News</h2>
            </div>
            <NewsFeed showFilters={false} />
          </div>
        )}

        {currentView === 'about' && (
          <div className="max-w-2xl">
            <Card>
              <CardContent className="p-8 space-y-4">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="h-10 w-10 text-primary" />
                  <h2 className="text-2xl font-bold">About VerifiedNews</h2>
                </div>

                <p className="text-muted-foreground">
                  VerifiedNews is a news aggregation platform that fetches the latest news from
                  multiple sources including Twitter/X, news APIs, RSS feeds, and web scraping.
                </p>

                <h3 className="text-lg font-semibold mt-6">Features</h3>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Real-time news aggregation from multiple sources</li>
                  <li>AI-powered content analysis and verification</li>
                  <li>Credibility scoring and fact-checking</li>
                  <li>Cross-reference verification across sources</li>
                  <li>Filter by category, source, and verification status</li>
                  <li>Trending news section</li>
                </ul>

                <h3 className="text-lg font-semibold mt-6">How Verification Works</h3>
                <p className="text-muted-foreground">
                  Our verification system uses multiple approaches:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li>Source credibility scoring based on historical accuracy</li>
                  <li>AI-powered content analysis to detect potential misinformation</li>
                  <li>Cross-referencing with other news sources</li>
                  <li>Fact-checking against verified claims</li>
                </ul>

                <h3 className="text-lg font-semibold mt-6">Verification Status</h3>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                  <li><span className="text-green-600 font-medium">Verified</span>: High confidence in accuracy</li>
                  <li><span className="text-yellow-600 font-medium">Needs Review</span>: May require human verification</li>
                  <li><span className="text-orange-600 font-medium">Unverified</span>: Not yet verified</li>
                  <li><span className="text-red-600 font-medium">Misleading</span>: Likely false or misleading</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2026 VerifiedNews. Aggregating and verifying news from around the world.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;