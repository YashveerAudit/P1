import { useState } from 'react';
import { POST_RULES, validatePost } from '../utils/validation';
import { ErrorMessage } from './Status';

const EMPTY_POST = { title: '', content: '', author: '' };

/**
 * Controlled form used for both creating and editing a post.
 * Validates on blur and on submit; shows server-side validation errors too.
 */
export default function PostEditor({ initialValues = EMPTY_POST, submitLabel, onSubmit, onCancel }) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    // Clear a field's error as soon as the user starts fixing it.
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  function handleBlur(event) {
    const { name } = event.target;
    const fieldError = validatePost(values)[name];
    setErrors((prev) => ({ ...prev, [name]: fieldError }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError(null);

    const clientErrors = validatePost(values);
    setErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) return;

    setSubmitting(true);
    try {
      await onSubmit({
        title: values.title.trim(),
        content: values.content.trim(),
        author: values.author.trim(),
      });
    } catch (err) {
      if (err.status === 422 && err.details.length > 0) {
        setErrors(err.fieldErrors());
      } else {
        setFormError(err.message);
      }
      setSubmitting(false);
    }
  }

  const fieldProps = (name) => ({
    id: name,
    name,
    value: values[name],
    onChange: handleChange,
    onBlur: handleBlur,
    maxLength: POST_RULES[name].max,
    'aria-invalid': Boolean(errors[name]),
    'aria-describedby': `${name}-hint`,
    disabled: submitting,
  });

  const hint = (name) => (
    <div id={`${name}-hint`} className="field__hint">
      {errors[name] ? (
        <span className="field__error">{errors[name]}</span>
      ) : (
        <span />
      )}
      <span className="meta">
        {values[name].trim().length}/{POST_RULES[name].max}
      </span>
    </div>
  );

  return (
    <form className="card form" onSubmit={handleSubmit} noValidate>
      {formError && <ErrorMessage message={formError} />}

      <div className="field">
        <label htmlFor="title">Title</label>
        <input type="text" placeholder="A catchy title" autoFocus {...fieldProps('title')} />
        {hint('title')}
      </div>

      <div className="field">
        <label htmlFor="author">Author</label>
        <input type="text" placeholder="Your name" {...fieldProps('author')} />
        {hint('author')}
      </div>

      <div className="field">
        <label htmlFor="content">Content</label>
        <textarea rows={12} placeholder="Write your post…" {...fieldProps('content')} />
        {hint('content')}
      </div>

      <div className="actions">
        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        <button type="button" className="btn" onClick={onCancel} disabled={submitting}>
          Cancel
        </button>
      </div>
    </form>
  );
}
