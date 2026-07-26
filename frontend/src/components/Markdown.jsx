/**
 * Lightweight markdown renderer for copilot answers.
 * Supports: **bold**, `inline code`, fenced code blocks, lists, headings, line breaks.
 */
export default function Markdown({ content }) {
  if (!content) return null;

  const blocks = parseBlocks(content);

  return (
    <div className="md">
      {blocks.map((block, i) => {
        if (block.type === "code") {
          return (
            <pre key={i} className="md-code">
              <code>{block.text}</code>
            </pre>
          );
        }
        if (block.type === "ul") {
          return (
            <ul key={i} className="md-list">
              {block.items.map((item, j) => (
                <li key={j}>{renderInline(item)}</li>
              ))}
            </ul>
          );
        }
        if (block.type === "ol") {
          return (
            <ol key={i} className="md-list md-list-ordered">
              {block.items.map((item, j) => (
                <li key={j}>{renderInline(item)}</li>
              ))}
            </ol>
          );
        }
        if (block.type === "h") {
          const Tag = `h${block.level}`;
          return (
            <Tag key={i} className={`md-h md-h${block.level}`}>
              {renderInline(block.text)}
            </Tag>
          );
        }
        return (
          <p key={i} className="md-p">
            {renderInline(block.text)}
          </p>
        );
      })}
    </div>
  );
}

function parseBlocks(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.trim().startsWith("```")) {
      i += 1;
      const codeLines = [];
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i += 1;
      }
      i += 1; // closing fence
      blocks.push({ type: "code", text: codeLines.join("\n") });
      continue;
    }

    // Heading
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      blocks.push({ type: "h", level: heading[1].length, text: heading[2] });
      i += 1;
      continue;
    }

    // Unordered list
    if (/^\s*[-*•]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*•]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*•]\s+/, ""));
        i += 1;
      }
      blocks.push({ type: "ul", items });
      continue;
    }

    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ""));
        i += 1;
      }
      blocks.push({ type: "ol", items });
      continue;
    }

    // Blank line → skip (paragraph separator)
    if (!line.trim()) {
      i += 1;
      continue;
    }

    // Paragraph (merge consecutive non-empty, non-special lines)
    const para = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].trim().startsWith("```") &&
      !/^(#{1,3})\s+/.test(lines[i]) &&
      !/^\s*[-*•]\s+/.test(lines[i]) &&
      !/^\s*\d+\.\s+/.test(lines[i])
    ) {
      para.push(lines[i]);
      i += 1;
    }
    blocks.push({ type: "p", text: para.join(" ") });
  }

  return blocks;
}

function renderInline(text) {
  // Split on **bold**, `code`, preserving order
  const parts = [];
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0;
  let match;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) {
      parts.push(text.slice(last, match.index));
    }
    const token = match[0];
    if (token.startsWith("**")) {
      parts.push(
        <strong key={key++}>{token.slice(2, -2)}</strong>
      );
    } else {
      parts.push(
        <code key={key++} className="md-inline-code">
          {token.slice(1, -1)}
        </code>
      );
    }
    last = match.index + token.length;
  }
  if (last < text.length) {
    parts.push(text.slice(last));
  }
  return parts.length ? parts : text;
}
