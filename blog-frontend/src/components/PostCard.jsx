import { Link } from 'react-router-dom';
import { excerpt, formatDate } from '../utils/format';

export default function PostCard({ post }) {
  return (
    <article className="card post-card">
      <h2 className="post-card__title">
        <Link to={`/posts/${post.id}`}>{post.title}</Link>
      </h2>
      <p className="meta">
        By {post.author} · {formatDate(post.created_at)}
      </p>
      <p className="post-card__excerpt">{excerpt(post.content)}</p>
      <Link to={`/posts/${post.id}`} className="post-card__more">
        Read more →
      </Link>
    </article>
  );
}
