const LOCAL_RELAY_SERVER_URL: string = process.env.REACT_APP_LOCAL_RELAY_SERVER_URL || '';

import { useEffect, useRef, useCallback, useState } from 'react';

import { RealtimeClient } from '@openai/realtime-api-beta';
import { ItemType } from '@openai/realtime-api-beta/dist/lib/client.js';

import { SessionManager, SessionInfo } from '../components/session-manager/SessionManager';
import { ContextManager, ContextInfo } from '../components/context-manager/ContextManager';
import { Conversation, TextConversationInput } from '../components/conversation/Conversation';

import './RealtimePage.scss';

export function RealtimePage() {
    const apiKey = LOCAL_RELAY_SERVER_URL ? '' : localStorage.getItem('tmp::voice_api_key') || prompt('OpenAI API Key') || '';
    if (apiKey !== '') {
        localStorage.setItem('tmp::voice_api_key', apiKey);
    }

    const [isConnected, setIsConnected] = useState(false);
    const [items, setItems] = useState<ItemType[]>([]);

    // 추후 Session은 별도 컴포넌트로 분리할 예정
    // 분리된 Session에는 아래 Session Related 부분을 모두 포함해야 함
    // Session Related
    const startTimeRef = useRef<string>(new Date().toISOString());
    const clientRef = useRef<RealtimeClient>(
        new RealtimeClient(
            LOCAL_RELAY_SERVER_URL
                ? { url: LOCAL_RELAY_SERVER_URL }
                : {
                    apiKey: apiKey,
                    dangerouslyAllowAPIKeyInBrowser: true,
                }
        )
    );
    const deleteConversationItem = useCallback(async (id: string) => {
        const client = clientRef.current;
        client.deleteItem(id);
    }, []);     // 사용자가 아이템을 삭제할 때 호출되는 함수

    const sessionInfo: SessionInfo = {
        isConnected,
        startTime: startTimeRef.current,
        sessionId: clientRef.current?.realtime?.url || 'N/A',
    };
    // Session Related End

    return (
        <div data-component="RealtimePage">
            <header>
                <RealtimePageTitle />
            </header>
            <main>
                <SessionManager sessionInfo={sessionInfo} />
                <Conversation items={items} onDeleteItem={deleteConversationItem} />
            </main>

        </div>
    )
}

function RealtimePageTitle() {
    return (
        <div className="title">
            <img src="/openai-logomark.svg" />
            <span>Realtime Console</span>
        </div>
    )
}