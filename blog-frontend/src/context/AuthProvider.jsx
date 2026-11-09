import { useCallback, useEffect, useMemo, useState } from 'react';
import * as authApi from '../api/auth';
import { setSessionExpiredHandler } from '../api/client';
import { getToken, setToken } from '../api/token';
import { AuthContext } from './auth-context';

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // True until we know whether a stored token is still valid.
  const [checking, setChecking] = useState(() => Boolean(getToken()));

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  // On first load, turn a stored token back into a user (or discard it).
  useEffect(() => {
    if (!getToken()) return;
    const controller = new AbortController();
    authApi
      .me(controller.signal)
      .then(setUser)
      .catch((err) => {
        if (err.name !== 'AbortError') signOut();
      })
      .finally(() => setChecking(false));
    return () => controller.abort();
  }, [signOut]);

  // An expired token anywhere in the app signs the user out.
  useEffect(() => {
    setSessionExpiredHandler(signOut);
    return () => setSessionExpiredHandler(() => {});
  }, [signOut]);

  const acceptSession = useCallback(({ access_token, user: signedInUser }) => {
    setToken(access_token);
    setUser(signedInUser);
    return signedInUser;
  }, []);

  const value = useMemo(
    () => ({
      user,
      checking,
      isSignedIn: Boolean(user),
      signIn: (credentials) => authApi.login(credentials).then(acceptSession),
      signUp: (details) => authApi.register(details).then(acceptSession),
      signOut,
    }),
    [user, checking, acceptSession, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
