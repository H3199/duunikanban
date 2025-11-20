export default function KanbanColumn({ title, jobs, onMove, allowedStates }) {
  return (
    <div
      style={{
        width: "260px",
        background: "#f7f7f7",
        padding: "10px",
        borderRadius: "8px",
      }}
    >
      <h3>
        {title} ({jobs.length})
      </h3>

      {jobs.map((job) => (
        <div
          key={job.id}
          style={{
            background: "white",
            padding: "10px",
            border: "1px solid #ddd",
            borderRadius: "6px",
            marginBottom: "10px",
          }}
        >
          <strong>{job.title}</strong>
          <br />
          <span style={{ color: "#555" }}>{job.company}</span>

          <div style={{ marginTop: "8px" }}>
            <select
              value={job.state || "new"}
              onChange={(e) => onMove(job, e.target.value)}
            >
              {allowedStates.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>
      ))}
    </div>
  );
}
