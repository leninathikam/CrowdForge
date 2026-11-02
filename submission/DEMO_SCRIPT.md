# 2:45 authentic demo — updated integrity proof

Record the actual final build, Twitch chat and Codex work. Use genuine viewer inputs; if only the broadcaster is available, call it a broadcaster test. The controlled exit-wall rejection is explicitly a streamer diagnostic. Hide credentials, cookies, callback codes and overlay tokens.

| Time | Actual footage | Narration / proof |
|---|---|---|
| 0:00–0:15 | Moving runner, portal, connected Twitch badge | “I have 100 seconds to escape. Twitch chat can rebuild the arena around me.” |
| 0:15–0:35 | Real chat sends `!lava`; visible count and window closes | “One vote per viewer decides the next change.” Capture a genuine outcome; do not splice synthetic input into this sequence. |
| 0:35–0:55 | Lava appears, runner reroutes; damage cue if real damage occurs | “Chat changes the terrain, but a change must preserve a lava-free route and stay within our detour and time limits.” |
| 0:55–1:20 | Open **Developer diagnostics** (shield icon or **Inspect world integrity**). Expand the actual applied mutation. | “This is this round's evidence: received inputs, committed tiles and the route before and after.” Show Twitch counters and tile diff. Adjacency describes proximity, not predicted damage. |
| 1:20–1:40 | While running, click **Test unsafe exit wall**. Expand rejection, then **Pause for replay proof**. | “This is my deliberate invalid test, not a viewer vote. Rejection leaves the world unchanged.” |
| 1:40–2:00 | Click **Verify deterministic replay**. Show actual digest/command count. | “The server reconstructs the paused round from its seed and recorded inputs, then compares the state and mutation history.” No signed-attestation or full-video-replay claim. |
| 2:00–2:20 | Close diagnostics, resume and show a genuine result; OBS view if captured | “The streamer stays in control. The crowd creates the obstacles and rescue routes.” Do not narrate a win over a loss. |
| 2:20–2:35 | `benchmarks/competition-results.json` and evaluation table | “On the same 1,800 adversarial cases, the original checker kept exits reachable but allowed 600 excessive-detour or time-budget violations. The new rules allowed zero.” Identify this as synthetic safety testing, not viewer capacity. |
| 2:35–2:45 | Actual Codex chat, implementation change and passing tests; end on game | “Codex helped implement, audit and test the engine. CrowdForge: the crowd fights back, and the world has to play fair.” |

Rehearse once. Prioritize clear real Twitch footage, real Codex footage and legible proof over extra cinematic shots. Export the live replay before stopping the server. The safe corridor can be fast: let the genuine vote resolve before ending the demo run, without claiming this staged pacing proves retention.

## Recording checklist

- [ ] Current build/server; reconnect Twitch after restart.
- [ ] Genuine command increments count and closes into an actual mutation.
- [ ] Diagnostics shows real live receipts; synthetic inputs are never called viewers.
- [ ] Exit-wall test is called a streamer diagnostic.
- [ ] Actual paused replay verifies and is exported.
- [ ] Show actual Codex edits/test output; include genuine principal session ID in the form.
- [ ] If using OBS, verify a 1920×1080 Browser source and text readability.
- [ ] No secrets, unlicensed music or third-party material without permission.
- [ ] Final video under three minutes; target 2:45.
- [ ] Upload to **public YouTube**, verify signed-out access, and use that real watch URL.
- [ ] Submit before 2 November 2026, 5 p.m. Eastern.

Do not invent a hosted-app or YouTube URL. Runnable source is the official access route; separate public hosting is recommended but not explicitly mandatory.
