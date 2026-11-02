import {
  Check,
  Flame,
  Hammer,
  ShieldCheck,
  Sparkles,
  Twitch,
  Users,
  Waves,
} from "lucide-react";
import type { State, Kind, GameAction } from "./types";
const choices: {
  kind: Kind;
  title: string;
  description: string;
  Icon: typeof Flame;
  tag: string;
}[] = [
  {
    kind: "lava",
    title: "Lava surge",
    description: "Turn up the heat. Reroute the escape.",
    Icon: Flame,
    tag: "HAZARD",
  },
  {
    kind: "wall",
    title: "Wall forge",
    description: "A new obstacle. A different way out.",
    Icon: Hammer,
    tag: "OBSTACLE",
  },
  {
    kind: "bridge",
    title: "Bridge builder",
    description: "Give the runner a fighting chance.",
    Icon: Waves,
    tag: "SUPPORT",
  },
];

export default function VotingPanel({
  state,
  overlay,
  action,
  inspect,
}: {
  state: State;
  overlay: boolean;
  action: GameAction;
  inspect?: () => void;
}) {
  return (
    <aside className="vote-column">
      <section className="vote-panel">
        <div className="vote-heading">
          <div>
            <span className="tiny-label">THE CROWD DECIDES</span>
            <h2>Forge the next move.</h2>
          </div>
          <Users size={21} />
        </div>
        <div className="vote-clock">
          <span>
            <i />
            {state.frozen
              ? "VOTING FROZEN"
              : state.phase === "running"
                ? "VOTING OPEN"
                : state.phase === "paused"
                  ? "VOTING PAUSED"
                  : "NEXT VOTE"}
          </span>
          <strong>
            {Math.ceil(state.vote.remaining)}
            <small>s</small>
          </strong>
        </div>
        <div className="vote-progress">
          <i style={{ width: `${(state.vote.remaining / 15) * 100}%` }} />
        </div>
        <div className="vote-options">
          {choices.map(({ kind, title, description, Icon, tag }, index) => {
            const count = state.vote.counts[kind],
              percent = state.vote.total
                ? Math.round((count / state.vote.total) * 100)
                : 0;
            return (
              <div className={`vote-option ${kind}`} key={kind}>
                <div className="option-top">
                  <span className="option-icon">
                    <Icon size={21} />
                  </span>
                  <span className="option-type">{tag}</span>
                  <span className="option-index">0{index + 1}</span>
                </div>
                <h3>{title}</h3>
                <p>{description}</p>
                <div className="option-bottom">
                  <code>!{kind}</code>
                  <b>
                    {count}
                    <span>votes</span>
                  </b>
                </div>
                <div className="option-meter">
                  <i style={{ width: `${percent}%` }} />
                </div>
              </div>
            );
          })}
        </div>
        <div className="vote-caption">
          <Users size={14} />
          <b>{state.vote.total}</b> votes this window{" "}
          <span>One voice. One vote.</span>
        </div>
      </section>
      <section className="integrity-panel">
        <div className="integrity-icon">
          <ShieldCheck size={21} />
        </div>
        <div>
          <h3>Chaos. With guardrails.</h3>
          <p>
            Every mutation is checked.
            <br />
            Mutations preserve a lava-free route.
          </p>
        </div>
        <span className="integrity-check">
          <Check size={13} />
        </span>
      </section>
      {!overlay && (
        <button className="text-button integrity-inspect" onClick={inspect}>
          Inspect world integrity
        </button>
      )}
      {!overlay && (
        <section className="simulation-panel">
          {state.mode === "simulation" ? (
            <>
              <div className="tiny-label">
                <Sparkles size={13} /> SIMULATION LAB
              </div>
              <p>Test the crowd before you go live.</p>
              <div>
                {choices.map(({ kind, Icon }) => (
                  <button
                    key={kind}
                    disabled={state.phase !== "running" || state.frozen}
                    aria-label={`Simulate ${kind} vote`}
                    onClick={() => void action("simulate", { choice: kind })}
                  >
                    <Icon size={13} /> +1 {kind}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className="tiny-label">
                <Twitch size={13} /> AUTHENTICATED CHAT
              </div>
              <p>{state.twitch.detail}</p>
              <small>Synthetic votes are disabled in live mode.</small>
            </>
          )}
        </section>
      )}
    </aside>
  );
}
