import { BrowserRouter, Route, Routes } from 'react-router';
import { AdvancedChat } from './pages/AdvancedChat/Console';
import { SpeakChat } from './pages/SpeakChat/SpeakChat';
import './App.scss';

function App() {
  return (
    <div data-component="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AdvancedChat />} />
          <Route path="/speak" element={<SpeakChat />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
