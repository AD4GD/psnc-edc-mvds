import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const { login } = useAuth();

  return (
    <div className="page page-center">
      <div className="card" style={{ maxWidth: 400, textAlign: "center" }}>
        <h2>Log In</h2>
        <p>Sign in with your Data Space account to access your dashboard.</p>
        <button className="btn btn-primary" onClick={login} style={{ marginTop: 16 }}>
          Sign In with Keycloak
        </button>
      </div>
    </div>
  );
}
