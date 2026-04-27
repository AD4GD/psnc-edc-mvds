import { useState } from "react";
import { useApi } from "../api/apiClient";

interface RegistrationForm {
  name: string;
  full_name: string;
  VAT_number: string;
  email: string;
  country: string;
  city: string;
  postal_code: string;
  street: string;
  building_number: string;
}

const emptyForm: RegistrationForm = {
  name: "",
  full_name: "",
  VAT_number: "",
  email: "",
  country: "",
  city: "",
  postal_code: "",
  street: "",
  building_number: "",
};

export function RegisterPage() {
  const [form, setForm] = useState<RegistrationForm>(emptyForm);
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const api = useApi();

  const update = <K extends keyof RegistrationForm>(key: K, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setMessage("");

    try {
      const result = await api.submitRegistration({
        name: form.name,
        full_name: form.full_name,
        VAT_number: form.VAT_number,
        email: form.email,
        location: {
          country: form.country,
          city: form.city,
          postal_code: form.postal_code,
          street: form.street,
          building_number: form.building_number,
        },
      });
      setStatus("success");
      setMessage(result.message || "Registration submitted! Check your email to confirm.");
      setForm(emptyForm);
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Registration failed");
    }
  };

  if (status === "success") {
    return (
      <div className="page">
        <div className="success-banner">
          <h2>✅ Registration Submitted</h2>
          <p>{message}</p>
          <p>Please check your email and click the confirmation link to proceed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>Register Your Organization</h1>
      <p className="subtitle">Fill in your company details to apply for Data Space participation.</p>

      <form onSubmit={handleSubmit} className="form">
        <fieldset>
          <legend>Company Information</legend>
          <div className="form-grid">
            <div className="form-field">
              <label>Short Name *</label>
              <input required value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="ACME" />
            </div>
            <div className="form-field">
              <label>Full Legal Name *</label>
              <input required value={form.full_name} onChange={(e) => update("full_name", e.target.value)} placeholder="ACME Corporation Ltd." />
            </div>
            <div className="form-field">
              <label>VAT Number *</label>
              <input required value={form.VAT_number} onChange={(e) => update("VAT_number", e.target.value)} placeholder="PL1234567890" />
            </div>
            <div className="form-field">
              <label>Contact Email *</label>
              <input required type="email" value={form.email} onChange={(e) => update("email", e.target.value)} placeholder="admin@acme.com" />
            </div>
          </div>
        </fieldset>

        <fieldset>
          <legend>Company Address</legend>
          <div className="form-grid">
            <div className="form-field">
              <label>Country (ISO code) *</label>
              <input required value={form.country} onChange={(e) => update("country", e.target.value)} placeholder="PL" maxLength={2} />
            </div>
            <div className="form-field">
              <label>City *</label>
              <input required value={form.city} onChange={(e) => update("city", e.target.value)} placeholder="Poznań" />
            </div>
            <div className="form-field">
              <label>Postal Code *</label>
              <input required value={form.postal_code} onChange={(e) => update("postal_code", e.target.value)} placeholder="61-001" />
            </div>
            <div className="form-field">
              <label>Street *</label>
              <input required value={form.street} onChange={(e) => update("street", e.target.value)} placeholder="Jana Pawła II" />
            </div>
            <div className="form-field">
              <label>Building Number</label>
              <input value={form.building_number} onChange={(e) => update("building_number", e.target.value)} placeholder="10" />
            </div>
          </div>
        </fieldset>

        {status === "error" && <div className="error-banner">{message}</div>}

        <button type="submit" className="btn btn-primary" disabled={status === "submitting"}>
          {status === "submitting" ? "Submitting…" : "Submit Registration"}
        </button>
      </form>
    </div>
  );
}
