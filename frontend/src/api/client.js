const API_BASE = "http://localhost:8000/api";

export async function uploadResume(file, location) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("location", location);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Upload failed");
  }

  return res.json();
}

export async function fetchJobs(sessionId, location = "", minScore = 40) {
  const params = new URLSearchParams({
    session_id: sessionId,
    location,
    min_score: String(minScore),
  });

  const res = await fetch(`${API_BASE}/jobs?${params}`);

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to fetch jobs");
  }

  return res.json();
}

export function downloadCsvUrl(sessionId, location = "", minScore = 40) {
  const params = new URLSearchParams({
    session_id: sessionId,
    location,
    min_score: String(minScore),
  });
  return `${API_BASE}/jobs/csv?${params}`;
}
