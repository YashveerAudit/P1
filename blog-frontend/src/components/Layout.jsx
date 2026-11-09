import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();
  // Pages pass a one-off success message via navigate(path, { state: { flash } }).
  const flash = location.state?.flash;

  return (
    <div className="app">
      <header className="navbar">
        <div className="container navbar__inner">
          <Link to="/" className="navbar__brand">
            BlogManager
          </Link>
          <nav className="navbar__links">
            <NavLink to="/" end>
              Posts
            </NavLink>
            <NavLink to="/posts/new" className="btn btn--primary btn--small">
              New post
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="container main">
        {flash && (
          <div key={location.key} className="alert alert--success" role="status">
            {flash}
          </div>
        )}
        <Outlet />
      </main>
    </div>
  );
}
