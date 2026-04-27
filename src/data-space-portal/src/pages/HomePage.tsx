import { useAuth } from "../auth/AuthContext";
import { useNavigate } from "react-router-dom";

export function HomePage() {
  const { authenticated, login } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="page">
      <h1>Welcome to the Data Space Portal</h1>
      <p className="subtitle">
        Register your organization to become a participant in the Data Space ecosystem.
      </p>

      <div className="home-cards">
        <div className="card">
          <h3>🏢 For Organizations</h3>
          <p>Register your company to join the Data Space. After approval, you'll be able to manage your connectors and request Verifiable Credentials.</p>
          {!authenticated && (
            <button className="btn btn-primary" onClick={() => navigate("/register")}>
              Register Now
            </button>
          )}
        </div>

        <div className="card">
          <h3>🔐 Already a Participant?</h3>
          <p>Log in to your dashboard to manage your profile, connectors, and request VCs for your infrastructure.</p>
          {!authenticated ? (
            <button className="btn btn-secondary" onClick={login}>
              Log In
            </button>
          ) : (
            <button className="btn btn-secondary" onClick={() => navigate("/dashboard")}>
              Go to Dashboard
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
