import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Message } from "@/utils/types";
import { Send } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { query } from "@/api/chatService";
import { loadChatHistory, saveChatHistory } from "@/utils/sessionStorage";
import { Link } from "react-router-dom";
import { useTheme } from "@/components/theme-provider";

interface ChatMessageProps {
    message: Message;
}

function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.sender === "user";
    return (
        <div className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`px-4 py-2 rounded-lg max-w-xs lg:max-w-md break-words ${isUser
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
            >
                {message.text}
            </div>
        </div>
    );
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>(loadChatHistory());
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const { setTheme } = useTheme();
    const messagesEndRef = useRef<null | HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    useEffect(() => {
        saveChatHistory(messages);
    }, [messages]);

    const handleSend = async () => {
        if (input.trim() === "" || isLoading) return;

        const userMessage: Message = { id: uuidv4(), sender: "user", text: input };
        setMessages((prev) => [...prev, userMessage]);

        const currentInput = input;
        setInput("");
        setIsLoading(true);

        try {
            const botResponse = await query(currentInput);
            const botMessage: Message = { id: uuidv4(), sender: "bot", text: botResponse };
            setMessages((prev) => [...prev, botMessage]);
        } catch (error) {
            const errorMessage: Message = { id: uuidv4(), sender: "bot", text: "Sorry, I encountered an error. Please try again." };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen">
            <header className="flex items-center justify-between p-4 border-b">
                <h1 className="text-xl font-bold">HR Assistant</h1>
                <div>
                    <Button onClick={() => setTheme("light")} variant="outline" size="sm" className="mr-2">Light</Button>
                    <Button onClick={() => setTheme("dark")} variant="outline" size="sm" className="mr-2">Dark</Button>
                    <Button asChild variant="outline">
                        <Link to="/upload">Upload Document</Link>
                    </Button>
                </div>
            </header>
            <main className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)}
                {isLoading && <ChatMessage message={{ id: "loading", sender: "bot", text: "Thinking..." }} />}
                <div ref={messagesEndRef} />
            </main>
            <footer className="p-4 border-t">
                <div className="flex items-center space-x-2">
                    <Input
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") handleSend() }}
                        disabled={isLoading}
                        className="flex-1"
                    />
                    <Button onClick={handleSend} disabled={isLoading}>
                        <Send className="w-4 h-4" />
                    </Button>
                </div>
            </footer>
        </div>
    );
} 