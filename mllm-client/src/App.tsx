import { ConsolePage } from './pages/ConsolePage';
import './App.scss';
import { RealtimePage } from './pages/RealtimePage';
import { BrowserRouter, Route, Routes } from 'react-router';

function App() {
  return (
    <div data-component="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ConsolePage />} />
          <Route path="/console" element={<RealtimePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
