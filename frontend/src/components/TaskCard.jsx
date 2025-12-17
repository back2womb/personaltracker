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
    const isDone = task.is_completed_today;

    return (
        <div
            className="card"
            style={{
                padding: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                opacity: isDone ? 0.7 : 1,
                transition: 'all 0.2s ease',
                cursor: 'pointer'
            }}
            onClick={(e) => {
                // Prevent toggle when clicking edit
                if (e.target.closest('.edit-btn')) return;
                onToggle(task.id);
            }}
        >
            {/* Custom Checkbox */}
            <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '6px',
                border: `2px solid ${isDone ? 'var(--color-success)' : 'var(--bg-surface-hover)'}`,
                background: isDone ? 'var(--color-success)' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                transition: 'all 0.2s ease'
            }}>
                {isDone && <span style={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>✓</span>}
            </div>

            <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <h3 style={{
                        marginBottom: 0,
                        fontSize: '1rem',
                        textDecoration: isDone ? 'line-through' : 'none',
                        color: isDone ? 'var(--text-muted)' : 'var(--text-main)',
                        fontWeight: 500
                    }}>
                        {task.title}
                    </h3>
                    <span
                        style={{
                            fontSize: '0.65rem',
                            fontWeight: 600,
                            color: categoryColor,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            border: `1px solid ${categoryColor}`,
                            padding: '1px 6px',
                            borderRadius: '4px',
                            backgroundColor: `${categoryColor}10`
                        }}
                    >
                        {task.category}
                    </span>
                    {task.scheduled_time && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.2rem', background: 'rgba(255,255,255,0.05)', padding: '1px 6px', borderRadius: '4px' }}>
                            ⏳ {task.scheduled_time}m
                        </span>
                    )}
                </div>
                {task.current_streak > 0 && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        🔥 {task.current_streak} day streak
                    </div>
                )}
            </div>

            <button
                className="btn btn-outline edit-btn"
                onClick={(e) => {
                    e.stopPropagation();
                    onEdit(task);
                }}
                style={{ fontSize: '0.8rem', padding: '0.3rem 0.6rem', border: 'none', background: 'transparent', opacity: 0.5 }}
                title="Edit"
            >
                ✏️
            </button>
        </div>
    );
};

export default TaskCard;
