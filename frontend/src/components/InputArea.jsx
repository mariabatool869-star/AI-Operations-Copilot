import { forwardRef } from "react";

const InputArea = forwardRef(function InputArea(
  { value, onChange, onSubmit, onClear, disabled },
  ref
) {
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) onSubmit();
    }
    if (e.key === "Escape") {
      e.preventDefault();
      onClear?.();
    }
  }

  return (
    <div className="input-area glass">
      <div className="input-row">
        <input
          ref={ref}
          type="text"
          className="chat-input"
          placeholder="Ask about plant assets..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-label="Ask about plant assets"
          autoComplete="off"
        />
        <button
          type="button"
          className="send-btn"
          onClick={onSubmit}
          disabled={disabled || !value.trim()}
          aria-label="Send message"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M22 2L11 13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M22 2L15 22L11 13L2 9L22 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span className="send-label">Send</span>
        </button>
      </div>
    </div>
  );
});

export default InputArea;
