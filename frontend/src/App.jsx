import { useEffect, useState } from "react";
import api from "./api";
import DashboardStats from "./components/DashboardStats";
import TaskCard from "./components/TaskCard";
import Login from "./components/Login";

const CATEGORIES = [
  "Personal Development",
  "Hobbies",
  "Career Development",
  "Academics",
  "Others"
];

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [dashboard, setDashboard] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorInfo, setErrorInfo] = useState(null);

  // Form State
  const [taskTitle, setTaskTitle] = useState("");
  const [taskCategory, setTaskCategory] = useState(CATEGORIES[4]); // Default to Others

  // Edit State
  const [editingTask, setEditingTask] = useState(null);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchData();
    } else {
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      setDashboard(null);
      setTasks([]);
    }
  }, [token]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, tasksRes] = await Promise.all([
        api.get("/dashboard/"),
        api.get("/tasks/")
      ]);
      setDashboard(statsRes.data);
      setTasks(tasksRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setErrorInfo(error.message);
      if (error.response?.status === 401) {
        setToken(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => setToken(null);

  const handleToggleTask = async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (task?.is_completed_today) {
      alert("Task already completed for today!");
      return;
    }
    try {
      await api.post("/logs/", { task_id: taskId, completed: true });
      fetchData();
    } catch (error) {
      console.error("Error logging task:", error);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!taskTitle.trim()) return;

    try {
      await api.post("/tasks/", { title: taskTitle, category: taskCategory });
      setTaskTitle("");
      setTaskCategory(CATEGORIES[4]);
      fetchData();
    } catch (error) {
      console.error("Error creating task:", error);
      if (error.response?.data?.detail) alert(error.response.data.detail);
    }
  };

  const handleUpdateTask = async (e) => {
    e.preventDefault();
    if (!editingTask) return;

    try {
      await api.put(`/tasks/${editingTask.id}`, {
        title: editingTask.title,
        category: editingTask.category
      });
      setEditingTask(null);
      fetchData();
    } catch (error) {
      console.error("Error updating task:", error);
      if (error.response?.data?.detail) alert(error.response.data.detail);
    }
  };

  // Group tasks by category
  const groupedTasks = CATEGORIES.reduce((acc, category) => {
    acc[category] = tasks.filter(t => t.category === category);
    return acc;
  }, {});

  // State defined at top
  const [usersList, setUsersList] = useState([]);
  const [showUsers, setShowUsers] = useState(false);
  const [adminStats, setAdminStats] = useState(null);

  // ... (existing handlers)

  const fetchUsers = async () => {
    try {
      const res = await api.get("/dashboard/community"); // Updated endpoint
      setUsersList(res.data);
      setShowUsers(true);
    } catch (error) {
      console.error("Error fetching community stats:", error);
      alert("Failed to load community data");
    }
  };

  const fetchAdminStats = async () => {
    try {
      const res = await api.get("/dashboard/admin/analytics");
      if (res.data.error) {
        alert("Access Denied: Admin only.");
      } else {
        setAdminStats(res.data);
      }
    } catch (error) {
      console.error("Error fetching admin stats:", error);
      alert("Failed to access admin panel.");
    }
  };

  if (!token) {
    return <Login setToken={setToken} />;
  }

  if (loading && !dashboard) {
    return (
      <div className="flex-between" style={{ height: '100vh', justifyContent: 'center' }}>
        <h2 className="animate-fade-in">Initializing Engine...</h2>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Edit Modal (Simple Overlay) */}
      {editingTask && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div className="card" style={{ width: '400px', maxWidth: '90%' }}>
            <h2>Edit Protocol</h2>
            <form onSubmit={handleUpdateTask} className="flex-column">
              <input
                className="input"
                value={editingTask.title}
                onChange={e => setEditingTask({ ...editingTask, title: e.target.value })}
              />
              <select
                className="input"
                value={editingTask.category}
                onChange={e => setEditingTask({ ...editingTask, category: e.target.value })}
              >
                {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
              <div className="flex-between" style={{ marginTop: '1rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setEditingTask(null)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Admin Modal */}
      {adminStats && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.9)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1200
        }}>
          <div className="card" style={{ width: '500px', maxWidth: '90%', textAlign: 'center' }}>
            <h2 style={{ color: '#22d3ee', marginBottom: '2rem' }}>🕵️‍♂️ Deployment Analytics</h2>

            <div className="grid-cols-2" style={{ gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ background: '#334155', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem' }}>👀</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{adminStats.visits}</div>
                <div style={{ color: '#94a3b8' }}>Total Site Visits</div>
              </div>
              <div style={{ background: '#334155', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem' }}>👤</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{adminStats.total_users}</div>
                <div style={{ color: '#94a3b8' }}>Registered Users</div>
              </div>
              <div style={{ background: '#334155', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem' }}>🔑</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{adminStats.logins}</div>
                <div style={{ color: '#94a3b8' }}>Total Logins</div>
              </div>
              <div style={{ background: '#334155', padding: '1rem', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem' }}>📝</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{adminStats.registrations}</div>
                <div style={{ color: '#94a3b8' }}>Signups</div>
              </div>
            </div>

            <button onClick={() => setAdminStats(null)} className="btn btn-primary">Close</button>
          </div>
        </div>
      )}

      {/* Community Leaderboard Modal (existing) */}
      {showUsers && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1100, backdropFilter: 'blur(5px)'
        }}>
          <div className="card" style={{ width: '600px', maxWidth: '95%', maxHeight: '85vh', overflowY: 'auto' }}>
            <div className="flex-between mb-4">
              <h2 style={{ background: 'linear-gradient(to right, #fbbf24, #d97706)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                🏆 Global Leaderboard
              </h2>
              <button onClick={() => setShowUsers(false)} className="btn btn-outline" style={{ padding: '0.25rem 0.6rem', fontSize: '1.2rem' }}>×</button>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.05)', textAlign: 'left' }}>
                  <th style={{ padding: '1rem', borderRadius: '8px 0 0 8px' }}>Rank</th>
                  <th style={{ padding: '1rem' }}>User</th>
                  <th style={{ padding: '1rem', textAlign: 'center' }}>Tasks Done</th>
                  <th style={{ padding: '1rem', borderRadius: '0 8px 8px 0', textAlign: 'center' }}>Active Streaks</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u, index) => {
                  let medal = null;
                  if (index === 0) medal = '🥇';
                  if (index === 1) medal = '🥈';
                  if (index === 2) medal = '🥉';

                  return (
                    <tr key={u.username} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '1rem', fontSize: '1.2rem' }}>{medal || index + 1}</td>
                      <td style={{ padding: '1rem', fontWeight: 'bold' }}>{u.username}</td>
                      <td style={{ padding: '1rem', textAlign: 'center', color: '#10b981', fontWeight: 'bold' }}>{u.tasks_completed}</td>
                      <td style={{ padding: '1rem', textAlign: 'center', color: '#f59e0b' }}>{u.active_streaks > 0 ? `🔥 ${u.active_streaks}` : '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <header className="flex-between mb-8">
        <div>
          <h1 style={{ background: 'linear-gradient(to right, #3b82f6, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Reference Implementation
          </h1>
          <p>Personal Execution Engine v1.2</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={fetchAdminStats} className="btn btn-outline" style={{ fontSize: '0.8rem', color: '#22d3ee', borderColor: '#22d3ee' }}>
            🛡️ Admin
          </button>
          <button onClick={fetchUsers} className="btn btn-outline" style={{ fontSize: '0.8rem' }}>
            👥 Community
          </button>
          <button onClick={handleLogout} className="btn btn-outline" style={{ fontSize: '0.8rem' }}>
            Logout
          </button>
        </div>
      </header>

      <main>
        <DashboardStats stats={dashboard} />

        <section className="mb-8">
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Initialize New Protocol</h3>
            <form onSubmit={handleCreateTask} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto', gap: '1rem' }}>
              <input
                className="input"
                placeholder="Protocol Name..."
                value={taskTitle}
                onChange={(e) => setTaskTitle(e.target.value)}
              />
              <select
                className="input"
                value={taskCategory}
                onChange={(e) => setTaskCategory(e.target.value)}
              >
                {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
              <button type="submit" className="btn btn-primary">Create</button>
            </form>
          </div>

          <div className="flex-column" style={{ gap: '2rem' }}>
            {/* Fallback view if grouping fails */}
            {tasks.length > 0 && Object.values(groupedTasks).every(g => g.length === 0) && (
              <div style={{ color: 'red' }}>
                Grouping Logic Mismatch! Listing all tasks raw:
                {tasks.map(task => <TaskCard key={task.id} task={task} onToggle={handleToggleTask} onEdit={setEditingTask} />)}
              </div>
            )}

            {CATEGORIES.map(category => {
              const categoryTasks = groupedTasks[category];
              if (!categoryTasks || categoryTasks.length === 0) return null;

              return (
                <div key={category} className="animate-fade-in">
                  <h3 style={{ borderBottom: '1px solid var(--bg-surface-hover)', paddingBottom: '0.5rem', marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                    {category}
                  </h3>
                  <div className="flex-column">
                    {categoryTasks.map(task => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onToggle={handleToggleTask}
                        onEdit={setEditingTask}
                      />
                    ))}
                  </div>
                </div>
              );
            })}

            {tasks.length === 0 && (
              <div className="text-center" style={{ padding: '2rem', color: 'var(--text-muted)' }}>
                No active protocols found. Initiate one above.
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
