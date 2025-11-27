import axios from "axios";

// Smart dynamic base URL (works local + LAN + Docker + prod)
const API_URL: string =
  import.meta.env.VITE_API_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
});

// ---- API FUNCTIONS ----

export const fetchJobs = async () => {
  const res = await api.get("/jobs");
  return res.data;
};

export const updateJobState = async (id: string, state: string) => {
  const res = await api.post(`/jobs/${id}/state`, { state });
  return res.data;
};

export const updateNotes = async (id: string, notes: string) => {
  const res = await api.patch(`/jobs/${id}/notes`, { notes });
  return res.data;
};
