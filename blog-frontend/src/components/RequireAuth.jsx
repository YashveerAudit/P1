import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/auth-context';
import { Loading } from './Status';

/** Wraps routes that need a signed-in user; sends visitors to the login page. */
export default function RequireAuth() {
  const { isSignedIn, checking } = useAuth();
  const location = useLocation();

  if (checking) return <Loading label="Checking your session…" />;

  if (!isSignedIn) {
    // Remember where they were going so login can send them back.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
