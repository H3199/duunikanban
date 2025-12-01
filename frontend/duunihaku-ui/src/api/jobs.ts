export type Job = {
  id: number;
  title: string;
  company: string;
  url: string;
  description?: string;
  country?: string;
  state: string;
  notes?: string;
  updated_at?: string | null;
};

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchJobs(): Promise<Job[]> {
  const res = await fetch(`${API_URL}/api/v1/jobs`);
  if (!res.ok) {
    throw new Error("Failed to load jobs");
  }
  return res.json();
}
