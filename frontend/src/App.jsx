import { useState } from "react";
import FileUpload from "./components/FileUpload";
import Filters from "./components/Filters";
import JobCard from "./components/JobCard";
import ResumeProfile from "./components/ResumeProfile";
import { uploadResume, fetchJobs, downloadCsvUrl } from "./api/client";
import "./App.css";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [minScore, setMinScore] = useState(40);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [location, setLocationState] = useState("");

  async function handleUpload(file, loc) {
    setLoading(true);
    setError("");
    setJobs([]);
    setProfile(null);
    setLocationState(loc);

    try {
      const upload = await uploadResume(file, loc);
      setProfile({
        job_title: upload.job_title,
        tech_stack: upload.tech_stack || [],
        certifications: upload.certifications || [],
      });
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

      {profile && <ResumeProfile profile={profile} />}

      {jobs.length > 0 && (
        <>
          <div className="results-toolbar">
            <Filters minScore={minScore} onMinScoreChange={handleFilterChange} />
            <a
              href={downloadCsvUrl(sessionId, location, minScore)}
              className="csv-download"
              download
            >
              Download CSV
            </a>
          </div>
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
