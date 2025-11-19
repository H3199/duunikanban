import { Route, Routes } from "react-router-dom";
import HomePage from "./routes/HomePage";
import JobPage from "./pages/JobPage";

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/job/:id" element={<JobPage />} />
    </Routes>
  );
}
