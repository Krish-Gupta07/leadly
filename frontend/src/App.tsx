import React, { useState, useEffect } from 'react';
import { searchLeads, getSearchStatus, getLeads, SearchRequest, SearchJobStatus, Lead } from './services/api';
import './App.css';

function App() {
  const [subreddits, setSubreddits] = useState<string>('forhire, freelance, slavelabour');
  const [query, setQuery] = useState<string>('I am a freelance graphic designer and a full stack web developer looking for potential clients who need design or/and development services.');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [jobStatus, setJobStatus] = useState<SearchJobStatus | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoadingLeads, setIsLoadingLeads] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'search' | 'leads'>('search');

  // Load initial leads when component mounts
  useEffect(() => {
    loadLeads();
  }, []);

  // Poll for job status updates
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    
    if (jobStatus && (jobStatus.status === 'pending' || jobStatus.status === 'processing')) {
      intervalId = setInterval(async () => {
        try {
          const updatedStatus = await getSearchStatus(jobStatus.job_id);
          setJobStatus(updatedStatus);
          
          // If job is completed, fetch the actual leads
          if (updatedStatus.status === 'completed') {
            await loadLeads();
          }
        } catch (error) {
          console.error('Error fetching job status:', error);
          if (intervalId) clearInterval(intervalId);
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobStatus]);

  const loadLeads = async () => {
    setIsLoadingLeads(true);
    try {
      const fetchedLeads = await getLeads();
      setLeads(fetchedLeads);
    } catch (error) {
      console.error('Error loading leads:', error);
    } finally {
      setIsLoadingLeads(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);
    setJobStatus(null);
    
    try {
      // Parse subreddits from comma-separated string
      const subredditList = subreddits
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      const searchRequest: SearchRequest = {
        subreddits: subredditList,
        user_query: query,
        limit_per_subreddit: 10
      };
      
      const result = await searchLeads(searchRequest);
      
      // Initialize job status
      const initialStatus: SearchJobStatus = {
        job_id: result.job_id,
        status: 'pending',
        progress: 0,
        results: {
          posts_processed: 0,
          comments_processed: 0,
          leads_found: 0
        },
        error: null
      };
      
      setJobStatus(initialStatus);
    } catch (error: any) {
      console.error('Search error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred while searching for leads.';
      setJobStatus({
        job_id: '',
        status: 'failed',
        progress: 0,
        results: {
          posts_processed: 0,
          comments_processed: 0,
          leads_found: 0
        },
        error: errorMessage
      });
    } finally {
      setIsSearching(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'failed': return '#ef4444';
      case 'processing': return '#f59e0b';
      default: return '#6366f1';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1 className="app-title">Leadly</h1>
          <p className="app-subtitle">Find potential leads on Reddit</p>
        </div>
      </header>
      
      <main className="App-main">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            Search
          </button>
          <button 
            className={`tab ${activeTab === 'leads' ? 'active' : ''}`}
            onClick={() => setActiveTab('leads')}
          >
            Leads ({leads.length})
          </button>
        </div>
        
        {activeTab === 'search' ? (
          <div className="tab-content">
            <form className="search-form" onSubmit={handleSearch}>
              <div className="form-group">
                <label htmlFor="subreddits">Subreddits</label>
                <input
                  type="text"
                  id="subreddits"
                  value={subreddits}
                  onChange={(e) => setSubreddits(e.target.value)}
                  placeholder="forhire, freelance, slavelabour"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label htmlFor="query">Your Service Query</label>
                <textarea
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="I am a freelance graphic designer and a full stack web developer looking for potential clients who need design or/and development services."
                  className="form-textarea"
                  rows={4}
                />
              </div>
              <button 
                type="submit" 
                className="search-button"
                disabled={isSearching}
              >
                {isSearching ? 'Searching...' : 'Find Leads'}
              </button>
            </form>
            
            {jobStatus && (
              <div className="job-status-card">
                <div className="job-header">
                  <span 
                    className="status-badge" 
                    style={{ backgroundColor: getStatusColor(jobStatus.status) }}
                  >
                    {jobStatus.status}
                  </span>
                  <span className="job-id">Job: {jobStatus.job_id.substring(0, 12)}...</span>
                </div>
                
                {jobStatus.status !== 'failed' ? (
                  <div className="progress-section">
                    <div className="progress-bar-container">
                      <div 
                        className="progress-bar" 
                        style={{ width: `${jobStatus.progress}%`, backgroundColor: getStatusColor(jobStatus.status) }}
                      ></div>
                    </div>
                    <div className="progress-text">{jobStatus.progress}%</div>
                  </div>
                ) : null}
                
                {jobStatus.results && jobStatus.status === 'completed' && (
                  <div className="results-grid">
                    <div className="result-item">
                      <span className="result-label">Posts</span>
                      <span className="result-value">{jobStatus.results.posts_processed}</span>
                    </div>
                    <div className="result-item">
                      <span className="result-label">Comments</span>
                      <span className="result-value">{jobStatus.results.comments_processed}</span>
                    </div>
                    <div className="result-item">
                      <span className="result-label">Leads</span>
                      <span className="result-value">{jobStatus.results.leads_found}</span>
                    </div>
                  </div>
                )}
                
                {jobStatus.error && (
                  <div className="error-message">
                    {jobStatus.error}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="tab-content">
            <div className="leads-header">
              <h2>Found Leads</h2>
              <button 
                className="refresh-button" 
                onClick={loadLeads}
                disabled={isLoadingLeads}
              >
                {isLoadingLeads ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            
            {isLoadingLeads ? (
              <div className="loading">Loading leads...</div>
            ) : leads.length > 0 ? (
              <div className="leads-grid">
                {leads.map((lead) => (
                  <div key={lead.id} className="lead-card">
                    <h3 className="lead-title">{lead.title}</h3>
                    <p className="lead-description">{lead.post_text}</p>
                    <div className="lead-footer">
                      <span className="lead-subreddit">r/{lead.subreddit_name}</span>
                      <a 
                        href={lead.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="lead-link"
                      >
                        View
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-leads">
                <p>No leads found yet. Run a search to find potential leads.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
