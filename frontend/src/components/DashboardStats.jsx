import React from 'react';

const StatCard = ({ title, value, icon }) => (
    <div className="card text-center">
        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{icon}</div>
        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-main)' }}>{value || 0}</div>
        <div style={{ color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.875rem', letterSpacing: '0.05em' }}>{title}</div>
    </div>
);

const DashboardStats = ({ stats }) => {
    if (!stats) return null;

    return (
        <div className="grid-cols-3 mb-8 animate-fade-in">
            <StatCard title="Active Streaks" value={stats.streaks?.active_streaks} icon="🔥" />
            <StatCard title="Tasks Done Today" value={stats.tasks?.completed_today} icon="✅" />
            <StatCard title="Total Rewards" value={stats.rewards?.total_rewards} icon="💎" />
        </div>
    );
};

export default DashboardStats;
