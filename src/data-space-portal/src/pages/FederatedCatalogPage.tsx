import { useState, useEffect, useCallback } from "react";
import { useApi, type FcTarget } from "../api/apiClient";
import { DataTable } from "../components/DataTable";

export function FederatedCatalogPage() {
  const [targets, setTargets] = useState<FcTarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const api = useApi();

  const fetchTargets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getFcTargets();
      setTargets(data);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to load Federated Catalog targets");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTargets();
  }, [fetchTargets]);

  const columns = [
    {
      header: "Participant DID",
      render: (t: FcTarget) => (
        <code style={{ fontSize: "0.85em", wordBreak: "break-all" }}>{t.id}</code>
      ),
    },
    {
      header: "DSP URL",
      render: (t: FcTarget) => (
        <a href={t.url} target="_blank" rel="noopener noreferrer">
          {t.url}
        </a>
      ),
    },
    {
      header: "Name",
      render: (t: FcTarget) => t.name || "—",
    },
    {
      header: "Protocols",
      render: (t: FcTarget) =>
        t.supportedProtocols && t.supportedProtocols.length > 0
          ? t.supportedProtocols.join(", ")
          : "—",
    },
  ];

  return (
    <DataTable
      title="Federated Catalog"
      columns={columns}
      rows={targets}
      keyFn={(t) => t.id}
      loading={loading}
      error={error}
      emptyMessage="No targets found in the Federated Catalog."
      onRefresh={fetchTargets}
    />
  );
}
