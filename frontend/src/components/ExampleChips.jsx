const EXAMPLES = [
  "How is pump P-104?",
  "Risk for compressor C-7?",
  "Show me recent anomalies",
  "What is the current vibration on P-104?",
];

export default function ExampleChips({ onSelect, disabled }) {
  return (
    <div className="example-row" aria-label="Example questions">
      <div className="example-scroll">
        {EXAMPLES.map((q) => (
          <button
            key={q}
            type="button"
            className="example-chip"
            disabled={disabled}
            onClick={() => onSelect(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
