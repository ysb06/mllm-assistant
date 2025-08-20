import { useState, useCallback, useRef } from 'react';
import { IChatElement, IEventElement } from '../lib/langgraph';
import { streamingClient } from '../lib/streamingClient';

export interface UseChatStreamingOptions {
    serverUrl: string;
    session?: string;
    onEventReceived?: (event: IEventElement) => void;
}

export interface ChatStreamingState {
    messages: IChatElement[];
    events: IEventElement[];
    isStreaming: boolean;
    error: Error | null;
}

export interface ChatStreamingActions {
    sendMessage: (content: string) => Promise<void>;
    setMessages: React.Dispatch<React.SetStateAction<IChatElement[]>>;
    setEvents: React.Dispatch<React.SetStateAction<IEventElement[]>>;
    clearError: () => void;
    cancelStreaming: () => void;
}

export function useChatStreaming(
    initialMessages: IChatElement[] = [],
    options: UseChatStreamingOptions
): [ChatStreamingState, ChatStreamingActions] {
    const [messages, setMessages] = useState<IChatElement[]>(initialMessages);
    const [events, setEvents] = useState<IEventElement[]>([]);
    const [isStreaming, setIsStreaming] = useState<boolean>(false);
    const [error, setError] = useState<Error | null>(null);

    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(async (content: string) => {
        if (isStreaming) {
            console.warn("Already streaming, ignoring new message");
            return;
        }

        setIsStreaming(true);
        setError(null);

        // 새로운 메시지를 추가하고 빈 어시스턴트 응답 준비
        const newMessages = [
            ...messages,
            { role: "user", content },
            { role: "assistant", content: "" }
        ];
        setMessages(newMessages);

        // AbortController 생성
        abortControllerRef.current = streamingClient.createAbortController();

        try {
            await streamingClient.streamChat(
                {
                    url: options.serverUrl,
                    messages: newMessages,
                    session: options.session,
                    signal: abortControllerRef.current.signal
                },
                {
                    onEvent: (event: IEventElement) => {
                        // 이벤트를 이벤트 리스트에 추가
                        setEvents(prevEvents => [...prevEvents, event]);

                        // 외부 콜백 호출
                        options.onEventReceived?.(event);

                        // 스트리밍 메시지 처리
                        if (event.event === "on_chat_model_stream") {
                            switch (event.metadata.langgraph_node) {
                                case "node_run_chatbot":
                                    setMessages(prevMessages => {
                                        const lastAssistantMessage = prevMessages[prevMessages.length - 1];
                                        if (lastAssistantMessage.role === "assistant") {
                                            const updatedMessages = prevMessages.slice(0, prevMessages.length - 1);
                                            return [
                                                ...updatedMessages,
                                                {
                                                    role: "assistant",
                                                    content: lastAssistantMessage.content + event.data.chunk.content
                                                }
                                            ];
                                        }
                                        return prevMessages;
                                    });
                                    break;
                                default:
                                    break;
                            }
                        }
                    },
                    onError: (streamError: Error) => {
                        console.error("Streaming error:", streamError);
                        setError(streamError);
                    },
                    onComplete: () => {
                        console.log("Streaming completed");
                    }
                }
            );
        } catch (sendError) {
            if (sendError instanceof Error && sendError.name !== 'AbortError') {
                console.error("Error sending message:", sendError);
                setError(sendError);
            }
        } finally {
            setIsStreaming(false);
            abortControllerRef.current = null;
        }
    }, [messages, events, isStreaming, options.serverUrl, options.session, options.onEventReceived]);

    const clearError = useCallback(() => {
        setError(null);
    }, []);

    const cancelStreaming = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
            setIsStreaming(false);
        }
    }, []);

    const state: ChatStreamingState = {
        messages,
        events,
        isStreaming,
        error
    };

    const actions: ChatStreamingActions = {
        sendMessage,
        setMessages,
        setEvents,
        clearError,
        cancelStreaming
    };

    return [state, actions];
}