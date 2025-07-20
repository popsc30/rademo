import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import UploadPage from './pages/UploadPage';
import AuthGuard from './components/AuthGuard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/" 
          element={
            <AuthGuard>
              <ChatPage />
            </AuthGuard>
          } 
        />
        <Route 
          path="/upload" 
          element={
            <AuthGuard>
              <UploadPage />
            </AuthGuard>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;