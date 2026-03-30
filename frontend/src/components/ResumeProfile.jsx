export default function ResumeProfile({ profile }) {
  return (
    <div className="resume-profile">
      <h3>Resume Analysis</h3>

      <div className="profile-field">
        <span className="profile-label">Detected Title</span>
        <span className="profile-value">{profile.job_title}</span>
      </div>

      {profile.tech_stack.length > 0 && (
        <div className="profile-field">
          <span className="profile-label">Tech Stack</span>
          <div className="tag-list">
            {profile.tech_stack.map((tech, i) => (
              <span key={i} className="tag tag-tech">
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {profile.certifications.length > 0 && (
        <div className="profile-field">
          <span className="profile-label">Certifications</span>
          <div className="tag-list">
            {profile.certifications.map((cert, i) => (
              <span key={i} className="tag tag-cert">
                {cert}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
