import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="*" element={<Navigate to="/new" replace />} />
        <Route path="/new" element={<App />} />
        <Route path="/c/:chatId" element={<App />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
