import { BrowserRouter, Route, Routes } from 'react-router';
import { ChatPage } from './pages/BaseChat/ChatPage';
import { ConsolePage } from './pages/OpenAIChat/ConsolePage';
import { AdvancedChat } from './pages/AdvancedChat/Console';
import './App.scss';

function App() {
  return (
    <div data-component="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AdvancedChat />} />
          <Route path="/chatbot" element={<ChatPage />} />
          <Route path="/console" element={<ConsolePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
