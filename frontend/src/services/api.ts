import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 second timeout
});

// Add a request interceptor to include API key
api.interceptors.request.use((config) => {
  // Get API key from localStorage (in a real app, this would be more secure)
  const apiKey = localStorage.getItem('leadly-api-key') || 'dev-key';
  if (apiKey) {
    config.headers.Authorization = `Bearer ${apiKey}`;
  }
  return config;
});

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export interface Lead {
  id: number;
  post_id: string;
  title: string;
  post_text: string | null;
  url: string;
  subreddit_name: string;
  created_at: string;
  updated_at: string;
}

export interface SearchResult {
  message: string;
  job_id: string;
}

export interface SearchJobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results: {
    posts_processed: number;
    comments_processed: number;
    leads_found: number;
  };
  error: string | null;
}

export interface SearchRequest {
  subreddits: string[];
  limit_per_subreddit?: number;
  keywords?: string[];
  user_query: string;
}

export const searchLeads = async (request: SearchRequest): Promise<SearchResult> => {
  const response = await api.post('/api/v1/reddit/search', request);
  return response.data;
};

export const getSearchStatus = async (jobId: string): Promise<SearchJobStatus> => {
  const response = await api.get(`/api/v1/reddit/search/${jobId}`);
  return response.data;
};

export const getLeads = async (): Promise<Lead[]> => {
  const response = await api.get('/api/v1/leads');
  return response.data.leads;
};

export const getSubreddits = async (): Promise<string[]> => {
  const response = await api.get('/api/v1/config/subreddits');
  return response.data.subreddits;
};

export const addSubreddit = async (subreddit: string): Promise<void> => {
  await api.post('/api/v1/config/subreddits', { subreddit });
};

// Function to set API key
export const setApiKey = (apiKey: string): void => {
  localStorage.setItem('leadly-api-key', apiKey);
};

// Function to get API key
export const getApiKey = (): string | null => {
  return localStorage.getItem('leadly-api-key');
};

// Test connectivity function
export const testConnectivity = async (): Promise<boolean> => {
  try {
    const response = await api.get('/api/v1/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
};

export default api;