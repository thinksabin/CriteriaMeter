export default function Dashboard() {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Validation results and dataset overview.</p>
      </div>

      <section className="placeholder-card">
        <span className="placeholder-icon">◈</span>
        <h2>Coming soon</h2>
        <p>
          The dashboard will display uploaded datasets, per-feature validation outcomes,
          and summary statistics once the ingestion pipeline is wired up.
        </p>
      </section>
    </div>
  )
}
