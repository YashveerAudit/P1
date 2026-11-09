import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import AuthForm from '../components/AuthForm';
import { useAuth } from '../context/auth-context';
import { AUTH_RULES, validateRegister } from '../utils/validation';

const FIELDS = [
  { name: 'name', label: 'Display name', type: 'text', autoComplete: 'name', hint: 'Shown as the author of your posts' },
  { name: 'email', label: 'Email', type: 'email', autoComplete: 'email' },
  {
    name: 'password',
    label: 'Password',
    type: 'password',
    autoComplete: 'new-password',
    hint: `At least ${AUTH_RULES.password.min} characters`,
  },
];

export default function Register() {
  const { signUp, isSignedIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = location.state?.from || '/';

  if (isSignedIn) return <Navigate to={destination} replace />;

  async function handleRegister(values) {
    const user = await signUp({
      name: values.name.trim(),
      email: values.email.trim(),
      password: values.password,
    });
    navigate(destination, { replace: true, state: { flash: `Welcome, ${user.name}! Your account is ready.` } });
  }

  return (
    <section className="auth">
      <h1>Create an account</h1>
      <AuthForm fields={FIELDS} validate={validateRegister} submitLabel="Sign up" onSubmit={handleRegister} />
      <p className="auth__footer meta">
        Already have an account? <Link to="/login" state={location.state}>Log in</Link>
      </p>
    </section>
  );
}
