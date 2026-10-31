import type { State } from "./types";

/** Reject incompatible or corrupted snapshots before they reach the renderer. */
export function decodeSnapshot(value: unknown): State {
  if (!value || typeof value !== "object")
    throw new Error("Missing world snapshot.");
  const state = value as State;
  if (state.schema !== 1)
    throw new Error("Incompatible world schema. Reload the page.");
  if (!["ready", "running", "paused", "won", "lost"].includes(state.phase))
    throw new Error("Invalid round phase.");
  if (
    ![
      state.version,
      state.seed,
      state.health,
      state.elapsed,
      state.remaining,
    ].every(Number.isFinite)
  )
    throw new Error("Invalid world counters.");
  if (
    !Array.isArray(state.grid) ||
    state.grid.length !== 16 ||
    state.grid.some(
      (row) =>
        !Array.isArray(row) ||
        row.length !== 24 ||
        row.some((tile) => !Number.isInteger(tile) || tile < 0 || tile > 3),
    )
  )
    throw new Error("Invalid arena dimensions or terrain.");
  for (const point of [state.player, state.exit]) {
    if (
      !Array.isArray(point) ||
      point.length !== 2 ||
      !point.every(Number.isInteger) ||
      point[0] < 0 ||
      point[0] >= 24 ||
      point[1] < 0 ||
      point[1] >= 16
    )
      throw new Error("Entity outside the arena.");
  }
  if (
    !state.vote ||
    !Number.isFinite(state.vote.remaining) ||
    !state.vote.counts ||
    !["lava", "wall", "bridge"].every(
      (kind) =>
        Number.isInteger(
          state.vote.counts[kind as keyof typeof state.vote.counts],
        ) && state.vote.counts[kind as keyof typeof state.vote.counts] >= 0,
    )
  )
    throw new Error("Invalid voting snapshot.");
  if (
    !state.twitch ||
    typeof state.twitch.detail !== "string" ||
    !Array.isArray(state.events) ||
    !Array.isArray(state.audit) ||
    !state.stats ||
    !["simulation", "live"].includes(state.mode)
  )
    throw new Error("Incomplete world snapshot.");
  return state;
}
