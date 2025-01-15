import { useEffect, useRef, useCallback, useState } from 'react';
import { StateGraph, EventList } from '../../components/chatbot/LangGraph';
import { IEventElement, IChatElement } from '../../lib/langgraph';
import { ChatList, ChatInput, sendChatMessage } from '../../components/chatbot/ChatContent';

import './ChatPage.scss';

interface IChatPageProps {
    title?: string;
    serverUrl?: string;
}

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

export function ChatPage({ title = "Chatbot", serverUrl = "http://127.0.0.1:8000/service/chatbot" }: IChatPageProps) {
    // const startTimeRef = useRef<string>(new Date().toISOString());
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

        await sendChatMessage(newMessages, serverUrl, (event: any) => {
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
                <PageTitle title={title}/>
            </header>
            <main>
                <div className="chat-content">
                    <ChatList messages={messages} />
                    <ChatInput onSend={handleSend} disabled={false} />
                </div>
                <div className="chat-sidebar">
                    <EventList events={events} />
                    <StateGraph baseUrl={serverUrl} />
                </div>
            </main>
            <footer></footer>
        </div>
    )
}