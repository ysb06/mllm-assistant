import { ConsolePage } from './pages/ConsolePage';
import './App.scss';
import { RealtimePage } from './pages/RealtimePage';
import { BrowserRouter, Route, Routes } from 'react-router';

function App() {
  return (
    <div data-component="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RealtimePage />} />
          <Route path="/console" element={<ConsolePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
