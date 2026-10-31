import { describe, expect, it } from "vitest";
import { decodeSnapshot } from "./wire";

const fixture = () => ({
  schema: 1,
  version: 0,
  seed: 1847,
  health: 100,
  elapsed: 0,
  remaining: 100,
  phase: "ready",
  grid: Array.from({ length: 16 }, () => Array(24).fill(0)),
  player: [2, 13],
  exit: [21, 2],
  vote: { remaining: 15, counts: { lava: 0, wall: 0, bridge: 0 } },
  twitch: { detail: "Simulation" },
  events: [],
  audit: [],
  stats: {},
  mode: "simulation",
});
describe("versioned server snapshots", () => {
  it("accepts a valid full state", () =>
    expect(decodeSnapshot(fixture()).player).toEqual([2, 13]));
  it("rejects an incompatible protocol", () =>
    expect(() => decodeSnapshot({ ...fixture(), schema: 2 })).toThrow(
      "schema",
    ));
  it("rejects missing state", () =>
    expect(() => decodeSnapshot(null)).toThrow());
  it("rejects a truncated map", () =>
    expect(() => decodeSnapshot({ ...fixture(), grid: [[0]] })).toThrow(
      "arena",
    ));
  it("rejects unknown terrain", () => {
    const state = fixture();
    state.grid[0][0] = 5;
    expect(() => decodeSnapshot(state)).toThrow("terrain");
  });
  it("rejects out-of-range entity coordinates", () =>
    expect(() => decodeSnapshot({ ...fixture(), player: [24, 1] })).toThrow(
      "outside",
    ));
  it("rejects fractional or negative votes", () => {
    const state = fixture();
    state.vote.counts.lava = -1;
    expect(() => decodeSnapshot(state)).toThrow("voting");
  });
  it("rejects non-finite counters", () =>
    expect(() => decodeSnapshot({ ...fixture(), health: NaN })).toThrow(
      "counters",
    ));
});
