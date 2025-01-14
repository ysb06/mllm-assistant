import { useEffect, useRef, useCallback, useState } from 'react';
import { IEventElement } from '../../lib/langgraph';

interface EventListProps {
    events: IEventElement[];
}

interface StateGraphProps {
    baseUrl: string;
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

export function StateGraph({ baseUrl }: StateGraphProps) {
    return (
        <div data-component="LangGraphImage">
            <h2>State Graph</h2>
            <img src={baseUrl + "/state-graph"} />
        </div>
    );
}