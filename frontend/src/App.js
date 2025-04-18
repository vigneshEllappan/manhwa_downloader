import React from 'react';
import Home from './pages/Home';
import Chapters from './pages/Chapters'
import {
  BrowserRouter as Router,
  Routes,
  Route,
} from 'react-router-dom';

function App() {
  return (
    <React.Fragment>
      <Router>
        <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/:title/chapters" element={<Chapters />} />
        </Routes>
      </Router>
    </React.Fragment>
  );
}

export default App;
