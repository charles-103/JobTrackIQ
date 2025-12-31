import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Trash2, Plus, X } from 'lucide-react';
import { applicationsAPI, eventsAPI } from '../services/api';
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

export default function ApplicationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEvent, setNewEvent] = useState({
    event_type: '',
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [appData, eventsData] = await Promise.all([
        applicationsAPI.get(id),
        eventsAPI.list(id),
      ]);
      setApplication(appData);
      setEvents(eventsData || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickEvent = async (eventType) => {
    try {
      await eventsAPI.create(id, {
        event_type: eventType,
        notes: eventType === 'follow_up' ? 'sent follow-up' : '',
      });
      loadData();
    } catch (err) {
      alert('Failed to add event: ' + err.message);
    }
  };

  const handleAddEvent = async (e) => {
    e.preventDefault();
    try {
      await eventsAPI.create(id, newEvent);
      setNewEvent({ event_type: '', notes: '' });
      setShowAddForm(false);
      loadData();
    } catch (err) {
      alert('Failed to add event: ' + err.message);
    }
  };

  const handleDeleteEvent = async (eventId) => {
    if (!window.confirm('Delete this event?')) {
      return;
    }
    try {
      await eventsAPI.delete(eventId);
      loadData();
    } catch (err) {
      alert('Failed to delete event: ' + err.message);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return format(new Date(dateString), 'MMM d, yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !application) {
    return (
      <div className="space-y-4">
        <Link to="/" className="btn btn-outline-secondary">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Link>
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error || 'Application not found'}
        </div>
      </div>
    );
  }

  const isFinal = ['offer', 'rejected', 'closed'].includes(application.status);
  const stageUI = EVENT_UI[application.current_stage] || {
    label: application.current_stage,
    icon: '•',
    badge: 'secondary',
  };

  return (
    <div className="space-y-6">
      <Link to="/" className="btn btn-outline-secondary inline-flex items-center">
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back
      </Link>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          {/* Application Card */}
          <div className="card p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {application.company_name} - {application.role_title}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-4">
              {application.location && (
                <span className="flex items-center gap-1"> Location: {application.location}
                </span>
              )}
              {application.channel && (
                <span className="flex items-center gap-1"> Channel: {application.channel}
                </span>
              )}
              <span className={`badge badge-${stageUI.badge}`}>
                {application.status}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Stage:</span>
              <span className={`badge badge-${stageUI.badge}`}>
                {stageUI.icon} {stageUI.label}
              </span>
            </div>
          </div>

          {/* Quick Events */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold mb-4">Quick Events</h2>
            {isFinal ? (
              <button
                onClick={() => handleQuickEvent('reopen')}
                className="btn btn-warning"
              >
                Reopen
              </button>
            ) : (
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleQuickEvent('interview_1')}
                  className="btn btn-outline-primary"
                >
                  Interview 1
                </button>
                <button
                  onClick={() => handleQuickEvent('interview_2')}
                  className="btn btn-outline-primary"
                >
                  Interview 2
                </button>
                <button
                  onClick={() => handleQuickEvent('follow_up')}
                  className="btn btn-outline-secondary"
                >
                  Follow-up
                </button>
                <button
                  onClick={() => handleQuickEvent('offer')}
                  className="btn btn-outline-success"
                >
                  Offer
                </button>
                <button
                  onClick={() => handleQuickEvent('rejection')}
                  className="btn btn-outline-danger"
                >
                  Rejected
                </button>
                <button
                  onClick={() => handleQuickEvent('closed')}
                  className="btn btn-outline-dark"
                >
                  Close
                </button>
              </div>
            )}
            <p className="text-xs text-gray-500 mt-3">
              Quick buttons create an event with current time. Final statuses only allow reopen.
            </p>
          </div>

          {/* Manual Add Event */}
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Add Event</h2>
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn btn-outline-primary btn-sm"
              >
                {showAddForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
              </button>
            </div>
            {showAddForm && (
              <form onSubmit={handleAddEvent} className="space-y-3">
                <div>
                  <input
                    type="text"
                    value={newEvent.event_type}
                    onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                    placeholder="Event type (applied, interview_1, offer, etc.)"
                    required
                    className="input"
                  />
                </div>
                <div>
                  <textarea
                    value={newEvent.notes}
                    onChange={(e) => setNewEvent({ ...newEvent, notes: e.target.value })}
                    placeholder="Notes"
                    rows={3}
                    className="input"
                  />
                </div>
                <button type="submit" className="btn btn-primary w-full">
                  Add Event
                </button>
              </form>
            )}
            <p className="text-xs text-gray-500 mt-3">
              Manual add is still subject to workflow rules (no backward stage; final statuses locked).
            </p>
          </div>
        </div>

        {/* Right Column - Timeline */}
        <div className="card p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Timeline</h2>
            <span className="text-sm text-gray-500">{events.length} events</span>
          </div>
          <div className="space-y-3">
            {events.length === 0 ? (
              <div className="text-center text-gray-500 py-8">No events yet.</div>
            ) : (
              events.map((event) => {
                const eventUI = EVENT_UI[event.event_type] || {
                  label: event.event_type,
                  badge: 'secondary',
                  icon: '•',
                };
                const isFinalEvent = ['offer', 'rejection', 'closed'].includes(event.event_type);
                
                return (
                  <div
                    key={event.id}
                    className="border border-gray-200 rounded-lg p-4 bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex justify-between items-start gap-3">
                      <div className="flex gap-3 flex-1">
                        <div className="text-2xl">{eventUI.icon}</div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`badge badge-${eventUI.badge}`}>
                              {eventUI.label}
                            </span>
                            {isFinalEvent && (
                              <span className="badge badge-secondary text-xs">Final</span>
                            )}
                            {event.event_type === 'reopen' && (
                              <span className="badge badge-secondary text-xs">Workflow</span>
                            )}
                          </div>
                          {event.notes && (
                            <p className="text-sm text-gray-600 mt-1">{event.notes}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatDate(event.event_time)}
                        </span>
                        <button
                          onClick={() => handleDeleteEvent(event.id)}
                          className="btn btn-outline-danger btn-sm p-1"
                          title="Delete event"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}










