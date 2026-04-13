import React from "react";

interface Column<T> {
  header: string;
  render: (row: T) => React.ReactNode;
  stopPropagation?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  keyFn: (row: T) => string;
  loading: boolean;
  error?: string;
  emptyMessage?: string;
  onRefresh?: () => void;
  onRowClick?: (row: T) => void;
  title?: string;
  headerExtra?: React.ReactNode;
}

export function DataTable<T>({
  columns,
  rows,
  keyFn,
  loading,
  error,
  emptyMessage = "No data found.",
  onRefresh,
  onRowClick,
  title,
  headerExtra,
}: DataTableProps<T>) {
  return (
    <div className="page">
      <div className="page-header">
        {title && <h1>{title}</h1>}
        <div className="page-header-actions">
          {headerExtra}
          {onRefresh && (
            <button className="btn btn-secondary btn-sm" onClick={onRefresh} disabled={loading}>
              {loading ? "Refreshing…" : "⟳ Refresh"}
            </button>
          )}
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <p>Loading…</p>
      ) : rows.length === 0 ? (
        <p>{emptyMessage}</p>
      ) : (
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((col, i) => (
                  <th key={i}>{col.header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr
                  key={keyFn(row)}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  className={onRowClick ? "clickable-row" : undefined}
                >
                  {columns.map((col, i) => (
                    <td
                      key={i}
                      onClick={col.stopPropagation ? (e) => e.stopPropagation() : undefined}
                    >
                      {col.render(row)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
