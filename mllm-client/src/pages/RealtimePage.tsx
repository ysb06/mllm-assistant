import { useEffect, useRef, useCallback, useState } from 'react';

import './RealtimePage.scss';

function RealtimePageTitle() {
    return (
        <div className="title">
            <img src="/openai-logomark.svg" />
            <span>Realtime Console</span>
        </div>
    )
}

export function RealtimePage() {
    const startTimeRef = useRef<string>(new Date().toISOString());

    return (
        <div data-component="RealtimePage">
            <header>
                <RealtimePageTitle />
            </header>
            <main>
            </main>
        </div>
    )
}

