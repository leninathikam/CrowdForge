export type Kind = "lava" | "wall" | "bridge";
export type GameAction = (
  action: string,
  extra?: Record<string, unknown>,
) => Promise<void>;
export interface WorldEvent {
  id: number;
  time: number;
  kind: string;
  text: string;
}
export interface MutationEvent {
  id: string;
  window: number;
  kind: Kind;
  targets: [number, number][];
  accepted: boolean;
  reason: string;
  timestamp: number;
  previous_version: number;
  resulting_version: number;
  protocol: string[];
}
export interface State {
  schema: number;
  version: number;
  seed: number;
  grid: number[][];
  player: [number, number];
  exit: [number, number];
  health: number;
  elapsed: number;
  remaining: number;
  phase: "ready" | "running" | "paused" | "won" | "lost";
  vote: {
    number: number;
    counts: Record<Kind, number>;
    remaining: number;
    total: number;
    allow_changes: boolean;
    closes_at_round_seconds: number;
  };
  events: WorldEvent[];
  audit: MutationEvent[];
  frozen: boolean;
  mode: "simulation" | "live";
  twitch: { state: string; channel: string; detail: string };
  twitch_configured: boolean;
  twitch_redirect_uri: string;
  stats: { accepted: number; rejected: number; votes: number; chaos: number };
}
export interface Session {
  id: string;
  overlay_token: string;
}
