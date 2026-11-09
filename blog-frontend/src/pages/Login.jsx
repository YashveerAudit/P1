import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { useAuth } from '../context/auth-context';
import { validateLogin } from '../utils/validation';

const FIELDS = [
  { name: 'email', label: 'Email', type: 'email', autoComplete: 'email' },
  { name: 'password', label: 'Password', type: 'password', autoComplete: 'current-password' },
];

export default function Login() {
  const { signIn, isSignedIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = location.state?.from || '/';

  if (isSignedIn) return <Navigate to={destination} replace />;

  async function handleLogin(values) {
    const user = await signIn({ email: values.email.trim(), password: values.password });
    navigate(destination, { replace: true, state: { flash: `Welcome back, ${user.name}.` } });
  }

  return (
    <section className="auth">
      <h1>Log in</h1>
      <AuthForm fields={FIELDS} validate={validateLogin} submitLabel="Log in" onSubmit={handleLogin} />
      <p className="auth__footer meta">
        No account yet? <Link to="/register" state={location.state}>Sign up</Link>
      </p>
    </section>
  );
}
