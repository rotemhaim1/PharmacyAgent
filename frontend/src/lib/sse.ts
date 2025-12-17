export type SseEvent = {
  event: string;
  data: any;
};

export async function* parseSseStream(
  stream: ReadableStream<Uint8Array>
): AsyncGenerator<SseEvent> {
  const reader = stream.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    // Normalize CRLF to LF so we can reliably split on blank lines.
    buffer = buffer.replace(/\r/g, "");

    while (true) {
      const sepIdx = buffer.indexOf("\n\n");
      if (sepIdx === -1) break;

      const rawEvent = buffer.slice(0, sepIdx);
      buffer = buffer.slice(sepIdx + 2);

      // Basic SSE parsing: event + data lines (ignore comments/empty lines)
      let event = "message";
      const dataLines: string[] = [];
      for (const line of rawEvent.split("\n")) {
        if (!line || line.startsWith(":")) continue;
        if (line.startsWith("event:")) event = line.slice("event:".length).trim();
        if (line.startsWith("data:")) dataLines.push(line.slice("data:".length).trimEnd());
      }
      const dataStr = dataLines.join("\n");
      let data: any = dataStr;
      try {
        data = JSON.parse(dataStr);
      } catch {
        // keep as string
      }
      yield { event, data };
    }
  }
}


