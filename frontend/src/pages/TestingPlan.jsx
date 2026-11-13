import { FlaskConical, Target, ListChecks, Gauge, Info, Activity } from "lucide-react";
import { PROPOSED_TARGETS, TEST_DATASET, ROADMAP, MEASURED_RESULTS } from "../lib/sampleData.js";

/**
 * Validation and testing dashboard.
 *
 * Two clearly-separated blocks: the presentation's PROPOSED TARGETS, and the
 * MEASURED RESULTS from running the test harness on this demo build. Neither is
 * presented as a real-college outcome.
 */
export default function TestingPlan() {
  return (
    <main className="section-wrap page-content">
      <div className="page-kicker">
        <FlaskConical size={16} /> VALIDATION &amp; TESTING
      </div>
      <h1>
        How we will <span className="gradient-text">check it.</span>
      </h1>
      <p className="page-lead">
        A testing plan based on the presentation's proposed targets, alongside the
        measured results for this demo build. Targets and results are kept separate.
      </p>

      <div className="notice-banner">
        <Info size={16} />
        <span>
          Measured results come from the offline demo with synthetic sample data. They are
          not real-college performance and not the presentation's proposed targets.
        </span>
      </div>

      <section className="how-block">
        <h2>
          <Target size={18} /> Proposed targets
        </h2>
        <div className="target-grid">
          {PROPOSED_TARGETS.map((t) => (
            <div key={t.label} className="target-card">
              <span className="target-value">{t.target}</span>
              <span className="target-label">{t.label}</span>
              <span className="target-tag">Target</span>
            </div>
          ))}
        </div>
      </section>

      <section className="how-block">
        <h2>
          <Activity size={18} /> Measured results — this demo build
        </h2>
        <p className="how-note">{MEASURED_RESULTS.runLabel}</p>
        <table className="metric-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Measured</th>
              <th>Target</th>
            </tr>
          </thead>
          <tbody>
            {MEASURED_RESULTS.metrics.map((m) => (
              <tr key={m.label}>
                <td>{m.label}</td>
                <td className="metric-measured">{m.measured}</td>
                <td className="metric-target">{m.target}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="how-note">{MEASURED_RESULTS.caveat}</p>
        <p className="how-note">
          Reproduce with <code>python tests/run_validation.py</code>.
        </p>
      </section>

      <section className="how-block">
        <h2>
          <ListChecks size={18} /> Test dataset — 50 curated questions
        </h2>
        <div className="dataset-grid">
          {TEST_DATASET.map((d) => (
            <div key={d.label} className="dataset-card">
              <b>{d.count}</b>
              <span>{d.label}</span>
            </div>
          ))}
        </div>
        <p className="how-note">
          The backend test suite in <code>tests/</code> exercises the answer policy,
          retrieval, evidence validation, publishing and the ticket workflow against this
          dataset.
        </p>
      </section>

      <section className="how-block">
        <h2>
          <Gauge size={18} /> What will be measured
        </h2>
        <ul className="metric-list">
          <li>Supported-answer accuracy</li>
          <li>Citation correctness</li>
          <li>Citation coverage</li>
          <li>Clarification rate</li>
          <li>Escalation rate</li>
          <li>Response latency</li>
        </ul>
        <p className="how-note">
          Results must be recorded honestly and separated from the proposed targets above.
        </p>
      </section>

      <section className="how-block">
        <h2>Future roadmap — not MVP features</h2>
        <ul className="roadmap-list">
          {ROADMAP.map((r) => (
            <li key={r}>
              <span className="roadmap-tag">Planned</span> {r}
            </li>
          ))}
        </ul>
        <p className="how-note">
          Deadline reminders require student consent. Personalised portal information
          requires authentication and a separate permission design.
        </p>
      </section>
    </main>
  );
}
