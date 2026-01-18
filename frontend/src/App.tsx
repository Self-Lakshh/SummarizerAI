import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Layout from '@/components/Layout';
import HomePage from '@/pages/HomePage';
import UploadPage from '@/pages/UploadPage';
import SummarizePage from '@/pages/SummarizePage';
import ChatPage from '@/pages/ChatPage';
import FlashcardsPage from '@/pages/FlashcardsPage';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="summarize" element={<SummarizePage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="flashcards" element={<FlashcardsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}

export default App;
