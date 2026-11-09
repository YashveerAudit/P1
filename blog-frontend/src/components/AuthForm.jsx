import { useState } from 'react';
import { ErrorMessage } from './Status';

/**
 * Shared form for the login and register pages.
 * `fields` describes the inputs; `validate(values)` returns { field: message }.
 */
export default function AuthForm({ fields, validate, submitLabel, onSubmit }) {
  const [values, setValues] = useState(() => Object.fromEntries(fields.map((f) => [f.name, ''])));
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: undefined }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setFormError(null);

    const clientErrors = validate(values);
    setErrors(clientErrors);
    if (Object.keys(clientErrors).length > 0) return;

    setSubmitting(true);
    try {
      await onSubmit(values);
    } catch (err) {
      if (err.status === 422 && err.details.length > 0) {
        setErrors(err.fieldErrors());
      } else {
        setFormError(err.message);
      }
      setSubmitting(false);
    }
  }

  return (
    <form className="card form" onSubmit={handleSubmit} noValidate>
      {formError && <ErrorMessage message={formError} />}

      {fields.map((field, index) => (
        <div className="field" key={field.name}>
          <label htmlFor={field.name}>{field.label}</label>
          <input
            id={field.name}
            name={field.name}
            type={field.type}
            autoComplete={field.autoComplete}
            autoFocus={index === 0}
            value={values[field.name]}
            onChange={handleChange}
            disabled={submitting}
            aria-invalid={Boolean(errors[field.name])}
            aria-describedby={`${field.name}-hint`}
          />
          <div id={`${field.name}-hint`} className="field__hint">
            {errors[field.name] ? (
              <span className="field__error">{errors[field.name]}</span>
            ) : (
              <span className="meta">{field.hint}</span>
            )}
          </div>
        </div>
      ))}

      <button type="submit" className="btn btn--primary" disabled={submitting}>
        {submitting ? 'Please wait…' : submitLabel}
      </button>
    </form>
  );
}
