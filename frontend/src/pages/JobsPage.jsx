import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, ExternalLink, Building2, MapPin, Calendar } from 'lucide-react';
import { jobsAPI, ingestAPI } from '../services/api';
import { format } from 'date-fns';

export default function JobsPage() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [skillsFilter, setSkillsFilter] = useState('');
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  
  const [showImportForm, setShowImportForm] = useState(false);
  const [importData, setImportData] = useState({
    company_name: '',
    fetch_jd: false,
  });
  const [importLoading, setImportLoading] = useState(false);
  
  const [showManualForm, setShowManualForm] = useState(false);
  const [newJob, setNewJob] = useState({
    company_name: '',
    role_title: '',
    location: '',
    url: '',
    jd_text: '',
  });

  useEffect(() => {
    loadJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offset]);
  
  useEffect(() => {
    // Reset to first page when filters change
    if (offset > 0) {
      setOffset(0);
    } else {
      loadJobs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, locationFilter, skillsFilter]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const params = { limit, offset };
      if (search) params.search = search;
      if (locationFilter) params.location = locationFilter;
      if (skillsFilter) params.skills = skillsFilter;
      
      const data = await jobsAPI.list(params);
      // Handle both old format (array) and new format (object with total/items)
      if (Array.isArray(data)) {
        setJobs(data);
        setTotal(data.length);
      } else {
        setJobs(data?.items || []);
        setTotal(data?.total || 0);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setOffset(0);
    // loadJobs will be called by useEffect
  };

  const handleSmartImport = async (e) => {
    e.preventDefault();
    try {
      setImportLoading(true);
      await ingestAPI.smart(importData.company_name, importData.fetch_jd);
      setImportData({ company_name: '', fetch_jd: false });
      setShowImportForm(false);
      loadJobs();
    } catch (err) {
      alert('Import failed: ' + err.message);
    } finally {
      setImportLoading(false);
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    try {
      await jobsAPI.create(newJob);
      setNewJob({ company_name: '', role_title: '', location: '', url: '', jd_text: '' });
      setShowManualForm(false);
      loadJobs();
    } catch (err) {
      alert('Failed to create job: ' + err.message);
    }
  };

  const handleCreateApplication = async (jobId) => {
    try {
      const application = await jobsAPI.toApplication(jobId);
      navigate(`/applications/${application.id}`);
      loadJobs();
    } catch (err) {
      alert('Failed to create application: ' + err.message);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return dateString;
    }
  };

  const resetAndLoad = (newOffset) => {
    setOffset(newOffset);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Job Inbox</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Forms */}
        <div className="space-y-4">
          {/* Smart Import */}
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Import Jobs</h2>
              <button
                onClick={() => setShowImportForm(!showImportForm)}
                className="btn btn-outline-primary btn-sm"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {showImportForm && (
              <form onSubmit={handleSmartImport} className="space-y-3">
                <div>
                  <input
                    type="text"
                    value={importData.company_name}
                    onChange={(e) => setImportData({ ...importData, company_name: e.target.value })}
                    placeholder="Company name (e.g. Airbnb, Google, Microsoft)"
                    required
                    className="input"
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="fetchJd"
                    checked={importData.fetch_jd}
                    onChange={(e) => setImportData({ ...importData, fetch_jd: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="fetchJd" className="ml-2 text-sm text-gray-600">
                    Fetch full JD (slower)
                  </label>
                </div>
                <button
                  type="submit"
                  disabled={importLoading}
                  className="btn btn-primary w-full"
                >
                  {importLoading ? 'Importing...' : 'Start import'}
                </button>
              </form>
            )}
            <p className="text-xs text-gray-500 mt-3">
              Tip: Tries Greenhouse / Lever / SmartRecruiters automatically and pulls JDs when available.
            </p>
          </div>

          {/* Manual Add */}
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Add Job Posting (Manual)</h2>
              <button
                onClick={() => setShowManualForm(!showManualForm)}
                className="btn btn-outline-primary btn-sm"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {showManualForm && (
              <form onSubmit={handleCreateJob} className="space-y-3">
                <div>
                  <input
                    type="text"
                    value={newJob.company_name}
                    onChange={(e) => setNewJob({ ...newJob, company_name: e.target.value })}
                    placeholder="Company"
                    required
                    className="input"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    value={newJob.role_title}
                    onChange={(e) => setNewJob({ ...newJob, role_title: e.target.value })}
                    placeholder="Role title"
                    required
                    className="input"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    value={newJob.location}
                    onChange={(e) => setNewJob({ ...newJob, location: e.target.value })}
                    placeholder="Location (optional)"
                    className="input"
                  />
                </div>
                <div>
                  <input
                    type="url"
                    value={newJob.url}
                    onChange={(e) => setNewJob({ ...newJob, url: e.target.value })}
                    placeholder="Job URL (optional)"
                    className="input"
                  />
                </div>
                <div>
                  <textarea
                    value={newJob.jd_text}
                    onChange={(e) => setNewJob({ ...newJob, jd_text: e.target.value })}
                    placeholder="Paste JD text (optional)"
                    rows={6}
                    className="input"
                  />
                </div>
                <button type="submit" className="btn btn-primary w-full">
                  Save to Inbox
                </button>
              </form>
            )}
            <p className="text-xs text-gray-500 mt-3">
              Tip: This avoids anti-bot issues and still lets you build a job dataset.
            </p>
          </div>
        </div>

        {/* Right Column - Jobs List */}
        <div className="card p-6">
          <form onSubmit={handleSearch} className="mb-4 space-y-3">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search company / role / keyword"
                  className="input pl-10"
                />
              </div>
              <button type="submit" className="btn btn-primary">
                Search
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <div>
                <input
                  type="text"
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                  placeholder="Filter by location (e.g. San Francisco, New York)"
                  className="input"
                />
              </div>
              <div>
                <input
                  type="text"
                  value={skillsFilter}
                  onChange={(e) => setSkillsFilter(e.target.value)}
                  placeholder="Filter by skills (e.g. python, react, aws)"
                  className="input"
                />
              </div>
            </div>
          </form>

          <div className="text-sm text-gray-600 mb-4">
            Total: {total} jobs | Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit) || 1}
          </div>

          {loading ? (
            <div className="text-center text-gray-500 py-8">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">No job postings yet.</div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => {
                const jdPreview = job.processed_jd || job.jd_text;
                const showPreview = jdPreview && jdPreview.length > 0;
                return (
                  <div
                    key={job.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start gap-3 mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Building2 className="w-4 h-4 text-gray-400" />
                          <h3 className="font-semibold text-gray-900">
                            {job.company_name} - {job.role_title}
                          </h3>
                        </div>
                        {job.location && (
                          <div className="flex items-center gap-1 text-sm text-gray-600 ml-6 mb-1">
                            <MapPin className="w-3 h-3" />
                            {job.location}
                          </div>
                        )}
                        {job.key_skills && job.key_skills.length > 0 && (
                          <div className="ml-6 mb-2 flex flex-wrap gap-1">
                            {job.key_skills.slice(0, 8).map((skill, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {skill}
                              </span>
                            ))}
                            {job.key_skills.length > 8 && (
                              <span className="text-xs text-gray-500">
                                +{job.key_skills.length - 8} more
                              </span>
                            )}
                          </div>
                        )}
                        {job.url && (
                          <div className="ml-6 mb-1">
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
                            >
                              <ExternalLink className="w-3 h-3" />
                              View Job
                            </a>
                          </div>
                        )}
                        {job.created_at && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 ml-6">
                            <Calendar className="w-3 h-3" />
                            Saved: {formatDate(job.created_at)}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => handleCreateApplication(job.id)}
                        className="btn btn-success btn-sm whitespace-nowrap"
                      >
                        Create Application
                      </button>
                    </div>
                    {showPreview && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-sm text-gray-600 line-clamp-3">
                          {jdPreview.length > 300 ? jdPreview.substring(0, 300) + '...' : jdPreview}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
          {!loading && total > 0 && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                Showing {offset + 1}-{Math.min(total, offset + jobs.length)} of {total} jobs
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => resetAndLoad(0)}
                  disabled={offset === 0}
                  className="btn btn-outline-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  First
                </button>
                {offset > 0 && (
                  <button
                    onClick={() => resetAndLoad(Math.max(0, offset - limit))}
                    className="btn btn-outline-secondary btn-sm"
                  >
                    Previous
                  </button>
                )}
                {offset + limit < total && (
                  <button
                    onClick={() => resetAndLoad(offset + limit)}
                    className="btn btn-outline-secondary btn-sm"
                  >
                    Next
                  </button>
                )}
                <button
                  onClick={() => resetAndLoad(Math.max(0, Math.floor((total - 1) / limit) * limit))}
                  disabled={offset + limit >= total}
                  className="btn btn-outline-secondary btn-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Last
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}



