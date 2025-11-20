export type Job = {
  id: number;
  title: string;
  company: string;
  url: string;
  description?: string;
  country?: string;
  state: string;
  notes?: string;
};

const API_URL = "http://localhost:8000";

export async function fetchJobs(): Promise<Job[]> {
  const res = await fetch(`${API_URL}/jobs`);
  if (!res.ok) {
    throw new Error("Failed to load jobs");
  }
  return res.json();
}
