import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import NotFound from './pages/NotFound';
import PostDetail from './pages/PostDetail';
import PostForm from './pages/PostForm';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="posts/new" element={<PostForm />} />
        <Route path="posts/:id" element={<PostDetail />} />
        <Route path="posts/:id/edit" element={<PostForm />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
