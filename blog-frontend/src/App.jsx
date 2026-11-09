import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import RequireAuth from './components/RequireAuth';
import Home from './pages/Home';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import PostDetail from './pages/PostDetail';
import PostForm from './pages/PostForm';
import Register from './pages/Register';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public */}
        <Route index element={<Home />} />
        <Route path="posts/:id" element={<PostDetail />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />

        {/* Signed-in users only */}
        <Route element={<RequireAuth />}>
          <Route path="posts/new" element={<PostForm />} />
          <Route path="posts/:id/edit" element={<PostForm />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
