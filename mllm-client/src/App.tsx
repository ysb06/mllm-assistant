import { BrowserRouter, Route, Routes } from 'react-router';
import { ChatPage } from './pages/ChatPage';
import { ConsolePage } from './pages/ConsolePage';
import './App.scss';

function App() {
  return (
    <div data-component="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/console" element={<ConsolePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
