import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth-context';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isSignedIn, signOut } = useAuth();
  // Pages pass a one-off success message via navigate(path, { state: { flash } }).
  const flash = location.state?.flash;

  function handleSignOut() {
    signOut();
    navigate('/', { state: { flash: 'You have been logged out.' } });
  }

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
            {isSignedIn ? (
              <>
                <NavLink to="/posts/new" className="btn btn--primary btn--small">
                  New post
                </NavLink>
                <span className="navbar__user" title={user.email}>
                  {user.name}
                </span>
                <button type="button" className="btn btn--small" onClick={handleSignOut}>
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login">Log in</NavLink>
                <NavLink to="/register" className="btn btn--primary btn--small">
                  Sign up
                </NavLink>
              </>
            )}
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
