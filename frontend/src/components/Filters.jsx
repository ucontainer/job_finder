export default function Filters({ minScore, onMinScoreChange }) {
  return (
    <div className="filters">
      <label>
        Min match score: {minScore}%
        <input
          type="range"
          min="0"
          max="100"
          value={minScore}
          onChange={(e) => onMinScoreChange(Number(e.target.value))}
        />
      </label>
    </div>
  );
}
