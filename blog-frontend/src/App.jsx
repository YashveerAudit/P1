import React, { useState, useEffect } from 'react';

function App() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/posts')
      .then((res) => {
        if (!res.ok) throw new Error('Could not connect to API server.');
        return res.json();
      })
      .then((data) => setPosts(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', fontFamily: 'sans-serif' }}>
      <nav style={{ backgroundColor: '#2563eb', padding: '1rem', color: '#ffffff', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', fontSize: '1.5rem', fontWeight: 'bold' }}>
          📝 BlogManager Dashboard
        </div>
      </nav>

      <main style={{ maxWidth: '1000px', margin: '2rem auto', padding: '0 1rem' }}>
        <div style={{ backgroundColor: '#ffffff', padding: '2rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <h2 style={{ color: '#1f2937', marginBottom: '1rem' }}>Server Status</h2>
          
          {loading && <p style={{ color: '#6b7280' }}>Connecting to FastAPI backend...</p>}
          
          {error && (
            <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: '0.375rem' }}>
              ⚠️ Frontend is Live, but Backend connection failed: {error}
            </div>
          )}

          {!loading && !error && (
            <div style={{ backgroundColor: '#ecfdf5', color: '#065f46', padding: '1rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>
              ✅ Successfully connected to MongoDB via FastAPI!
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;