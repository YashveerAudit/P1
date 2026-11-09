import { Link, useSearchParams } from 'react-router-dom';
import { listPosts } from '../api/posts';
import PostCard from '../components/PostCard';
import { EmptyState, ErrorMessage, Loading } from '../components/Status';
import { useApi } from '../hooks/useApi';

const PAGE_SIZE = 9;

export default function Home() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Math.max(1, Number.parseInt(searchParams.get('page'), 10) || 1);

  const { data, error, loading, reload } = useApi(
    (signal) => listPosts({ skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE }, signal),
    [page],
  );

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  const goToPage = (next) => setSearchParams(next === 1 ? {} : { page: String(next) });

  return (
    <section>
      <div className="page-header">
        <div>
          <h1>Blog posts</h1>
          {data && (
            <p className="meta">
              {data.total} {data.total === 1 ? 'post' : 'posts'}
            </p>
          )}
        </div>
      </div>

      {loading && <Loading label="Loading posts…" />}
      {error && <ErrorMessage message={error.message} onRetry={reload} />}

      {!loading && data?.items.length === 0 && (
        <EmptyState title={page > 1 ? 'No posts on this page' : 'No posts yet'}>
          {page > 1 ? (
            <button type="button" className="btn" onClick={() => goToPage(1)}>
              Back to first page
            </button>
          ) : (
            <Link to="/posts/new" className="btn btn--primary">
              Write the first post
            </Link>
          )}
        </EmptyState>
      )}

      {!loading && data?.items.length > 0 && (
        <>
          <div className="post-grid">
            {data.items.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>

          {totalPages > 1 && (
            <nav className="pagination" aria-label="Pagination">
              <button
                type="button"
                className="btn"
                onClick={() => goToPage(page - 1)}
                disabled={page <= 1}
              >
                ← Previous
              </button>
              <span className="meta">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                className="btn"
                onClick={() => goToPage(page + 1)}
                disabled={page >= totalPages}
              >
                Next →
              </button>
            </nav>
          )}
        </>
      )}
    </section>
  );
}
