import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ChatPage from "@/pages/ChatPage";
import UploadPage from "@/pages/UploadPage";
import { ThemeProvider } from "@/components/theme-provider";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
