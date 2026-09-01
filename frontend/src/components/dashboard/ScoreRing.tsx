export function ScoreRing({ value, label }: { value: number | null; label: string }) {
  const normalized = value ?? 0;
  return (
    <div className="score-ring" style={{ "--score": `${normalized * 3.6}deg` } as React.CSSProperties}>
      <div><strong>{value ?? "—"}</strong><span>{value === null ? "sem score" : "%"}</span><small>{label}</small></div>
    </div>
  );
}
