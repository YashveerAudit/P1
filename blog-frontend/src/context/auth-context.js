import { createContext, useContext } from 'react';

export const AuthContext = createContext(null);

/** Access the signed-in user and sign-in/sign-out actions from any component. */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>');
  return context;
}
