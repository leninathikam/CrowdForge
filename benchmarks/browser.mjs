import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";

const base = process.argv[2] || "http://127.0.0.1:8000";
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(base);
  await page.getByRole("button", { name: "Enter the arena", exact: true }).click();
  await page.getByRole("button", { name: "Enter the arena", exact: true }).waitFor({ state: "hidden" });
  const measurement = await page.evaluate(async () => {
    const times = [];
    await new Promise((resolve) => {
      function frame(time) {
        times.push(time);
        if (times.length === 121) resolve();
        else requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    });
    const intervals = times.slice(1).map((time, i) => time - times[i]).sort((a, b) => a - b);
    return {
      frames: intervals.length,
      duration_ms: Number((times.at(-1) - times[0]).toFixed(2)),
      effective_frames_per_second: Number((intervals.length * 1000 / (times.at(-1) - times[0])).toFixed(2)),
      frame_interval_ms_median: Number(intervals[Math.floor(intervals.length / 2)].toFixed(2)),
      frame_interval_ms_p95: Number(intervals[Math.floor(intervals.length * .95)].toFixed(2)),
      visibility: document.visibilityState,
    };
  });
  const result = { ...measurement, viewport: "1920x1080", browser: "Playwright headless Chromium", limits: "120 requestAnimationFrame intervals while rendering an offline round on one workstation. Not a GPU frame profiler, OBS test, live Twitch load test or long-duration soak." };
  await mkdir("artifacts", { recursive: true });
  await writeFile("artifacts/browser-performance.json", JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify(result, null, 2));
} finally {
  await browser.close();
}
