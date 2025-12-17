
import { useState } from 'react';
import api from '../api';

const Login = ({ setToken }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isRegister, setIsRegister] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Using URLSearchParams for OAuth2 form data
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            if (isRegister) {
                await api.post('/auth/register', { username, password });
                // Auto login after register
                const res = await api.post('/auth/login', formData);
                setToken(res.data.access_token);
            } else {
                const res = await api.post('/auth/login', formData);
                setToken(res.data.access_token);
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || 'Authentication failed');
        }
    };

    return (
        <div className="flex-between" style={{ height: '100vh', justifyContent: 'center' }}>
            <div className="card" style={{ width: '400px', padding: '2rem' }}>
                <h2 className="text-center" style={{ marginBottom: '2rem' }}>
                    {isRegister ? 'Initialize Access' : 'Authenticate'}
                </h2>

                {error && <div style={{ color: 'var(--color-danger)', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

                <form onSubmit={handleSubmit} className="flex-column">
                    <input
                        className="input"
                        placeholder="Username / Callsign"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        className="input"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" className="btn btn-primary" style={{ marginTop: '1rem', width: '100%' }}>
                        {isRegister ? 'Create Account' : 'Login'}
                    </button>
                </form>

                <div className="text-center" style={{ marginTop: '1.5rem', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>
                        {isRegister ? 'Already have access? ' : 'Need access? '}
                    </span>
                    <button
                        style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', textDecoration: 'underline' }}
                        onClick={() => setIsRegister(!isRegister)}
                    >
                        {isRegister ? 'Login' : 'Register'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;
