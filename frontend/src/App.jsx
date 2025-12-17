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

      <header className="flex-between mb-8">
        <div>
          <h1 style={{ background: 'linear-gradient(to right, #3b82f6, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Reference Implementation
          </h1>
          <p>Personal Execution Engine v1.2</p>
        </div>
        <button onClick={handleLogout} className="btn btn-outline" style={{ fontSize: '0.8rem' }}>
          Logout
        </button>
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
