import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Plus, Trash2, Calendar, Building2, MapPin, Briefcase } from 'lucide-react';
import { applicationsAPI, metricsAPI, companiesAPI } from '../services/api';
import { format } from 'date-fns';

const EVENT_UI = {
  applied: { label: 'Applied', badge: 'secondary', icon: 'AP' },
  interview_1: { label: 'Interview 1', badge: 'primary', icon: 'INT1' },
  interview_2: { label: 'Interview 2', badge: 'primary', icon: 'INT2' },
  follow_up: { label: 'Follow-up', badge: 'info', icon: 'F/U' },
  offer: { label: 'Offer', badge: 'success', icon: 'OFF' },
  rejection: { label: 'Rejected', badge: 'danger', icon: 'X' },
  closed: { label: 'Closed', badge: 'dark', icon: 'CL' },
  reopen: { label: 'Reopened', badge: 'warning', icon: 'RE' },
};

const STATUS_BADGE = {
  active: 'primary',
  offer: 'success',
  rejected: 'danger',
  closed: 'secondary',
};

export default function ApplicationsPage() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  
  const [metrics, setMetrics] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newApp, setNewApp] = useState({
    company_name: '',
    role_title: '',
    channel: '',
    location: '',
  });
  const [companySuggestions, setCompanySuggestions] = useState([]);

  useEffect(() => {
    loadApplications();
    loadMetrics();
  }, [search, status, offset]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const params = {
        limit,
        offset,
        ...(search && { search }),
        ...(status && { status }),
      };
      const data = await applicationsAPI.list(params);
      setApplications(data.items || []);
      setTotal(data.total || 0);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const data = await metricsAPI.overview();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load metrics:', err);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setOffset(0);
    loadApplications();
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this application? This will also delete its events.')) {
      return;
    }
    try {
      await applicationsAPI.delete(id);
      loadApplications();
      loadMetrics();
    } catch (err) {
      alert('Failed to delete application: ' + err.message);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const app = await applicationsAPI.create(newApp);
      setShowAddForm(false);
      setNewApp({ company_name: '', role_title: '', channel: '', location: '' });
      loadApplications();
      loadMetrics();
      navigate(`/applications/${app.id}`);
    } catch (err) {
      alert('Failed to create application: ' + err.message);
    }
  };

  const handleCompanyInput = async (value) => {
    setNewApp({ ...newApp, company_name: value });
    if (value.length >= 2) {
      try {
        const suggestions = await companiesAPI.suggest(value, 10);
        setCompanySuggestions(suggestions);
      } catch (err) {
        console.error('Failed to load suggestions:', err);
      }
    } else {
      setCompanySuggestions([]);
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search/Filter */}
          <div className="card p-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder="Search company / role"
                      className="input pl-10"
                    />
                  </div>
                </div>
                <div>
                  <select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                    className="input"
                  >
                    <option value="">All status</option>
                    <option value="active">Active</option>
                    <option value="rejected">Rejected</option>
                    <option value="offer">Offer</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div>
                  <button type="submit" className="btn btn-primary w-full">
                    Filter
                  </button>
                </div>
              </div>
            </form>
          </div>

          {/* Applications List */}
          <div className="card">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading...</div>
            ) : applications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No applications found.
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {applications.map((app) => {
                  const eventUI = EVENT_UI[app.current_stage] || {
                    label: app.current_stage,
                    badge: 'secondary',
                    icon: '�?',
                  };
                  const statusBadge = STATUS_BADGE[app.status] || 'secondary';
                  
                  return (
                    <div key={app.id} className="p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <Link
                            to={`/applications/${app.id}`}
                            className="block group"
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <Building2 className="w-4 h-4 text-gray-400 flex-shrink-0" />
                              <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                                {app.company_name} �?{app.role_title}
                              </h3>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-gray-500 ml-6">
                              {app.location && (
                                <div className="flex items-center gap-1">
                                  <MapPin className="w-3 h-3" />
                                  {app.location}
                                </div>
                              )}
                              {app.channel && (
                                <div className="flex items-center gap-1">
                                  <Briefcase className="w-3 h-3" />
                                  {app.channel}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center gap-2 mt-2 ml-6">
                              <span className={`badge badge-${eventUI.badge}`}>
                                {eventUI.icon} {eventUI.label}
                              </span>
                              {app.updated_at && (
                                <span className="text-xs text-gray-400 flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  {formatDate(app.updated_at)}
                                </span>
                              )}
                            </div>
                          </Link>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className={`badge badge-${statusBadge}`}>
                            {app.status}
                          </span>
                          <button
                            onClick={() => handleDelete(app.id)}
                            className="btn btn-outline-danger btn-sm text-xs"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Pagination */}
            {!loading && total > 0 && (
              <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  Total: {total}
                </div>
                <div className="flex gap-2">
                  {offset > 0 && (
                    <button
                      onClick={() => setOffset(Math.max(0, offset - limit))}
                      className="btn btn-outline-secondary btn-sm"
                    >
                      Previous
                    </button>
                  )}
                  {offset + limit < total && (
                    <button
                      onClick={() => setOffset(offset + limit)}
                      className="btn btn-outline-secondary btn-sm"
                    >
                      Next
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Quick Add */}
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Quick Add</h2>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn btn-outline-primary btn-sm"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {showAddForm && (
              <form onSubmit={handleCreate} className="space-y-3">
                <div>
                  <input
                    type="text"
                    value={newApp.company_name}
                    onChange={(e) => handleCompanyInput(e.target.value)}
                    placeholder="Company"
                    required
                    list="companySuggestions"
                    className="input"
                  />
                  <datalist id="companySuggestions">
                    {companySuggestions.map((c) => (
                      <option key={c.id} value={c.name} />
                    ))}
                  </datalist>
                </div>
                <div>
                  <input
                    type="text"
                    value={newApp.role_title}
                    onChange={(e) => setNewApp({ ...newApp, role_title: e.target.value })}
                    placeholder="Role title"
                    required
                    className="input"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    value={newApp.channel}
                    onChange={(e) => setNewApp({ ...newApp, channel: e.target.value })}
                    placeholder="Channel (LinkedIn, etc)"
                    className="input"
                  />
                </div>
                <div>
                  <input
                    type="text"
                    value={newApp.location}
                    onChange={(e) => setNewApp({ ...newApp, location: e.target.value })}
                    placeholder="Location"
                    className="input"
                  />
                </div>
                <button type="submit" className="btn btn-success w-full">
                  Create
                </button>
              </form>
            )}
          </div>

          {/* Metrics */}
          {metrics && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold mb-4">Metrics</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Total applications</span>
                  <span className="font-semibold">{metrics.total_applications || 0}</span>
                </div>
                <div className="border-t border-gray-200 pt-4 space-y-2">
                  {Object.entries(metrics.by_status || {}).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 capitalize">{key}</span>
                      <span className="font-semibold">{value}</span>
                    </div>
                  ))}
                </div>
                <div className="border-t border-gray-200 pt-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Offer rate</span>
                    <span className="font-semibold">
                      {((metrics.offer_rate || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Rejection rate</span>
                    <span className="font-semibold">
                      {((metrics.rejection_rate || 0) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                {metrics.avg_days_to_interview !== null && (
                  <div className="border-t border-gray-200 pt-4 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Avg days to interview</span>
                      <span className="font-semibold">
                        {metrics.avg_days_to_interview?.toFixed(1) || '-'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Avg days to offer</span>
                      <span className="font-semibold">
                        {metrics.avg_days_to_offer?.toFixed(1) || '-'}
                      </span>
                    </div>
                  </div>
                )}
                {metrics.channels && metrics.channels.length > 0 && (
                  <div className="border-t border-gray-200 pt-4">
                    <div className="text-sm text-gray-600 mb-2">By channel</div>
                    {metrics.channels.map((row, idx) => (
                      <div key={idx} className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">{row.channel}</span>
                        <span className="font-semibold">
                          {((row.offer_rate || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}









