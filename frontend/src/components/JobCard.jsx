import { useState } from "react";
import CoverLetterModal from "./CoverLetterModal";

export default function JobCard({ job }) {
  const [showLetter, setShowLetter] = useState(false);

  return (
    <div className="job-card">
      <div className="job-card-header">
        <h3>{job.job_title}</h3>
        <span className="match-score">{job.match_score}%</span>
      </div>

      <p className="company">{job.company}</p>
      <p className="date">Posted: {job.posting_date}</p>

      {job.why_work_here && (
        <div className="why-work-here">
          <span className="why-label">Why work here:</span>
          <p>{job.why_work_here}</p>
        </div>
      )}

      <div className="job-card-actions">
        <button onClick={() => setShowLetter(true)}>View Cover Letter</button>
        <a href={job.job_url} target="_blank" rel="noopener noreferrer">
          Apply
        </a>
      </div>

      {showLetter && (
        <CoverLetterModal
          letter={job.cover_letter}
          jobTitle={job.job_title}
          company={job.company}
          onClose={() => setShowLetter(false)}
        />
      )}
    </div>
  );
}
