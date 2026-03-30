import { useState } from "react";

export default function FileUpload({ onUpload, loading }) {
  const [file, setFile] = useState(null);
  const [location, setLocation] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;
    onUpload(file, location);
  }

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2>Upload Your Resume</h2>

      <label className="file-label">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />
        {file ? file.name : "Choose PDF..."}
      </label>

      <input
        type="text"
        placeholder="Location (e.g., Berlin, Remote)"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        className="location-input"
      />

      <button type="submit" disabled={!file || loading}>
        {loading ? "Analyzing..." : "Find Jobs"}
      </button>
    </form>
  );
}
