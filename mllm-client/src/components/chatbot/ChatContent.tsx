import { useEffect, useRef, useCallback, useState } from 'react';
import { IEventElement, IChatElement } from '../../lib/langgraph';

interface ChatListProps {
    messages: IChatElement[];
}

export function ChatList({ messages }: ChatListProps) {
    const listRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div ref={listRef} data-component="ChatList">
            {messages.map((message, i) => {
                return (
                    <div className={message.role} key={i}>
                        {message.content}
                    </div>
                );
            })}
        </div>
    );
}

interface ChatInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [inputText, setInputText] = useState("");

    const handleSend = () => {
        if (inputText.trim() !== "") {
            onSend(inputText.trim());
            setInputText("");
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
            event.preventDefault();
            handleSend();
        }
    };

    return (
        <div data-component="ChatInput">
            <textarea
                value={inputText}
                placeholder="Type your message..."
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={disabled}
            />
            <button onClick={handleSend} disabled={disabled || inputText.trim() === ""}>
                Send
            </button>
        </div>
    );
}

export async function sendChatMessage(messages: IChatElement[], url: string, onStreamReceive: (content: IEventElement) => void) {
    const content = {
        messages: messages,
    }
    const request = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(content),
    };

    try {
        const response = await fetch(url, request);

        if (!response.ok || !response.body) {
            console.error("Network error or empty body.");
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        // FastAPI의 StreamingResponse 처리
        let buffer = "";
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";     // lines.pop()이 true면 그대로, false면 "" 반환

            for (const line of lines) {
                if (line.trim() !== "") {
                    const obj = JSON.parse(line);
                    onStreamReceive(obj);
                }
            }
        }
    } catch (error) {
        console.error("Fetch or streaming error:", error);
    }
}