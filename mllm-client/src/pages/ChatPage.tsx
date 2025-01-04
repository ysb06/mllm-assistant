import { useEffect, useRef, useCallback, useState } from 'react';

import './ChatPage.scss';
import { n } from 'react-router/dist/development/fog-of-war-DU_DzpDb';

function PageTitle() {
    return (
        <div className="title">
            <img src="/openai-logomark.svg" />
            <span>Realtime Console</span>
        </div>
    )
}

interface IMessage {
    role: string,
    content: string
}

export function ChatPage() {
    const startTimeRef = useRef<string>(new Date().toISOString());
    const [messages, setMessages] = useState<IMessage[]>([
        {
            role: "system",
            content: "You are very helpful assistant!"
        },
    ]);

    const handleSend = async (message: string) => {
        let newMessages = [
            ...messages,
            { role: "user", content: message },
        ];
        setMessages(newMessages);

        let assistantMessage = { role: "assistant", content: "" }
        await sendChatMessage(newMessages, (chunkContent) => {
            assistantMessage.content += chunkContent;
            setMessages([...newMessages, assistantMessage]);
        });
    };

    return (
        <div data-component="ChatPage">
            <header>
                <PageTitle />
            </header>
            <main>
                <ChatList messages={messages} />
                <ChatInput onSend={handleSend} disabled={false} />
            </main>
            <footer></footer>
        </div>
    )
}

// Components, 나중에 이동시킬 것

interface ChatListProps {
    messages: IMessage[];
}

export function ChatList({ messages }: ChatListProps) {
    return (
        <div data-component="ChatList">
            {messages.map((message, i) => {
                return (
                    <div key={i}>
                        {message.role}: {message.content}
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
        if (event.key === "Enter" && !event.shiftKey) {
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
                onKeyUp={handleKeyPress}
                disabled={disabled}
            />
            <button onClick={handleSend} disabled={disabled || inputText.trim() === ""}>
                Send
            </button>
        </div>
    );
}

async function sendChatMessage(messages: IMessage[], onStreamReceive: (content: string) => void) {
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
        const response = await fetch("http://127.0.0.1:8000/chat", request);

        if (!response.ok || !response.body) {
            console.error("Network response was not ok or no body.");
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            const chunkText = decoder.decode(value, { stream: true });
            const chunkObj = JSON.parse(chunkText);
            console.log("Chunk text:", chunkObj.content);
            onStreamReceive(chunkObj.content);
        }
        console.log("Done streaming.");
    } catch (error) {
        console.error("Fetch or streaming error:", error);
    }
}
