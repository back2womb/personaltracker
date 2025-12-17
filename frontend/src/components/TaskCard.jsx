import React from 'react';

const CATEGORY_COLORS = {
    "Personal Development": "var(--color-primary)",
    "Hobbies": "var(--color-accent)",
    "Career Development": "var(--color-success)",
    "Academics": "#8b5cf6", // violet
    "Others": "var(--text-muted)",
};

const TaskCard = ({ task, onToggle, onEdit }) => {
    const categoryColor = CATEGORY_COLORS[task.category] || "var(--text-muted)";

    return (
        <div className="card flex-between" style={{ padding: '1.25rem' }}>
            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <span
                        style={{
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: categoryColor,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            border: `1px solid ${categoryColor}`,
                            padding: '2px 8px',
                            borderRadius: '999px',
                            backgroundColor: `${categoryColor}20` // 20% opacity
                        }}
                    >
                        {task.category}
                    </span>
                    <h3 style={{
                        marginBottom: 0,
                        fontSize: '1.1rem',
                        textDecoration: task.is_completed_today ? 'line-through' : 'none',
                        color: task.is_completed_today ? 'var(--text-muted)' : 'var(--text-main)'
                    }}>
                        {task.title}
                    </h3>
                </div>
                <p style={{ marginBottom: 0, fontSize: '0.9rem' }}>
                    🔥 Streak: <span className="text-accent" style={{ fontWeight: 'bold' }}>{task.current_streak} days</span>
                </p>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                    className="btn btn-outline"
                    onClick={() => onEdit(task)}
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                >
                    Edit
                </button>
                <button
                    className={`btn ${task.is_completed_today ? 'btn-outline' : 'btn-primary'}`}
                    onClick={() => onToggle(task.id)}
                >
                    {task.is_completed_today ? 'Done' : 'Complete'}
                </button>
            </div>
        </div>
    );
};

export default TaskCard;
