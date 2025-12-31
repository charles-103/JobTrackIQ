import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Applications API
export const applicationsAPI = {
  list: async (params = {}) => {
    const response = await api.get('/applications', { params });
    return response.data;
  },
  
  get: async (id) => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/applications', data);
    return response.data;
  },
  
  delete: async (id) => {
    await api.delete(`/applications/${id}`);
  },
};

// Events API
export const eventsAPI = {
  list: async (applicationId) => {
    const response = await api.get(`/applications/${applicationId}/events`);
    return response.data;
  },
  
  create: async (applicationId, data) => {
    const response = await api.post(`/applications/${applicationId}/events`, data);
    return response.data;
  },
  
  delete: async (eventId) => {
    await api.delete(`/events/${eventId}`);
  },
};

// Jobs API
export const jobsAPI = {
  list: async (params = {}) => {
    const cleanParams = {};
    if (params.search) cleanParams.search = params.search;
    if (params.location) cleanParams.location = params.location;
    if (params.skills) cleanParams.skills = params.skills;
    if (Number.isInteger(params.limit)) cleanParams.limit = params.limit;
    if (Number.isInteger(params.offset)) cleanParams.offset = params.offset;
    
    const response = await api.get('/jobs', { params: cleanParams });
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/jobs', data);
    return response.data;
  },
  
  toApplication: async (jobId) => {
    const response = await api.post(`/jobs/${jobId}/to-application`);
    return response.data;
  },
};

// Ingest API
const baseUrl = API_BASE_URL.replace('/api/v1', '');

const ingestViaForm = async (endpoint, formData) => {
  const response = await fetch(`${baseUrl}${endpoint}`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Import failed');
  }
  
  return { success: true };
};

export const ingestAPI = {
  smart: async (companyName, fetchJd = false) => {
    const formData = new FormData();
    formData.append('company_name', companyName);
    if (fetchJd) {
      formData.append('fetch_jd', 'on');
    }
    return ingestViaForm('/ui/ingest/smart', formData);
  },
  
  // Legacy method kept for compatibility (optional)
  greenhouse: async (boardToken, companyName, fetchJd = false) => {
    const formData = new FormData();
    formData.append('board_token', boardToken);
    formData.append('company_name', companyName);
    if (fetchJd) {
      formData.append('fetch_jd', 'on');
    }
    return ingestViaForm('/ui/ingest/greenhouse', formData);
  },
  
  lever: async (site, companyName) => {
    const formData = new FormData();
    formData.append('site', site);
    formData.append('company_name', companyName);
    return ingestViaForm('/ui/ingest/lever', formData);
  },
  
  smartrecruiters: async (companyIdentifier, companyName) => {
    const formData = new FormData();
    formData.append('company_identifier', companyIdentifier);
    formData.append('company_name', companyName);
    return ingestViaForm('/ui/ingest/smartrecruiters', formData);
  },
  
  workday: async (careersSiteUrl, companyName) => {
    const formData = new FormData();
    formData.append('careers_site_url', careersSiteUrl);
    formData.append('company_name', companyName);
    return ingestViaForm('/ui/ingest/workday', formData);
  },
};

// Companies API
export const companiesAPI = {
  suggest: async (query, limit = 10) => {
    const response = await api.get('/companies/suggest', {
      params: { q: query, limit },
    });
    return response.data;
  },
};

// Metrics API
export const metricsAPI = {
  overview: async () => {
    const response = await api.get('/metrics/overview');
    return response.data;
  },
};

export default api;






