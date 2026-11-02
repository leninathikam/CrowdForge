import ArenaPanel from "./ArenaPanel";
import VotingPanel from "./VotingPanel";
import Dialogs from "./Dialogs";
import { time } from "./format";
import { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowUpRight,
  CircleHelp,
  Flame,
  Gamepad2,
  Layers3,
  Radio,
  ShieldCheck,
  Settings2,
  Swords,
  Twitch,
  Unplug,
  X,
  Zap,
} from "lucide-react";
import { overlay, useGame } from "./useGame";
import "./style.css";

function App() {
  const {
    session,
    state,
    connection,
    error,
    setError,
    create,
    action,
    replay,
  } = useGame();
  const [modal, setModal] = useState<
    "help" | "settings" | "setup" | "overlay" | "diagnostics" | null
  >(null);
  const [sound, setSound] = useState(false);
  const [view, setView] = useState<"arena" | "events">("arena");
  const keys = useRef(new Set<string>()),
    phase = useRef(state?.phase);
  phase.current = state?.phase;
  const latestAction = useRef(action);
  latestAction.current = action;
  const auditCount = useRef(0);

  useEffect(() => {
    if (overlay) return;
    const direction: Record<string, [number, number]> = {
      w: [0, -1],
      arrowup: [0, -1],
      s: [0, 1],
      arrowdown: [0, 1],
      a: [-1, 0],
      arrowleft: [-1, 0],
      d: [1, 0],
      arrowright: [1, 0],
    };
    function keydown(event: KeyboardEvent) {
      if (
        modal ||
        (event.target as HTMLElement).matches("input,textarea,select,button")
      )
        return;
      const key = event.key.toLowerCase();
      if (direction[key]) {
        event.preventDefault();
        keys.current.add(key);
        if (!event.repeat)
          void latestAction.current("move", {
            dx: direction[key][0],
            dy: direction[key][1],
          });
      }
      if (key === " " && !event.repeat) {
        event.preventDefault();
        void latestAction.current(
          phase.current === "paused" ? "resume" : "pause",
        );
      }
      if (key === "escape") keys.current.clear();
    }
    const keyup = (event: KeyboardEvent) =>
      keys.current.delete(event.key.toLowerCase());
    const blur = () => keys.current.clear();
    window.addEventListener("keydown", keydown);
    window.addEventListener("keyup", keyup);
    window.addEventListener("blur", blur);
    const interval = setInterval(() => {
      const key = [...keys.current].at(-1);
      if (key && direction[key] && !modal)
        void latestAction.current("move", {
          dx: direction[key][0],
          dy: direction[key][1],
        });
    }, 150);
    return () => {
      clearInterval(interval);
      keys.current.clear();
      window.removeEventListener("keydown", keydown);
      window.removeEventListener("keyup", keyup);
      window.removeEventListener("blur", blur);
    };
  }, [modal]);

  useEffect(() => {
    const count = state?.audit.length || 0;
    if (count > auditCount.current && sound) {
      const context = new AudioContext();
      const oscillator = context.createOscillator(),
        gain = context.createGain();
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.type = "triangle";
      oscillator.frequency.setValueAtTime(440, context.currentTime);
      oscillator.frequency.exponentialRampToValueAtTime(
        180,
        context.currentTime + 0.16,
      );
      gain.gain.setValueAtTime(0.035, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.2);
      oscillator.start();
      oscillator.stop(context.currentTime + 0.2);
      oscillator.onended = () => void context.close();
    }
    auditCount.current = count;
  }, [state?.audit.length, sound]);

  const connect = () => {
    if (!state?.twitch_configured) {
      setModal("setup");
      return;
    }
    location.href = "/api/auth/start?session=" + session?.id;
  };
  if (!state)
    return (
      <div className="loading">
        <div className="brand-glyph">
          <Swords size={28} />
        </div>
        <h1>
          CROWDFORGE<span>THE WORLD FIGHTS BACK</span>
        </h1>
        <p>{error || "Forging your arena…"}</p>
        {error && !overlay && (
          <button className="primary" onClick={() => location.reload()}>
            Retry connection
          </button>
        )}
      </div>
    );
  const live = state.mode === "live" && state.twitch.state === "connected";

  return (
    <div className={`app ${overlay ? "overlay" : ""}`}>
      {!overlay && (
        <aside className="rail">
          <button
            className="brand-glyph"
            aria-label="CrowdForge home"
            onClick={() => {
              setView("arena");
              setModal(null);
            }}
          >
            <Swords size={25} />
          </button>
          <div className="rail-center">
            <button
              className={view === "arena" ? "rail-active" : ""}
              aria-label="Arena"
              title="Arena"
              onClick={() => setView("arena")}
            >
              <Gamepad2 />
            </button>
            <button
              className={view === "events" ? "rail-active" : ""}
              aria-label="Audience impact timeline"
              title="Audience impact timeline"
              onClick={() => setView("events")}
            >
              <Layers3 />
            </button>
            <button
              aria-label="OBS overlay setup"
              title="OBS overlay"
              onClick={() => setModal("overlay")}
            >
              <Radio />
            </button>
          </div>
          <div className="rail-bottom">
            <button
              aria-label="Developer diagnostics"
              title="Developer diagnostics"
              onClick={() => setModal("diagnostics")}
            >
              <ShieldCheck size={20} />
            </button>
            <button
              aria-label="Settings"
              title="Settings"
              onClick={() => setModal("settings")}
            >
              <Settings2 size={20} />
            </button>
            <button
              aria-label="How to play"
              title="How to play"
              onClick={() => setModal("help")}
            >
              <CircleHelp size={20} />
            </button>
            <span className="avatar">CF</span>
          </div>
        </aside>
      )}
      <div className="workspace">
        <header className="topbar">
          <a className="wordmark" href="/">
            CROWD<span>FORGE</span>
            <span className="brand-sub">THE WORLD FIGHTS BACK</span>
          </a>
          <div className="top-center">
            <span className="slash">/</span> THE FORGE{" "}
            <span className="build-badge">SEASON 01</span>
          </div>
          {!overlay && (
            <div className="top-actions">
              <span className={`mode ${live ? "live" : ""}`}>
                <i />
                {live
                  ? "TWITCH CONNECTED"
                  : state.mode === "simulation"
                    ? "SIMULATION MODE"
                    : "TWITCH " + state.twitch.state.toUpperCase()}
              </span>
              <button
                className="twitch-button"
                onClick={live ? () => void action("disconnect") : connect}
              >
                {live ? <Unplug size={16} /> : <Twitch size={17} />}{" "}
                {live ? state.twitch.channel : "Connect Twitch"}
                {!live && <ArrowUpRight size={15} />}
              </button>
            </div>
          )}
        </header>
        <main>
          {!overlay && (
            <section className="intro">
              <div>
                <div className="eyebrow">
                  <span /> A MULTIPLAYER GAME WITH ONE PLAYER
                </div>
                <h1>
                  Your run. <span>Their rules.</span>
                </h1>
                <p>Make it to the portal. Chat has other plans.</p>
              </div>
              <div className="intro-note">
                <div className="tiny-label">THE OBJECTIVE</div>
                <span>
                  <i className="portal-dot" /> Reach the exit. Survive the
                  crowd.
                </span>
                <small>
                  Every 15 seconds, your audience changes the world.
                </small>
              </div>
            </section>
          )}
          <div className="game-layout">
            <ArenaPanel
              state={state}
              overlay={overlay}
              view={view}
              setView={setView}
              action={action}
              replay={replay}
            />
            <VotingPanel
              state={state}
              overlay={overlay}
              action={action}
              inspect={() => setModal("diagnostics")}
            />
          </div>
          <section className="event-strip">
            <div>
              <span className="tiny-label">
                <Zap size={14} /> WORLD FEED
              </span>
              <span className="feed-line" />
            </div>
            <div className="feed-items" aria-live="polite">
              {state.events
                .slice(-3)
                .reverse()
                .map((event) => (
                  <div className="feed-item" key={event.id}>
                    <span className={`event-dot ${event.kind}`} />
                    <code>{time(event.time)}</code>
                    <span>{event.text}</span>
                  </div>
                ))}
            </div>
            <div className="chaos-counter">
              <span className="tiny-label">CHAOS SCORE</span>
              <strong>
                {String(state.stats.chaos).padStart(3, "0")}
                <Flame size={16} />
              </strong>
            </div>
          </section>
          {!overlay && (
            <footer className="page-footer">
              <span>
                <i
                  className={
                    connection === "connected" ? "connected" : "disconnected"
                  }
                />
                {connection === "connected"
                  ? "World synchronized"
                  : "Reconnecting to server…"}
                <span className="footer-divider">/</span>{" "}
                {state.mode === "simulation"
                  ? "Offline simulation · synthetic audience"
                  : state.twitch.detail}
              </span>
              <div>
                <span>BUILT WITH CODEX</span>
                <span className="footer-divider">/</span>
                <button onClick={() => setModal("help")}>
                  How to play <ArrowUpRight size={12} />
                </button>
              </div>
            </footer>
          )}
        </main>
      </div>
      {!overlay && (
        <div className="touch-controls" aria-label="Touch movement">
          {[
            [0, -1, ArrowUp, "Up"],
            [-1, 0, ArrowLeft, "Left"],
            [0, 1, ArrowDown, "Down"],
            [1, 0, ArrowRight, "Right"],
          ].map(([dx, dy, Icon, label]) => {
            const Component = Icon as typeof ArrowUp;
            return (
              <button
                key={String(label)}
                aria-label={`Move ${label}`}
                onClick={() => void action("move", { dx, dy })}
              >
                <Component size={18} />
              </button>
            );
          })}
        </div>
      )}
      {error && (
        <div role="alert" className="error-toast">
          <span>{error}</span>
          <button aria-label="Dismiss error" onClick={() => setError("")}>
            <X size={16} />
          </button>
        </div>
      )}
      {modal && !overlay && (
        <Dialogs
          modal={modal}
          state={state}
          session={session}
          action={action}
          create={create}
          sound={sound}
          setSound={setSound}
          setError={setError}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
