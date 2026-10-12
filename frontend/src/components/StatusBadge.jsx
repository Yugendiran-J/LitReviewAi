const statusStyles = {
  include:   "badge-include",
  included:  "badge-include",
  accepted:  "badge-include",
  complete:  "badge-include",
  completed: "badge-include",
  verified:  "badge-verified",
  supported: "badge-include",
  exclude:   "badge-exclude",
  excluded:  "badge-exclude",
  rejected:  "badge-exclude",
  "not supported": "badge-exclude",
  pending:   "badge-pending",
  uncertain: "badge-pending",
  review:    "badge-pending",
  "needs review": "badge-pending",
  "partially supported": "badge-pending",
  "insufficient evidence": "badge-neutral",
};

export default function StatusBadge({ status, children }) {
  const label = children ?? status ?? "—";
  const key = String(status || label).toLowerCase();
  const style = statusStyles[key] || "badge-neutral";
  return <span className={`badge ${style}`}>{label}</span>;
}
