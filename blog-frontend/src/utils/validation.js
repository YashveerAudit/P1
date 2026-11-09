// Client-side rules mirror the backend (app/schemas/post.py) so users get
// instant feedback. The server still validates everything.

export const POST_RULES = {
  title: { label: 'Title', min: 3, max: 150 },
  content: { label: 'Content', min: 10, max: 20000 },
  author: { label: 'Author', min: 2, max: 80 },
};

export function validatePost(values) {
  const errors = {};
  for (const [field, rule] of Object.entries(POST_RULES)) {
    const value = (values[field] ?? '').trim();
    if (!value) {
      errors[field] = `${rule.label} is required.`;
    } else if (value.length < rule.min) {
      errors[field] = `${rule.label} must be at least ${rule.min} characters.`;
    } else if (value.length > rule.max) {
      errors[field] = `${rule.label} must be at most ${rule.max} characters.`;
    }
  }
  return errors;
}
