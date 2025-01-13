import { useEffect, useRef, useCallback, useState } from 'react';

import './ChatPage.scss';

function PageTitle() {
    return (
        <div className="title">
            <img src="/openai-logomark.svg" />
            <span>Realtime Console</span>
        </div>
    )
}

interface IChatElement {
    role: string,
    content: string
}

interface IEventElement {
    data: any,
    event: string,
    metadata: any,
    name: string,
    parent_ids: string[],
    run_id: string,
    tags: string[]
}

export function ChatPage() {
    const startTimeRef = useRef<string>(new Date().toISOString());
    const [messages, setMessages] = useState<IChatElement[]>([
        {   // Initial messages with prompt
            role: "system",
            content: "You are very helpful assistant!"
        },
    ]);
    const [events, setEvents] = useState<IEventElement[]>([]);

    const handleSend = async (message: string) => {
        let newMessages = [
            ...messages,
            { role: "user", content: message },
            { role: "assistant", content: "" }
        ];
        setMessages(newMessages);

        await sendChatMessage(newMessages, (event: any) => {
            setEvents((prevEvents) => [...prevEvents, event]);
            if (event.event === "on_chat_model_stream") {
                setMessages((prevMessages) => {
                    const lastAssistantMessage = prevMessages[prevMessages.length - 1];
                    const newMessages = prevMessages.slice(0, prevMessages.length - 1);
                    return [
                        ...newMessages,
                        { role: "assistant", content: lastAssistantMessage.content + event.data.chunk.content }
                    ];
                });
            }
        });
    };

    return (
        <div data-component="ChatPage">
            <header>
                <PageTitle />
            </header>
            <main>
                <div className="chat-content">
                    <ChatList messages={messages} />
                    <ChatInput onSend={handleSend} disabled={false} />
                </div>
                <div className="chat-sidebar">
                    <EventList events={events} />
                    <LangGraphImage />
                </div>
            </main>
            <footer></footer>
        </div>
    )
}

// Components, 나중에 이동시킬 것

export function LangGraphImage() {
    return (
        <div data-component="LangGraphImage">
            <h2>State Graph</h2>
            <img src="http://127.0.0.1:8000/chat/graph" />
        </div>
    );
}

interface EventListProps {
    events: IEventElement[];
}

export function EventList({ events }: EventListProps) {
    const [expandedEvents, setExpandedEvents] = useState<number[]>([]);
    const listRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [events]);
    const handleExpansion = useCallback((index: number) => {
        setExpandedEvents((prev) => {
            if (prev.includes(index)) {
                return prev.filter((i) => i !== index);
            } else {
                return [...prev, index];
            }
        });
    }, [expandedEvents]);
    return (
        <div ref={listRef} data-component="EventList">
            <h2>Events</h2>
            <div className="event-container">
                {events.map((event, i) => {
                    const isExpanded = expandedEvents.includes(i);
                    return (
                        <div className="event-item" key={i} onClick={() => handleExpansion(i)}>
                            <strong>{i}. {event.event}</strong>
                            {isExpanded && (
                                <pre style={{ whiteSpace: "pre-wrap", marginTop: "4px" }}>
                                    {JSON.stringify(event, null, 2)}
                                </pre>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

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

async function sendChatMessage(messages: IChatElement[], onStreamReceive: (content: IEventElement) => void) {
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
