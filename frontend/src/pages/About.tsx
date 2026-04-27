export default function About() {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">About</h1>
        <p className="page-subtitle">Project background and technical details.</p>
      </div>

      <section className="intro-card">
        <h2>Project</h2>
        <p>
          CriteriaMeter is a lean, local-first application built to validate dataset
          features against user-defined criteria without requiring cloud infrastructure
          or third-party services.
        </p>
      </section>

      <section className="intro-card">
        <h2>Stack</h2>
        <ul className="about-list">
          <li><span className="about-label">Frontend</span> React 18, TypeScript, Vite</li>
          <li><span className="about-label">Backend</span> Python 3.12, FastAPI, Pydantic v2</li>
          <li><span className="about-label">Storage</span> SQLite via SQLAlchemy 2.x</li>
        </ul>
      </section>

      <section className="intro-card">
        <h2>Design principles</h2>
        <ul className="about-list">
          <li>Start with the smallest stack that proves the core workflow.</li>
          <li>Add complexity only after a measured bottleneck or missing product need appears.</li>
          <li>All data crossing the browser–API boundary is untrusted. The API is the sole enforcement point.</li>
        </ul>
      </section>
    </div>
  )
}
