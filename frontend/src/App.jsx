import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import ResearchLayout from "./components/ResearchLayout";
import Dashboard from "./pages/Dashboard";
import ResearchSetup from "./pages/ResearchSetup";
import Literature from "./pages/Literature";
import Screening from "./pages/Screening";
import Evidence from "./pages/Evidence";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import BasePaperGuide from "./pages/BasePaperGuide";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { getToken } from "./services/api";

function RequireAuth() {
  const location = useLocation();
  const [token, setToken] = useState(getToken);

  useEffect(() => {
    const refreshToken = () => setToken(getToken());
    window.addEventListener("auth:expired", refreshToken);
    window.addEventListener("storage", refreshToken);
    return () => {
      window.removeEventListener("auth:expired", refreshToken);
      window.removeEventListener("storage", refreshToken);
    };
  }, []);

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route element={<RequireAuth />}>
          <Route element={<ResearchLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/research/new" element={<ResearchSetup />} />
            <Route path="/literature" element={<Literature />} />
            <Route path="/screening" element={<Screening />} />
            <Route path="/evidence" element={<Evidence />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/base-paper-guide" element={<BasePaperGuide />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
