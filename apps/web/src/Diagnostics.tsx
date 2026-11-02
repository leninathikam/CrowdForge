import { useState } from "react";
import type { GameAction, Session, State } from "./types";

interface Proof {
  matches: boolean;
  audit_matches: boolean;
  digest: string;
  reconstructed_digest: string;
  commands: number;
  verification_ms: number;
  round_id: string;
  version: number;
}
const terrain = ["Ground", "Wall", "Lava", "Bridge"];
const ms = (value: number | null | undefined) =>
  value == null ? "No samples" : `${value.toFixed(3)} ms`;

export default function Diagnostics({
  state,
  session,
  action,
}: {
  state: State;
  session: Session | null;
  action: GameAction;
}) {
  const [proof, setProof] = useState<Proof | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const d = state.diagnostics;
  const twitch = d?.twitch;
  const verify = async () => {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      const response = await fetch(`/api/sessions/${session.id}/proof`);
      const result = await response.json();
      if (!response.ok)
        throw new Error(result.detail || "Replay verification failed.");
      setProof(result);
    } catch (failure) {
      setError((failure as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="diagnostics">
      <div className="eyebrow">WORLD INTEGRITY / RULES {d?.rules ?? 1}</div>
      <h2>Show your work.</h2>
      <p>
        Measured from this session.{" "}
        {state.mode === "live"
          ? "Twitch transport counters cover this connection."
          : "Simulation inputs are synthetic. No live Twitch reception is claimed."}
      </p>
      <dl className="proof-grid">
        <div>
          <dt>Twitch received / delivered</dt>
          <dd>
            {twitch
              ? `${twitch.received} / ${twitch.delivered}`
              : "Not connected"}
          </dd>
        </div>
        <div>
          <dt>Duplicate / stale / limited</dt>
          <dd>
            {twitch
              ? `${twitch.duplicates} / ${twitch.stale} / ${twitch.limited}`
              : "—"}
          </dd>
        </div>
        <div>
          <dt>Round inputs accepted / ignored</dt>
          <dd>
            {d
              ? `${d.vote_receipts.accepted} / ${d.vote_receipts.ignored}`
              : "—"}
          </dd>
        </div>
        <div>
          <dt>World applied / rejected</dt>
          <dd>
            {state.stats.accepted} / {state.stats.rejected}
          </dd>
        </div>
        <div>
          <dt>Validation last / p95</dt>
          <dd>
            {ms(d?.validation_ms_last)} / {ms(d?.validation_ms_p95)}
          </dd>
        </div>
        <div>
          <dt>State / snapshot sequence</dt>
          <dd>
            v{state.version} / {state.snapshot_sequence ?? "—"}
          </dd>
        </div>
      </dl>
      <p className="fine-print">
        Validation: last {d?.validation_samples ?? 0} proposals (maximum 200);
        excludes target search, network and rendering. Accepted inputs include
        vote changes, so they can exceed unique votes. Evidence:{" "}
        {d?.persistence ?? "unknown"}.
      </p>
      {twitch?.last_received_at && (
        <p className="fine-print">
          Last Twitch notification: {twitch.last_received_at}
        </p>
      )}
      <div className="proof-actions">
        <button
          className="secondary"
          disabled={state.phase !== "running"}
          onClick={() => void action("integrity_probe")}
        >
          Test unsafe exit wall
        </button>
        {state.phase === "running" && (
          <button className="secondary" onClick={() => void action("pause")}>
            Pause for replay proof
          </button>
        )}
        <button
          className="primary"
          disabled={busy || state.phase === "running"}
          onClick={() => void verify()}
        >
          {busy ? "Reconstructing…" : "Verify deterministic replay"}
        </button>
      </div>
      <p className="fine-print">
        The exit-wall test is a labeled streamer diagnostic, never an audience
        vote. Replay verification reconstructs this paused or finished round on
        the server.
      </p>
      {error && <p role="alert">{error}</p>}
      {proof && (
        <div className="replay-proof" role="status">
          <strong>
            {proof.matches && proof.audit_matches
              ? "REPLAY VERIFIED"
              : "REPLAY MISMATCH"}
          </strong>
          <p>
            {proof.commands} recorded inputs · {ms(proof.verification_ms)} ·
            state and mutation history compared
          </p>
          <code>{proof.digest}</code>
          {(proof.round_id !== state.round_id ||
            proof.version !== state.version) && (
            <p>
              Evidence is from an earlier state. Pause and verify again for
              current proof.
            </p>
          )}
        </div>
      )}
      <h3>Mutation evidence</h3>
      {!state.audit.length && (
        <p>
          No proposals yet. Start a round and cast a vote or run the diagnostic.
        </p>
      )}
      {[...state.audit].reverse().map((event) => (
        <details className="mutation-proof" key={event.id}>
          <summary>
            {event.accepted ? "APPLIED" : "REJECTED"} · {event.kind} ·{" "}
            {event.timestamp.toFixed(1)}s · v{event.previous_version} → v
            {event.resulting_version}
          </summary>
          <p>{event.reason}</p>
          <code>{event.protocol.join(" → ")}</code>
          {event.metrics && (
            <p>
              Safe route: {event.metrics.before.steps ?? "none"} →{" "}
              {event.metrics.after.steps ?? "none"} steps. Lava-adjacent route
              tiles: {event.metrics.before.hazard_adjacent_tiles} →{" "}
              {event.metrics.after.hazard_adjacent_tiles}. Escape estimate:{" "}
              {event.metrics.minimum_escape_seconds}s.
            </p>
          )}
          <p className="fine-print">
            Lava adjacency describes proximity, not unavoidable damage. Escape
            estimate assumes 5 moves/second plus 0.5s reaction time, not a
            guaranteed human escape.
          </p>
          {!!event.changes?.length && (
            <div className="tile-diff" aria-label="Before and after terrain">
              {event.changes.map((tile) => (
                <span key={`${tile.x},${tile.y}`}>
                  <code>
                    ({tile.x},{tile.y})
                  </code>
                  <i className={`terrain-${tile.before}`}>
                    {terrain[tile.before]}
                  </i>{" "}
                  →{" "}
                  <i className={`terrain-${tile.after}`}>
                    {terrain[tile.after]}
                  </i>
                </span>
              ))}
            </div>
          )}
        </details>
      ))}
    </div>
  );
}
