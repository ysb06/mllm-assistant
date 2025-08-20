import { useEffect, useState } from 'react';
import { IEventElement, IChatElement } from '../../lib/langgraph';
import { ChatList } from '../../components/chatbot/ChatContent';
import { StateGraph, EventList } from '../../components/chatbot/LangGraph';
import { SpeechToText } from '../../components/chatbot/SpeechToText';
import { Selector } from '../AdvancedChat/Session';
import { useChatStreaming } from '../../hooks/useChatStreaming';
import { v4 as uuidv4 } from 'uuid';

import './SpeakChat.scss';

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

interface SidebarTabProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
    events: IEventElement[];
    sessionList: string[];
    session: string;
    onSessionChange: (session: string) => void;
}

function SidebarTabs({ activeTab, onTabChange, events, sessionList, session, onSessionChange }: SidebarTabProps) {
    const tabs = [
        { id: 'events', label: 'Events', component: <EventList events={events} /> },
        { id: 'graph', label: 'Graph', component: <StateGraph baseUrl={SERVER_URL} /> },
        { id: 'session', label: 'Session', component: <Selector options={sessionList} selectedValue={session} onChange={onSessionChange} /> }
    ];

    return (
        <div className="sidebar-tabs">
            <div className="tab-buttons">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => onTabChange(tab.id)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            <div className="tab-content">
                {tabs.find(tab => tab.id === activeTab)?.component}
            </div>
        </div>
    );
}

interface VoiceButtonProps {
    onSpeechResult: (transcript: string) => void;
    disabled: boolean;
}

function VoiceButton({ onSpeechResult, disabled }: VoiceButtonProps) {
    const handleTranscript = (transcript: string) => {
        if (transcript.trim()) {
            onSpeechResult(transcript);
        }
    };

    return (
        <div className="voice-button-container">
            <div className="voice-button-wrapper">
                <SpeechToText onTranscript={handleTranscript} />
            </div>
        </div>
    );
}

export function SpeakChat() {
    const [sessionList, setSessionList] = useState<string[]>([]);
    const [session, setSession] = useState<string>(uuidv4());
    const [activeTab, setActiveTab] = useState<string>('events');

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
    }, []);

    const handleSpeechResult = async (transcript: string) => {
        if (isStreaming) return; // 이미 전송 중이면 무시
        
        try {
            await sendMessage(transcript);
        } catch (error) {
            console.error("Error sending speech message:", error);
        }
    };

    const handleSessionChange = (newSession: string) => {
        setSession(newSession);
    };

    return (
        <div data-component="SpeakChat">
            <header>
                <PageTitle title="Voice Chat Interface" />
            </header>
            <main className="speak-chat-main">
                <div className="chat-area">
                    <div className="chat-messages">
                        <ChatList messages={messages} />
                    </div>
                    <VoiceButton onSpeechResult={handleSpeechResult} disabled={isStreaming} />
                </div>
                <SidebarTabs 
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    events={events}
                    sessionList={sessionList}
                    session={session}
                    onSessionChange={handleSessionChange}
                />
            </main>
        </div>
    );
}