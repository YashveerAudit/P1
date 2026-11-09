import { useCallback, useEffect, useState } from 'react';

/**
 * Load data from the API with loading / error state and a reload() function.
 * Requests are cancelled when the component unmounts or `deps` change.
 *
 *   const { data, error, loading, reload } = useApi((signal) => getPost(id, signal), [id]);
 */
export function useApi(fetcher, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    fetcher(controller.signal)
      .then((data) => setState({ data, error: null, loading: false }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ data: null, error, loading: false });
      });

    return () => {
      controller.abort();
      setState((prev) => ({ ...prev, error: null, loading: true }));
    };
    // `fetcher` is recreated on every render; `deps` controls when to refetch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, attempt]);

  const reload = useCallback(() => setAttempt((n) => n + 1), []);

  return { ...state, reload };
}
