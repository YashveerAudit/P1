import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { deletePost, getPost } from '../api/posts';
import ConfirmDialog from '../components/ConfirmDialog';
import { EmptyState, ErrorMessage, Loading } from '../components/Status';
import { useAuth } from '../context/auth-context';
import { useApi } from '../hooks/useApi';
import { formatDate } from '../utils/format';

export default function PostDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: post, error, loading, reload } = useApi((signal) => getPost(id, signal), [id]);

  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  async function handleDelete() {
    setDeleting(true);
    setDeleteError(null);
    try {
      await deletePost(id);
      navigate('/', { state: { flash: `“${post.title}” was deleted.` } });
    } catch (err) {
      setDeleteError(err.message);
      setDeleting(false);
      setConfirmOpen(false);
    }
  }

  if (loading) return <Loading label="Loading post…" />;

  if (error?.isNotFound) {
    return (
      <EmptyState title="Post not found">
        <p>It may have been deleted, or the link is wrong.</p>
        <Link to="/" className="btn">
          Back to all posts
        </Link>
      </EmptyState>
    );
  }

  if (error) return <ErrorMessage message={error.message} onRetry={reload} />;

  const wasEdited = post.updated_at !== post.created_at;
  // Only the author sees Edit/Delete. The server enforces this too.
  const isOwner = Boolean(user) && user.id === post.owner_id;

  return (
    <article className="card post-detail">
      <Link to="/" className="back-link">
        ← All posts
      </Link>

      <h1>{post.title}</h1>
      <p className="meta">
        By {post.author} · {formatDate(post.created_at)}
        {wasEdited && ` · Updated ${formatDate(post.updated_at)}`}
      </p>

      {deleteError && <ErrorMessage message={deleteError} />}

      {/* Rendered as text, never as HTML, so user content cannot inject scripts. */}
      <div className="post-detail__content">{post.content}</div>

      {isOwner && (
        <div className="actions">
          <Link to={`/posts/${post.id}/edit`} className="btn btn--primary">
            Edit
          </Link>
          <button type="button" className="btn btn--danger" onClick={() => setConfirmOpen(true)}>
            Delete
          </button>
        </div>
      )}

      <ConfirmDialog
        open={confirmOpen}
        title="Delete this post?"
        message={`“${post.title}” will be permanently deleted. This cannot be undone.`}
        confirmLabel="Delete"
        busy={deleting}
        onConfirm={handleDelete}
        onCancel={() => setConfirmOpen(false)}
      />
    </article>
  );
}
