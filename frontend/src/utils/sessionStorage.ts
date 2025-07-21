import { Message } from "./types";

const CHAT_HISTORY_KEY = "chat_history";

export const saveChatHistory = (messages: Message[]) => {
  try {
    const data = JSON.stringify(messages);
    sessionStorage.setItem(CHAT_HISTORY_KEY, data);
  } catch (error) {
    console.error("Failed to save chat history to session storage:", error);
  }
};

export const loadChatHistory = (): Message[] => {
  try {
    const saved = sessionStorage.getItem(CHAT_HISTORY_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error("Failed to load chat history from session storage:", error);
    return [];
  }
};
