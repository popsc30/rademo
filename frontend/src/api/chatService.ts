import axios from "axios";

const API_URL = "http://localhost:8002";

// TypeScript interfaces for streaming responses
export interface StreamingStep {
  step:
    | "retrieving"
    | "retrieved"
    | "analyzing"
    | "generating"
    | "complete"
    | "error";
  message: string;
  count?: number;
  result?: string;
  meta?: {
    documents: any[];
  };
}

export interface StreamingCallbacks {
  onStep: (step: StreamingStep) => void;
  onComplete: (result: string, meta?: any) => void;
  onError: (error: string) => void;
}

export const query = async (message: string) => {
  try {
    const response = await axios.post(`${API_URL}/query`, { query: message });
    return response.data.answer?.[0];
  } catch (error) {
    console.error("Error querying API:", error);
    throw new Error("Failed to get response from API");
  }
};

export const queryStreaming = (
  message: string,
  callbacks: StreamingCallbacks
): EventSource => {
  const encodedQuery = encodeURIComponent(message);
  const eventSource = new EventSource(`${API_URL}/query/stream`, {
    withCredentials: false,
  });

  // Create a POST request manually since EventSource only supports GET
  // We'll use fetch with POST and handle the stream manually
  const controller = new AbortController();

  const handleStream = async () => {
    try {
      const response = await fetch(`${API_URL}/query/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({ query: message }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("Failed to get response reader");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              callbacks.onStep(data);

              if (data.step === "complete") {
                callbacks.onComplete(data.result, data.meta);
                return;
              } else if (data.step === "error") {
                callbacks.onError(data.message);
                return;
              }
            } catch (parseError) {
              console.error("Error parsing SSE data:", parseError);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name !== "AbortError") {
        console.error("Streaming error:", error);
        callbacks.onError(error.message);
      }
    }
  };

  handleStream();

  // Return a mock EventSource-like object for compatibility
  return {
    close: () => controller.abort(),
    readyState: 1,
  } as EventSource;
};

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data.message;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw new Error("File upload failed");
  }
};
