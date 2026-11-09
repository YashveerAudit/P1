import { useEffect, useRef } from 'react';

/** Accessible confirmation modal built on the native <dialog> element. */
export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  busy = false,
  onConfirm,
  onCancel,
}) {
  const ref = useRef(null);

  useEffect(() => {
    const dialog = ref.current;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      className="dialog"
      aria-labelledby="dialog-title"
      onCancel={(e) => {
        e.preventDefault(); // Escape key: let the parent decide
        if (!busy) onCancel();
      }}
    >
      <h2 id="dialog-title">{title}</h2>
      <p>{message}</p>
      <div className="dialog__actions">
        <button type="button" className="btn" onClick={onCancel} disabled={busy}>
          Cancel
        </button>
        <button type="button" className="btn btn--danger" onClick={onConfirm} disabled={busy}>
          {busy ? 'Deleting…' : confirmLabel}
        </button>
      </div>
    </dialog>
  );
}
