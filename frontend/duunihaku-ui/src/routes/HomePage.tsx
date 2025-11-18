import { useQuery } from "@tanstack/react-query";
import { fetchJobs } from "../api/jobs";

export default function HomePage() {
  const { data, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: fetchJobs,
  });

  if (isLoading) return <p>Loading...</p>;
  if (!data) return <p>No data</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h1>Job List</h1>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {data.map((job) => (
          <li
            key={job.id}
            style={{
              padding: "10px",
              marginBottom: "6px",
              border: "1px solid #ddd",
              borderRadius: "6px",
            }}
          >
            <strong>{job.title}</strong>{" "}
            <span style={{ color: "#666" }}>({job.company})</span>
            <br />
            <small style={{ color: "orange" }}>Status: {job.state}</small>
          </li>
        ))}
      </ul>
    </div>
  );
}
