import {
  ArrowRight,
  Clock3,
  Download,
  Heart,
  Pause,
  Play,
  RefreshCw,
  Settings2,
  ShieldCheck,
  Snowflake,
  Swords,
} from "lucide-react";
import Arena from "./Arena";
import { time } from "./format";
import type { State, GameAction } from "./types";
interface Props {
  state: State;
  overlay: boolean;
  view: "arena" | "events";
  setView: (view: "arena" | "events") => void;
  action: GameAction;
  replay: () => Promise<void>;
}
export default function ArenaPanel({
  state,
  overlay,
  view,
  setView,
  action,
  replay,
}: Props) {
  const finished = ["won", "lost"].includes(state.phase);
  const lastMutation = state.audit.at(-1);
  return (
    <section className="arena-panel">
      <div className="panel-heading">
        <div className="arena-title">
          <span className="tiny-label">THE ARENA</span>
          <strong>
            Ember Hollow <span>01</span>
          </strong>
        </div>
        <div className="seed">
          <span>WORLD SEED</span>
          <b>#{state.seed}</b>
          <span className={`state-dot ${state.phase}`} />
          {state.phase.toUpperCase()}
        </div>
      </div>
      <div className="hud">
        <div className="health">
          <Heart size={17} />
          <span className="tiny-label">VITALS</span>
          <div className="health-bars">
            {Array.from({ length: 10 }, (_, i) => (
              <i key={i} className={i * 10 < state.health ? "filled" : ""} />
            ))}
          </div>
          <b>
            {Math.ceil(state.health)}
            <small>/100</small>
          </b>
        </div>
        <div className={`timer ${state.remaining < 20 ? "urgent" : ""}`}>
          <Clock3 size={16} />
          <b data-testid="round-timer">{time(state.remaining)}</b>
          <span>TO ESCAPE</span>
        </div>
        <div className="round-chip">
          ROUND <b>{String(state.vote.number).padStart(2, "0")}</b>
        </div>
      </div>
      <div className="arena-wrap">
        <Arena state={state} />
        {state.phase === "running" &&
          !state.frozen &&
          state.vote.total > 0 &&
          state.vote.remaining <= 3 && (
            <div className="forge-countdown" role="status">
              CHAT IS FORGING <b>{Math.ceil(state.vote.remaining)}</b>
            </div>
          )}
        {view === "events" && !overlay && (
          <div className="timeline-view">
            <div className="eyebrow">AUDIENCE IMPACT REPLAY</div>
            <h2>Every turn of the world.</h2>
            <p>
              Seed #{state.seed} · {state.stats.votes} counted votes ·{" "}
              {state.stats.chaos} chaos
            </p>
            <div className="timeline-list">
              {state.events.map((event) => (
                <div key={event.id}>
                  <code>{time(event.time)}</code>
                  <i className={event.kind} />
                  <span>{event.text}</span>
                </div>
              ))}
            </div>
            <button className="primary" onClick={() => void replay()}>
              <Download size={16} /> Export deterministic replay
            </button>
            <button className="text-button" onClick={() => setView("arena")}>
              Back to arena <ArrowRight size={15} />
            </button>
          </div>
        )}
        {state.phase === "ready" && view === "arena" && (
          <div className="arena-curtain">
            <div className="curtain-symbol">
              <Swords size={28} />
            </div>
            <div className="tiny-label">WELCOME TO EMBER HOLLOW</div>
            <h2>
              One way out.
              <br />
              <em>A thousand ways to stop you.</em>
            </h2>
            <p>
              You're the runner. The audience is the architect.
              <br />
              Keep moving. The world won't wait.
            </p>
            {!overlay && (
              <button
                className="primary start"
                onClick={() => {
                  void action("start");
                  (document.activeElement as HTMLElement)?.blur();
                }}
              >
                <Play size={16} fill="currentColor" /> Enter the arena{" "}
                <ArrowRight size={17} />
              </button>
            )}
            <span className="curtain-hint">
              {overlay
                ? "Waiting for streamer to begin"
                : "WASD / ARROW KEYS TO MOVE"}
            </span>
          </div>
        )}
        {state.phase === "paused" && view === "arena" && (
          <div className="arena-curtain paused">
            <Pause size={32} />
            <h2>The world can wait.</h2>
            <p>Round timer and voting are paused.</p>
            {!overlay && (
              <button
                className="primary"
                onClick={() => {
                  void action("resume");
                  (document.activeElement as HTMLElement)?.blur();
                }}
              >
                <Play size={16} /> Resume round
              </button>
            )}
          </div>
        )}
        {finished && view === "arena" && (
          <div className="arena-curtain result">
            <div className="eyebrow">ROUND COMPLETE</div>
            <h2>
              {state.phase === "won"
                ? "You beat the world."
                : "The crowd wins this one."}
            </h2>
            <p>
              {state.phase === "won"
                ? "A good escape deserves an encore."
                : "Every great escape starts with another try."}
            </p>
            <div className="result-stats">
              <div>
                <b>{state.stats.votes}</b>
                <span>VOTES COUNTED</span>
              </div>
              <div>
                <b>{state.stats.accepted}</b>
                <span>WORLD CHANGES</span>
              </div>
              <div>
                <b>{state.stats.chaos}</b>
                <span>CHAOS SCORE</span>
              </div>
            </div>
            {!overlay && (
              <>
                <button
                  className="primary"
                  onClick={() => void action("reset")}
                >
                  <RefreshCw size={16} /> Forge another run
                </button>
                <button
                  className="text-button"
                  onClick={() => setView("events")}
                >
                  See the impact timeline <ArrowRight size={16} />
                </button>
              </>
            )}
          </div>
        )}
        {lastMutation &&
          state.elapsed - lastMutation.timestamp < 3 &&
          state.phase === "running" && (
            <div
              className={`mutation-toast ${lastMutation.accepted ? "" : "blocked"}`}
            >
              <ShieldCheck size={20} />
              <div>
                <b>
                  {lastMutation.accepted
                    ? `${lastMutation.kind.toUpperCase()} FORGED`
                    : "MUTATION BLOCKED"}
                </b>
                <span>{lastMutation.reason}</span>
              </div>
            </div>
          )}
        <span className="map-coordinate">
          EMBER HOLLOW / {state.grid[0].length} × {state.grid.length}
        </span>
      </div>
      <div className="arena-footer">
        <div className="key-hints">
          <span>
            <kbd>W</kbd>
            <kbd>A</kbd>
            <kbd>S</kbd>
            <kbd>D</kbd> Move
          </span>
          <span>
            <kbd>SPACE</kbd> Pause
          </span>
        </div>
        <div className="legend">
          <span>
            <i className="safe" />
            Safe ground
          </span>
          <span>
            <i className="danger" />
            Lava
          </span>
          <span>
            <i className="exit" />
            Exit portal
          </span>
        </div>
      </div>
      {!overlay && (
        <div className="streamer-controls">
          <span className="tiny-label">
            <Settings2 size={13} /> STREAMER CONTROLS
          </span>
          <div>
            <button
              onClick={() =>
                void action(state.phase === "paused" ? "resume" : "pause")
              }
              disabled={state.phase === "ready" || finished}
            >
              {state.phase === "paused" ? (
                <Play size={14} />
              ) : (
                <Pause size={14} />
              )}{" "}
              {state.phase === "paused" ? "Resume" : "Pause"}
            </button>
            <button
              className={state.frozen ? "selected" : ""}
              onClick={() => void action("freeze")}
              disabled={state.phase === "ready" || finished}
            >
              <Snowflake size={14} />
              {state.frozen ? "Unfreeze votes" : "Freeze votes"}
            </button>
            <button
              onClick={() => void action("rescue")}
              disabled={state.phase === "ready" || finished}
            >
              <Heart size={14} /> Rescue
            </button>
            <button onClick={() => void action("reset")} title="Reset round">
              <RefreshCw size={14} />
              <span>Reset</span>
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
