import { useEffect, useRef } from "react";
import type { State } from "./types";

const TILE = 36,
  PAD = 24,
  WIDTH = 24 * TILE + PAD * 2,
  HEIGHT = 16 * TILE + PAD * 2;
const hash = (x: number, y: number, seed: number) =>
  Math.abs(Math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453) % 1;

function render(
  ctx: CanvasRenderingContext2D,
  state: State,
  frame: number,
  reduced: boolean,
  visualPlayer: [number, number],
  damageFlash: number,
) {
  const t = reduced ? 0 : frame / 1000;
  ctx.clearRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = "#101713";
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.save();
  ctx.translate(PAD, PAD);
  const recent = state.audit
    .filter((a) => a.accepted && state.elapsed - a.timestamp < 1.2)
    .flatMap((a) => a.targets.map((p) => p.join(",")));
  for (let y = 0; y < state.grid.length; y++)
    for (let x = 0; x < state.grid[y].length; x++) {
      const tile = state.grid[y][x],
        px = x * TILE,
        py = y * TILE,
        h = hash(x, y, state.seed);
      const border = x === 0 || y === 0 || x === 23 || y === 15;
      if (tile === 0) {
        ctx.fillStyle = h > 0.7 ? "#253b30" : h > 0.3 ? "#23382e" : "#20352c";
        ctx.fillRect(px, py, TILE, TILE);
        ctx.fillStyle = "#2b4335";
        ctx.fillRect(px + 1, py + 1, TILE - 2, 1);
        ctx.fillStyle = "#1c3027";
        ctx.fillRect(px, py + TILE - 1, TILE, 1);
        ctx.fillStyle = "#3b5340";
        if (h > 0.68) {
          ctx.fillRect(px + 8, py + 11, 3, 2);
          ctx.fillRect(px + 22, py + 25, 2, 3);
        }
        if (h < 0.18) {
          ctx.fillStyle = "#546342";
          ctx.fillRect(px + 16, py + 22, 2, 5);
          ctx.fillRect(px + 13, py + 22, 2, 2);
        }
      } else if (tile === 1) {
        ctx.fillStyle = border ? "#19231e" : "#1a2921";
        ctx.fillRect(px, py, TILE, TILE);
        if (border) {
          ctx.fillStyle = "#303b30";
          ctx.fillRect(px + 1, py + 1, 34, 27);
          ctx.fillStyle = "#3b4838";
          ctx.fillRect(px + 1, py + 1, 34, 3);
          ctx.fillStyle = "#242f27";
          ctx.fillRect(px + 2, py + 17, 32, 2);
          ctx.fillRect(px + 17, py + 3, 2, 14);
        } else {
          ctx.fillStyle = "#344936";
          ctx.fillRect(px + 3, py + 3, 30, 24);
          ctx.fillStyle = "#506044";
          ctx.fillRect(px + 3, py + 3, 30, 4);
          ctx.fillStyle = "#42563c";
          ctx.fillRect(px + 3, py + 7, 5, 18);
          ctx.fillStyle = "#293c2c";
          ctx.fillRect(px + 9, py + 16, 22, 3);
          ctx.fillStyle = "#668051";
          if (h > 0.6) {
            ctx.fillRect(px + 7, py + 4, 9, 3);
            ctx.fillRect(px + 13, py + 7, 5, 3);
          }
        }
      } else if (tile === 2) {
        ctx.fillStyle = "#8d3523";
        ctx.fillRect(px, py, TILE, TILE);
        ctx.fillStyle = "#d75027";
        ctx.fillRect(px + 2, py + 3, 32, 29);
        ctx.fillStyle = "#f57a35";
        const offset = Math.floor(Math.sin(t * 2 + h * 8) * 3);
        ctx.fillRect(px + 5, py + 8 + offset, 18, 3);
        ctx.fillRect(px + 16, py + 22 - offset, 15, 3);
        ctx.fillStyle = "#ffbf66";
        ctx.fillRect(px + 6, py + 8 + offset, 5, 2);
        ctx.fillStyle = "#542d22";
        ctx.fillRect(px + 4, py + 17, 7, 5);
        ctx.fillRect(px + 26, py + 5, 5, 4);
      } else {
        ctx.fillStyle = "#223c39";
        ctx.fillRect(px, py, TILE, TILE);
        for (let j = 0; j < 4; j++) {
          ctx.fillStyle = j % 2 ? "#9a794c" : "#aa8758";
          ctx.fillRect(px + 2, py + j * 8 + 2, 32, 6);
          ctx.fillStyle = "#5d533c";
          ctx.fillRect(px + 6, py + j * 8 + 3, 2, 2);
          ctx.fillRect(px + 28, py + j * 8 + 3, 2, 2);
        }
        ctx.fillStyle = "#74b2a0";
        ctx.fillRect(px, py, 2, TILE);
        ctx.fillRect(px + 34, py, 2, TILE);
      }
      if (recent.includes(`${x},${y}`)) {
        ctx.strokeStyle = "#f9d29b";
        ctx.lineWidth = 2;
        ctx.strokeRect(px + 2, py + 2, 32, 32);
      }
    }
  // Original pixel portal, arch, lanterns and player are drawn without external assets.
  const ex = state.exit[0] * TILE,
    ey = state.exit[1] * TILE;
  ctx.fillStyle = "#122e2c";
  ctx.fillRect(ex - 5, ey - 11, 46, 51);
  ctx.fillStyle = "#698c78";
  ctx.fillRect(ex - 3, ey - 13, 6, 49);
  ctx.fillRect(ex + 33, ey - 13, 6, 49);
  ctx.fillRect(ex + 3, ey - 17, 30, 6);
  ctx.fillStyle = "#61dac6";
  ctx.fillRect(ex + 7, ey - 8, 22, 39);
  ctx.fillStyle = "#a2efda";
  ctx.fillRect(ex + 11, ey - 4, 14, 31);
  ctx.fillStyle = "#308e84";
  for (let j = 0; j < 3; j++) {
    const yy = (j * 11 + Math.floor(t * 12)) % 36;
    ctx.fillRect(ex + 10, ey - 7 + yy, 16, 2);
  }
  ctx.fillStyle = "#adf4d4";
  ctx.font = "bold 8px monospace";
  ctx.textAlign = "center";
  ctx.fillText("EXIT", ex + 18, ey - 25);
  for (const [lx, ly] of [
    [1, 3],
    [22, 12],
    [1, 12],
    [22, 3],
  ]) {
    const x = lx * TILE + 18,
      y = ly * TILE + 12;
    ctx.fillStyle = "#171f19";
    ctx.fillRect(x - 6, y + 2, 12, 20);
    ctx.fillStyle = "#7d7150";
    ctx.fillRect(x - 5, y, 10, 5);
    ctx.fillStyle = "#ffbc61";
    ctx.fillRect(x - 3, y - 10, 6, 11);
    ctx.fillStyle = "#ffdf8c";
    ctx.fillRect(x - 1, y - 12 + Math.floor(Math.sin(t * 6) * 2), 3, 9);
  }
  const px = visualPlayer[0] * TILE + 18,
    py = visualPlayer[1] * TILE + 17;
  ctx.fillStyle = "#0b1d16";
  ctx.fillRect(px - 11, py + 11, 23, 7);
  ctx.fillStyle = "#d26239";
  ctx.fillRect(px - 10, py - 2, 7, 18);
  ctx.fillRect(px - 12, py + 6, 5, 10);
  ctx.fillStyle = "#77d8c7";
  ctx.fillRect(px - 6, py - 1, 14, 14);
  ctx.fillStyle = "#c1e7cf";
  ctx.fillRect(px - 5, py - 11, 13, 12);
  ctx.fillStyle = "#e9e4c3";
  ctx.fillRect(px - 3, py - 13, 9, 3);
  ctx.fillStyle = "#21382b";
  ctx.fillRect(px + 1, py - 6, 8, 3);
  ctx.fillStyle = "#d6c7a4";
  ctx.fillRect(px + 10, py + 2, 4, 7);
  ctx.fillStyle = "#b3b89e";
  ctx.fillRect(px + 13, py - 5, 3, 15);
  ctx.fillStyle = "#374c3f";
  ctx.fillRect(px - 6, py + 13, 6, 5);
  ctx.fillRect(px + 3, py + 13, 6, 5);
  ctx.fillStyle = "#c6e5c8";
  ctx.font = "bold 8px monospace";
  ctx.textAlign = "center";
  ctx.fillText("YOU", px, py - 22);
  ctx.strokeStyle = "#81d7bc";
  ctx.lineWidth = 1;
  ctx.strokeRect(px - 16, py - 17, 33, 37);
  ctx.restore();
  const vignette = ctx.createRadialGradient(
    WIDTH / 2,
    HEIGHT / 2,
    HEIGHT * 0.3,
    WIDTH / 2,
    HEIGHT / 2,
    WIDTH * 0.65,
  );
  vignette.addColorStop(0, "#00000000");
  vignette.addColorStop(1, "#080d0b8a");
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  if (damageFlash > 0 && !reduced) {
    ctx.strokeStyle = `rgba(255, 105, 65, ${damageFlash * 0.7})`;
    ctx.lineWidth = 10;
    ctx.strokeRect(5, 5, WIDTH - 10, HEIGHT - 10);
  }
}

export default function Arena({ state }: { state: State }) {
  const canvas = useRef<HTMLCanvasElement>(null),
    current = useRef(state);
  current.current = state;
  useEffect(() => {
    const ctx = canvas.current?.getContext("2d");
    if (!ctx) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    let target = current.current.player,
      from = target,
      movedAt = 0;
    let health = current.current.health,
      damagedAt = -1000;
    const draw = (time: number) => {
      const state = current.current;
      if (target[0] !== state.player[0] || target[1] !== state.player[1]) {
        from = target;
        target = state.player;
        movedAt = time;
      }
      if (state.health < health) damagedAt = time;
      health = state.health;
      const fraction =
        reduced ||
        state.phase !== "running" ||
        Math.abs(target[0] - from[0]) + Math.abs(target[1] - from[1]) > 1
          ? 1
          : Math.min(1, (time - movedAt) / 90);
      const position: [number, number] = [
        from[0] + (target[0] - from[0]) * fraction,
        from[1] + (target[1] - from[1]) * fraction,
      ];
      render(
        ctx,
        state,
        time,
        reduced,
        position,
        Math.max(0, 1 - (time - damagedAt) / 350),
      );
      frame = requestAnimationFrame(draw);
    };
    frame = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(frame);
  }, []);
  return (
    <canvas
      ref={canvas}
      width={WIDTH}
      height={HEIGHT}
      aria-label={`Arena. Player at ${state.player.join(", ")}. Exit at ${state.exit.join(", ")}. Use WASD or arrow keys.`}
      role="img"
      data-testid="arena"
    />
  );
}
