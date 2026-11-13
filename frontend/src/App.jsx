import { useCallback, useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import Footer from "./components/Footer.jsx";
import SourceViewer from "./components/SourceViewer.jsx";
import HomeIntro from "./pages/HomeIntro.jsx";
import AuthPage from "./pages/AuthPage.jsx";
import Landing from "./pages/Landing.jsx";
import ChatPage from "./pages/ChatPage.jsx";
import Noticeboard from "./pages/Noticeboard.jsx";
import Tickets from "./pages/Tickets.jsx";
import HowItWorks from "./pages/HowItWorks.jsx";
import TestingPlan from "./pages/TestingPlan.jsx";
import AdminWorkspace from "./pages/AdminWorkspace.jsx";
import {
  currentStudent,
  getMode,
  isStudentLoggedIn,
  refreshStudent,
  studentLogout,
} from "./lib/api.js";

// Pages a signed-in student may reach. The home intro, noticeboard and the
// information pages stay public; the chatbot and tickets require a student
// account.
const STUDENT_ONLY = new Set(["chat", "tickets"]);

/**
 * CampusMate application shell.
 *
 * Holds global appearance/accessibility state, the active page, the shared chat
 * context, the source viewer and the student session. Pages are modular
 * components under `pages/`.
 */
export default function App() {
  const [page, setPage] = useState("home");
  const [theme, setTheme] = useState(localStorage.getItem("cm-theme") || "dark");
  const [largeText, setLargeText] = useState(localStorage.getItem("cm-large") === "true");
  const [highContrast, setHighContrast] = useState(localStorage.getItem("cm-contrast") === "true");
  const [reduceMotion, setReduceMotion] = useState(localStorage.getItem("cm-motion") === "true");
  const [mode, setMode] = useState(getMode());

  const [studentAccount, setStudentAccount] = useState(currentStudent());
  const [authMode, setAuthMode] = useState("signin");

  const [chatContext, setChatContext] = useState({});
  const [pendingQuestion, setPendingQuestion] = useState(null);
  const [sourceCitation, setSourceCitation] = useState(null);
  const [ticketPreset, setTicketPreset] = useState(null);

  useEffect(() => {
    const update = (event) => setMode(event.detail);
    window.addEventListener('campusmate:mode-change', update);
    return () => window.removeEventListener('campusmate:mode-change', update);
  }, []);

  useEffect(() => {
    if (isStudentLoggedIn())
      refreshStudent().then((account) => account && setStudentAccount(account));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("cm-theme", theme);
  }, [theme]);
  useEffect(() => {
    document.documentElement.classList.toggle("large-text", largeText);
    localStorage.setItem("cm-large", largeText);
  }, [largeText]);
  useEffect(() => {
    document.documentElement.classList.toggle("high-contrast", highContrast);
    localStorage.setItem("cm-contrast", highContrast);
  }, [highContrast]);
  useEffect(() => {
    document.documentElement.classList.toggle("reduce-motion", reduceMotion);
    localStorage.setItem("cm-motion", reduceMotion);
  }, [reduceMotion]);

  const navigate = useCallback(
    (next) => {
      // The chatbot and tickets are for signed-in students. Send visitors to the
      // auth page instead of the protected page.
      if (STUDENT_ONLY.has(next) && !isStudentLoggedIn()) {
        setAuthMode("signin");
        next = "auth";
      }
      setPage(next);
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      setMode(getMode());
    },
    [reduceMotion]
  );

  const openAuth = useCallback(
    (which) => {
      setAuthMode(which);
      navigate("auth");
    },
    [navigate]
  );

  const handleStudentAuthed = useCallback(() => {
    setStudentAccount(currentStudent());
    setPage("chat");
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  }, [reduceMotion]);

  const handleStudentLogout = useCallback(() => {
    studentLogout();
    setStudentAccount(null);
    setPage("home");
    window.scrollTo({ top: 0, behavior: "auto" });
  }, []);

  const handleAsk = useCallback(
    (question) => {
      if (!isStudentLoggedIn()) {
        openAuth("signin");
        return;
      }
      setPendingQuestion(question);
      navigate("chat");
    },
    [navigate, openAuth]
  );

  const handleRaiseTicket = useCallback(
    (result) => {
      if (!isStudentLoggedIn()) {
        openAuth("signin");
        return;
      }
      setTicketPreset({
        category: result?.category || undefined,
        description: result?.answer ? `Related to: ${result.answer}` : "",
      });
      navigate("tickets");
    },
    [navigate, openAuth]
  );

  const student = isStudentLoggedIn() ? studentAccount : null;

  return (
    <div className="app-shell">
      <Header
        page={page}
        onNavigate={navigate}
        theme={theme}
        onTheme={() => setTheme(theme === "light" ? "dark" : "light")}
        largeText={largeText}
        onLargeText={() => setLargeText((v) => !v)}
        highContrast={highContrast}
        onHighContrast={() => setHighContrast((v) => !v)}
        reduceMotion={reduceMotion}
        onReduceMotion={() => setReduceMotion((v) => !v)}
        mode={mode}
        student={student}
        onSignIn={() => openAuth("signin")}
        onSignUp={() => openAuth("signup")}
        onLogout={handleStudentLogout}
      />

      {page === "home" &&
        (student ? (
          <Landing onNavigate={navigate} onAsk={handleAsk} />
        ) : (
          <HomeIntro
            student={student}
            onNavigate={navigate}
            onSignIn={() => openAuth("signin")}
            onSignUp={() => openAuth("signup")}
          />
        ))}
      {page === "auth" && (
        <AuthPage
          key={authMode}
          initialMode={authMode}
          onNavigate={navigate}
          onAuthed={handleStudentAuthed}
        />
      )}
      {page === "chat" && (
        <ChatPage
          context={chatContext}
          onContextChange={setChatContext}
          onOpenSource={setSourceCitation}
          onAskTopic={handleAsk}
          onNavigate={navigate}
          pendingQuestion={pendingQuestion}
          onConsumePending={() => setPendingQuestion(null)}
        />
      )}
      {page === "notices" && <Noticeboard onOpenSource={setSourceCitation} />}
      {page === "tickets" && <Tickets preset={ticketPreset} onNavigate={navigate} />}
      {page === "how" && <HowItWorks />}
      {page === "testing" && <TestingPlan />}
      {page === "admin" && <AdminWorkspace onNavigate={navigate} />}

      <Footer onNavigate={navigate} student={student} />

      <SourceViewer citation={sourceCitation} onClose={() => setSourceCitation(null)} />
    </div>
  );
}
