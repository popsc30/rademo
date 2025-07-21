export interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  isStreaming?: boolean;
  thinkingSteps?: ThinkingStep[];
  status?: "sending" | "streaming" | "complete" | "error";
}

export interface ThinkingStep {
  step:
    | "retrieving"
    | "retrieved"
    | "analyzing"
    | "generating"
    | "complete"
    | "error";
  message: string;
  count?: number;
  timestamp: number;
}

export interface StreamingMessage extends Message {
  isStreaming: true;
  thinkingSteps: ThinkingStep[];
  status: "streaming" | "complete" | "error";
}
