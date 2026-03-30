export default function CoverLetterModal({
  letter,
  jobTitle,
  company,
  onClose,
}) {
  function handleCopy() {
    navigator.clipboard.writeText(letter);
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>
          Cover Letter — {jobTitle} at {company}
        </h3>
        <p className="cover-letter-text">{letter}</p>
        <div className="modal-actions">
          <button onClick={handleCopy}>Copy</button>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
