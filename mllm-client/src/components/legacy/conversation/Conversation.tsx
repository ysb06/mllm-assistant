import React, { useState } from 'react';
import { ItemType } from '@openai/realtime-api-beta/dist/lib/client.js';
import { X, Edit, Zap, ArrowUp, ArrowDown } from 'react-feather';
import './Conversation.scss';

interface ConversationProps {
  items: ItemType[];
  onDeleteItem: (id: string) => Promise<void>;
}


export function Conversation({ items, onDeleteItem }: ConversationProps) {
  return (
    <div data-component="Conversation">
      <h2 className="content-block-title">Conversation</h2>
      <div className="content-block-body" data-conversation-content>
        {!items.length && `awaiting connection...`}
        {items.map((conversationItem, i) => {
          return (
            <div className="conversation-item" key={conversationItem.id}>
              <div className={`speaker ${conversationItem.role || ''}`}>
                <div>
                  {(conversationItem.role || conversationItem.type).replaceAll('_', ' ')}
                </div>
                <div
                  className="close"
                  onClick={() => onDeleteItem(conversationItem.id)}
                >
                  <X />
                </div>
              </div>
              <div className={`speaker-content`}>
                {/* tool response */}
                {conversationItem.type === 'function_call_output' && (
                  <div>{conversationItem.formatted.output}</div>
                )}
                {/* tool call */}
                {!!conversationItem.formatted.tool && (
                  <div>
                    {conversationItem.formatted.tool.name}(
                    {conversationItem.formatted.tool.arguments})
                  </div>
                )}
                {!conversationItem.formatted.tool &&
                  conversationItem.role === 'user' && (
                    <div>
                      {conversationItem.formatted.transcript ||
                        (conversationItem.formatted.audio?.length ? '(awaiting transcript)' : conversationItem.formatted.text || '(item sent)')}
                    </div>
                  )}
                {!conversationItem.formatted.tool &&
                  conversationItem.role === 'assistant' && (
                    <div>
                      {conversationItem.formatted.transcript || conversationItem.formatted.text || '(truncated)'}
                    </div>
                  )}
                {conversationItem.formatted.file && (
                  <audio
                    src={conversationItem.formatted.file.url}
                    controls
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}




interface TextConversationInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function TextConversationInput({ onSend, disabled }: TextConversationInputProps) {
  const [inputText, setInputText] = useState('');

  const handleSend = () => {
    if (inputText.trim() !== '') {
      onSend(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div data-component="ConversationInput">
      <input
        type="text"
        value={inputText}
        placeholder="Type your message..."
        onChange={(e) => setInputText(e.target.value)}
        onKeyUp={handleKeyPress}
        disabled={disabled}
      />
      <button onClick={handleSend} disabled={disabled || inputText.trim() === ''}>
        Send
      </button>
    </div>
  );
}

export default TextConversationInput;