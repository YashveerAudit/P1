// Client-side rules mirror the backend (app/schemas/*.py) so users get
// instant feedback. The server still validates everything.

export const POST_RULES = {
  title: { label: 'Title', min: 3, max: 150 },
  content: { label: 'Content', min: 10, max: 20000 },
};

export const AUTH_RULES = {
  name: { label: 'Display name', min: 2, max: 80 },
  password: { label: 'Password', min: 8, max: 128 },
};

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function checkLength(value, rule) {
  const trimmed = value.trim();
  if (!trimmed) return `${rule.label} is required.`;
  if (trimmed.length < rule.min) return `${rule.label} must be at least ${rule.min} characters.`;
  if (trimmed.length > rule.max) return `${rule.label} must be at most ${rule.max} characters.`;
  return undefined;
}

function checkEmail(value) {
  if (!value.trim()) return 'Email is required.';
  if (!EMAIL_PATTERN.test(value.trim())) return 'Enter a valid email address.';
  return undefined;
}

/** Return only the fields that have an error. */
function collect(errors) {
  return Object.fromEntries(Object.entries(errors).filter(([, message]) => message));
}

export function validatePost(values) {
  return collect({
    title: checkLength(values.title ?? '', POST_RULES.title),
    content: checkLength(values.content ?? '', POST_RULES.content),
  });
}

export function validateLogin(values) {
  return collect({
    email: checkEmail(values.email ?? ''),
    password: values.password ? undefined : 'Password is required.',
  });
}

export function validateRegister(values) {
  return collect({
    name: checkLength(values.name ?? '', AUTH_RULES.name),
    email: checkEmail(values.email ?? ''),
    password: checkLength(values.password ?? '', AUTH_RULES.password),
  });
}
