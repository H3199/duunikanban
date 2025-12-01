import axios from "axios";
import type { Job } from "./jobs";

// Smart dynamic base URL (works local + LAN + Docker + prod)
const API_URL: string =
  import.meta.env.VITE_API_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`;

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
});

// ---- API FUNCTIONS ----

export async function fetchJobs(range?: string) {
  const url = range
    ? `${API_URL}/api/v1/jobs?range=${range}`
    : `${API_URL}/api/v1/jobs`;
  const res = await fetch(url);
  return res.json();
}

export const updateJobState = async (id: string, state: string) => {
  const res = await api.post(`/jobs/${id}/state`, { state });
  return res.data;
};

export const updateNotes = async (id: string, notes: string) => {
  const res = await api.patch(`/jobs/${id}/notes`, { notes });
  return res.data;
};

export const fetchCredits = async () => {
  const res = await api.get("/status/credits");
  return res.data.remaining_credits;
};
