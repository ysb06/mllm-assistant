import { useEffect, useState } from 'react';
import { StateGraph, EventList } from '../../components/chatbot/LangGraph';
import { IEventElement, IChatElement } from '../../lib/langgraph';
import { ChatList, ChatInput } from '../../components/chatbot/ChatContent';
import { useChatStreaming } from '../../hooks/useChatStreaming';

import './style.scss';
import { Selector } from './Session';
import { v4 as uuidv4 } from 'uuid';


const SERVER_URL = "http://127.0.0.1:8000/agent"

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
    const [sessionList, setSessionList] = useState<string[]>([]);
    const [session, setSession] = useState<string>(uuidv4());

    const [state, actions] = useChatStreaming(
        [{ role: "system", content: "You are very helpful assistant" }],
        {
            serverUrl: SERVER_URL,
            session: session,
            onEventReceived: (event) => {
                console.log('Event received:', event);
            }
        }
    );

    const { messages, events, isStreaming } = state;
    const { sendMessage } = actions;

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
        try {
            await sendMessage(message);
        } catch (error) {
            console.error("Error sending message:", error);
        }
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
                    <ChatList
                        messages={messages}
                        nodeName={events.length ? events[events.length - 1]?.metadata.langgraph_node : undefined}
                    />
                    <ChatInput onSend={handleSend} disabled={isStreaming} />
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