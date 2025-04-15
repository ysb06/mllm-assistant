import { useEffect, useRef, useCallback, useState } from 'react';
import { StateGraph, EventList } from '../../components/chatbot/LangGraph';
import { IEventElement, IChatElement } from '../../lib/langgraph';
import { ChatList, ChatInput, sendChatMessage } from '../../components/chatbot/ChatContent';

import './style.scss';
import { Selector } from './Session';
import { v4 as uuidv4 } from 'uuid';


const SERVER_URL = "http://127.0.0.1:8000/chatbot"

interface IPageTitleProps {
    title: string;
}

function PageTitle({ title }: IPageTitleProps) {
    return (
        <div className="title">
            <img src="/openai-logomark.svg" />
            <span>LangChain Console - {title}</span>
        </div>
    )
}

export function AdvancedChat() {
    // const startTimeRef = useRef<string>(new Date().toISOString());
    const [messages, setMessages] = useState<IChatElement[]>([
        { role: "system", content: "You are very helpful assistant" }
    ]);
    const [events, setEvents] = useState<IEventElement[]>([]);
    const [sessionList, setSessionList] = useState<string[]>([]);
    const [session, setSession] = useState<string>(uuidv4());

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const response = await fetch(`${SERVER_URL}/sessions`);
                if (!response.ok) {
                    console.error("Failed to fetch session list");
                    return;
                }
                const data = await response.json();
                if (data && data.sessions) {
                    setSessionList(data.sessions);
                } else {
                    console.warn("Unexpected response structure:", data);
                }
            } catch (error) {
                console.error("Error fetching sessions:", error);
            }
        };

        fetchSessions();
    }, []); // 빈 배열을 넣어 한 번만 실행되도록

    const handleSend = async (message: string) => {
        let newMessages = [
            ...messages,
            { role: "user", content: message },
            { role: "assistant", content: "" }
        ];
        setMessages(newMessages);

        await sendChatMessage(newMessages, SERVER_URL, (event: any) => {
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
        }, session);
    };

    const handleSessionSelectorChange = (newSession: string) => {
        setSession(newSession);
    };

    return (
        <div data-component="ChatPage">
            <header>
                <PageTitle title="Chatbot with Advanced Function" />
            </header>
            <main>
                <div className="chat-content">
                    <ChatList messages={messages} />
                    <ChatInput onSend={handleSend} disabled={false} />
                </div>
                <div className="chat-sidebar">
                    <EventList events={events} />
                    <div className="session">
                        <StateGraph baseUrl={SERVER_URL} />
                        <Selector options={sessionList} selectedValue={session} onChange={handleSessionSelectorChange} />
                    </div>
                </div>
            </main>
            <footer></footer>
        </div>
    )
}