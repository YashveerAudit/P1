import { Link, useNavigate, useParams } from 'react-router-dom';
import { createPost, getPost, updatePost } from '../api/posts';
import PostEditor from '../components/PostEditor';
import { EmptyState, ErrorMessage, Loading } from '../components/Status';
import { useApi } from '../hooks/useApi';

/** Handles both /posts/new (create) and /posts/:id/edit (edit). */
export default function PostForm() {
  const { id } = useParams();
  return id ? <EditPost id={id} /> : <CreatePost />;
}

function CreatePost() {
  const navigate = useNavigate();

  async function handleCreate(values) {
    const created = await createPost(values);
    navigate(`/posts/${created.id}`, { state: { flash: 'Post published.' } });
  }

  return (
    <section className="narrow">
      <h1>New post</h1>
      <PostEditor submitLabel="Publish" onSubmit={handleCreate} onCancel={() => navigate('/')} />
    </section>
  );
}

function EditPost({ id }) {
  const navigate = useNavigate();
  const { data: post, error, loading, reload } = useApi((signal) => getPost(id, signal), [id]);

  async function handleUpdate(values) {
    await updatePost(id, values);
    navigate(`/posts/${id}`, { state: { flash: 'Changes saved.' } });
  }

  if (loading) return <Loading label="Loading post…" />;

  if (error?.isNotFound) {
    return (
      <EmptyState title="Post not found">
        <Link to="/" className="btn">
          Back to all posts
        </Link>
      </EmptyState>
    );
  }

  if (error) return <ErrorMessage message={error.message} onRetry={reload} />;

  return (
    <section className="narrow">
      <h1>Edit post</h1>
      <PostEditor
        key={post.id}
        initialValues={{ title: post.title, content: post.content, author: post.author }}
        submitLabel="Save changes"
        onSubmit={handleUpdate}
        onCancel={() => navigate(`/posts/${id}`)}
      />
    </section>
  );
}
