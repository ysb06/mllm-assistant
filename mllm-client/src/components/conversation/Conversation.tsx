import React, { useState } from 'react';
import './Conversation.scss';

interface TextInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function TextConversationInput({ onSend, disabled }: TextInputProps) {
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
    <div data-component="Conversation">
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