import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">Welcome to CriteriaMeter</h1>
        <p className="page-subtitle">
          Your local-first platform for feature validation and measurement.
        </p>
      </div>

      <section className="intro-card">
        <h2>What is CriteriaMeter?</h2>
        <p>
          CriteriaMeter lets you upload datasets, parse and validate features against
          defined criteria, and explore results through an interactive dashboard —
          all without sending your data to a third-party service.
        </p>
        <p>
          Upload a dataset, let the pipeline validate each feature, then inspect
          pass/fail outcomes, filter by property, and drill into individual records.
        </p>
      </section>

      <section className="feature-grid">
        <div className="feature-tile">
          <span className="tile-icon">↑</span>
          <h3>Upload</h3>
          <p>Bring in your own datasets. Raw files are stored securely outside the web root.</p>
        </div>
        <div className="feature-tile">
          <span className="tile-icon">✓</span>
          <h3>Validate</h3>
          <p>Each feature is parsed and checked against your criteria. Failures are captured with full detail.</p>
        </div>
        <div className="feature-tile">
          <span className="tile-icon">◎</span>
          <h3>Explore</h3>
          <p>Filter, paginate, and inspect results. Drill into any feature to see exactly what passed or failed.</p>
        </div>
      </section>

      <section className="intro-card">
        <h2>Get started</h2>
        <p>
          Use the{' '}
          <Link to="/meter-reading" className="slsa-link">
            Meter Reading
          </Link>{' '}
          page to assess your supply-chain security posture against the SLSA v1.2
          Build Track — walk through each level's requirements and track your
          compliance progress interactively.
        </p>
      </section>
    </div>
  )
}
