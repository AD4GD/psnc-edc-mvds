import { useSearchParams, Link } from "react-router-dom";

export function EmailConfirmedPage() {
  const [params] = useSearchParams();
  const status = params.get("status");
  const isError = status === "error";

  return (
    <div className="page" style={{ maxWidth: 480, margin: "80px auto", textAlign: "center" }}>
      {isError ? (
        <>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>❌</div>
          <h1>Confirmation Failed</h1>
          <p className="text-muted">
            The confirmation link is invalid or has expired. Please register again or contact support.
          </p>
        </>
      ) : (
        <>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>✅</div>
          <h1>Email Confirmed!</h1>
          <p className="text-muted">
            Your email has been verified. Your registration is now pending admin approval — you'll
            receive an email once your account is ready.
          </p>
        </>
      )}
      <Link to="/" className="btn btn-primary" style={{ marginTop: "24px", display: "inline-block" }}>
        Back to Home
      </Link>
    </div>
  );
}
