import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Message, ThinkingStep } from "@/utils/types";
import { Send, Brain, FileSearch, Zap, CheckCircle, XCircle } from "lucide-react";
import { useEffect, useState, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import { query, queryStreaming, StreamingCallbacks } from "@/api/chatService";
import { loadChatHistory, saveChatHistory } from "@/utils/sessionStorage";
import { Link } from "react-router-dom";
import { useTheme } from "@/components/theme-provider";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ChatMessageProps {
    message: Message;
}

function ThinkingStepsComponent({ steps }: { steps: ThinkingStep[] }) {
    const getStepIcon = (step: string) => {
        switch (step) {
            case 'retrieving':
                return <FileSearch className="w-4 h-4 text-blue-500" />;
            case 'retrieved':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'analyzing':
                return <Brain className="w-4 h-4 text-purple-500" />;
            case 'generating':
                return <Zap className="w-4 h-4 text-orange-500" />;
            case 'complete':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'error':
                return <XCircle className="w-4 h-4 text-red-500" />;
            default:
                return <Brain className="w-4 h-4 text-gray-500" />;
        }
    };

    return (
        <div className="space-y-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg mb-2">
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-2">
                🤔 Thinking process...
            </div>
            {steps.map((step, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                    {getStepIcon(step.step)}
                    <span className="text-gray-700 dark:text-gray-300">{step.message}</span>
                    {step.count && (
                        <span className="text-xs text-gray-500 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                            {step.count} docs
                        </span>
                    )}
                </div>
            ))}
        </div>
    );
}

function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.sender === "user";
    return (
        <div className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}>
            <div
                className={`px-4 py-2 rounded-lg max-w-2xl break-words ${isUser
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                    }`}
            >
                {message.thinkingSteps && message.thinkingSteps.length > 0 && (
                    <ThinkingStepsComponent steps={message.thinkingSteps} />
                )}
                <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                            a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                        }}
                    >
                        {message.text}
                    </ReactMarkdown>
                </div>
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
    const streamingRef = useRef<EventSource | null>(null);

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

        // Create a bot message that will be updated with streaming data
        const botMessageId = uuidv4();
        const initialBotMessage: Message = {
            id: botMessageId,
            sender: "bot",
            text: "",
            isStreaming: true,
            thinkingSteps: [],
            status: 'streaming'
        };
        setMessages((prev) => [...prev, initialBotMessage]);

        const callbacks: StreamingCallbacks = {
            onStep: (step) => {
                const thinkingStep: ThinkingStep = {
                    ...step,
                    timestamp: Date.now()
                };

                setMessages((prev) => prev.map((msg) => {
                    if (msg.id === botMessageId) {
                        return {
                            ...msg,
                            thinkingSteps: [...(msg.thinkingSteps || []), thinkingStep]
                        };
                    }
                    return msg;
                }));
            },
            onComplete: (result, meta) => {
                setMessages((prev) => prev.map((msg) => {
                    if (msg.id === botMessageId) {
                        return {
                            ...msg,
                            text: result,
                            isStreaming: false,
                            status: 'complete'
                        };
                    }
                    return msg;
                }));
                setIsLoading(false);
            },
            onError: (error) => {
                setMessages((prev) => prev.map((msg) => {
                    if (msg.id === botMessageId) {
                        return {
                            ...msg,
                            text: `Sorry, I encountered an error: ${error}`,
                            isStreaming: false,
                            status: 'error'
                        };
                    }
                    return msg;
                }));
                setIsLoading(false);
            }
        };

        try {
            streamingRef.current = queryStreaming(currentInput, callbacks);
        } catch (error) {
            callbacks.onError("Failed to start streaming query");
        }
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (streamingRef.current) {
                streamingRef.current.close();
            }
        };
    }, []);

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