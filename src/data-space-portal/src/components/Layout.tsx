import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function Layout() {
  const { authenticated, user, login, logout } = useAuth();

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <img
            src="/logo.png"
            alt="Logo"
            style={{ height: 32, marginBottom: 8, display: "block" }}
            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
          <h2>Data Space</h2>
          <span className="sidebar-subtitle">Portal</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")} end>
            Home
          </NavLink>

          {!authenticated && (
            <>
              <NavLink to="/register" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
                Register
              </NavLink>
              <button className="nav-link nav-btn" onClick={login}>
                Login
              </button>
            </>
          )}

          {authenticated && (
            <>
              {!user?.is_admin && (
                <>
                  <div className="nav-section">Participant</div>
                  <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
                    Overview
                  </NavLink>
                  <NavLink to="/request-vc" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
                    Verifiable Credentials
                  </NavLink>
                </>
              )}

              {user?.is_admin && (
                <>
                  <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
                    Dashboard
                  </NavLink>
                  <div className="nav-section">Admin</div>
                  <NavLink
                    to="/admin/registrations"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  >
                    Registrations
                  </NavLink>
                  <NavLink
                    to="/admin/participants"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  >
                    Participants
                  </NavLink>
                  <NavLink
                    to="/admin/federated-catalog"
                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  >
                    Federated Catalog
                  </NavLink>
                </>
              )}
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          {authenticated && (
            <div className="user-info">
              <span className="user-email">{user?.email}</span>
              <button className="nav-link nav-btn logout-btn" onClick={logout}>
                Logout
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
