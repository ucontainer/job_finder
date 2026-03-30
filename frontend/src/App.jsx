import { useState } from "react";
import FileUpload from "./components/FileUpload";
import Filters from "./components/Filters";
import JobCard from "./components/JobCard";
import { uploadResume, fetchJobs } from "./api/client";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [jobTitle, setJobTitle] = useState("");
  const [jobs, setJobs] = useState([]);
  const [minScore, setMinScore] = useState(40);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [location, setLocationState] = useState("");

  async function handleUpload(file, loc) {
    setLoading(true);
    setError("");
    setJobs([]);
    setLocationState(loc);

    try {
      const upload = await uploadResume(file, loc);
      setJobTitle(upload.job_title);
      setSessionId(upload.session_id);

      const matched = await fetchJobs(upload.session_id, loc, minScore);
      setJobs(matched);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleFilterChange(newScore) {
    setMinScore(newScore);
    if (!sessionId) return;

    setLoading(true);
    try {
      const matched = await fetchJobs(sessionId, location, newScore);
      setJobs(matched);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Jobbb Finder</h1>
        <p>Upload your resume. Get matched jobs. Get cover letters.</p>
      </header>

      <FileUpload onUpload={handleUpload} loading={loading} />

      {error && <p className="error">{error}</p>}

      {jobTitle && (
        <p className="detected-title">
          Detected title: <strong>{jobTitle}</strong>
        </p>
      )}

      {jobs.length > 0 && (
        <>
          <Filters minScore={minScore} onMinScoreChange={handleFilterChange} />
          <div className="job-list">
            {jobs.map((job, i) => (
              <JobCard key={i} job={job} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
