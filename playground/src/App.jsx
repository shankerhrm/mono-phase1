import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import Playground from './pages/Playground';
import './App.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/playground" element={<Playground />} />
            </Routes>
        </Router>
    );
}

export default App;
