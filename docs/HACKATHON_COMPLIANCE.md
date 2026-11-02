# Hackathon compliance

Initially verified against the linked official pages on October 30, 2026 (America/New_York); official rules and deadline rechecked on November 2. The rules permit access through a runnable repository. A separate public app host is recommended, not explicitly mandatory.

- [Rules](https://twitchcon-codex.devpost.com/rules): entrants must be at least 18 or local age of majority, whichever is older; individuals/teams only. Explicitly listed excluded residences include Brazil, Quebec, Russia, Crimea, Cuba, Iran and North Korea, plus applicable sanctions/prohibited jurisdictions. Sponsor/administrator affiliates and conflict-of-interest relationships are excluded. Entrants must personally confirm eligibility against section 3.
- New work must be created during October 23, 2026 10 a.m. Pacific through November 2, 2026 2 p.m. Pacific. Deadline is **November 2, 5 p.m. EST / 22:00 UTC**. Standard frameworks and tools are allowed; previous project code is not used here.
- Must build an interactive Twitch experience with OpenAI Codex. Twitch connection examples include chat, API, EventSub, extensions and overlays. CrowdForge implements authenticated chat via EventSub WebSockets.
- Four equally weighted criteria: Innovation/Idea, Potential Impact, Technological implementation (including Codex use), Design. Each is 25%.
- Repository must be on GitHub, GitLab or Bitbucket and include all source, assets and installation instructions. Private GitHub/GitLab repositories must be shared with the judging contact shown in the official rules; verify that contact directly before sharing.
- English description and testing instructions, authentic principal Codex session ID, and a publicly visible YouTube demo are required. Keep video below three minutes, showing Twitch functionality and Codex development. Only use music/art/trademarks with permission.
- Original work remains entrant-owned. Open-source dependencies are permitted subject to their licenses. Our game artwork is procedural, authored in this repository; no external game assets or music are included.
- Working project must be freely accessible to judges until judging ends. **Schedule discrepancy:** [dates page](https://twitchcon-codex.devpost.com/details/dates) lists Nov 3–6; rules list Nov 5–15. Rules section 11 says rules prevail. Keep access through **Nov 15, 5 p.m. Pacific** and request organizer clarification if necessary.

## Repository provenance

Initial audit: the supplied CrowdForge directory contained only an initialized `.git`, no commits, no remote, and no source. All application files in this repository were created in this build session. No previous hackathon code was copied. Check Git commit timestamps and `docs/CODEX_EVIDENCE.md`.

## Submission checklist

- [x] Empty repository origin audited
- [x] Principal session ID retrieved from supported environment metadata
- [x] Original procedural artwork and Codex-built source
- [ ] Entrant confirms age, residence, team representation and exclusions
- [x] Real Twitch account authorizes the registered application
- [ ] Record real chat affecting the game; simulation does not satisfy this
- [x] Publish repository and verify source access (leninathikam/CrowdForge)
- [ ] Recommended: verify public deployment with HTTPS and persistent backend; runnable repository is the permitted alternative
- [ ] Upload public YouTube video below three minutes
- [ ] Submit description, repository, video and session ID before deadline

## Twitch implementation references

[Developer overview](https://dev.twitch.tv/docs/), [EventSub](https://dev.twitch.tv/docs/eventsub/), [Chat](https://dev.twitch.tv/docs/chat/), [WebSocket lifecycle](https://dev.twitch.tv/docs/eventsub/handling-websocket-events/), [chat subscription](https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channelchatmessage), [OAuth authorization code](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#authorization-code-grant-flow), [hourly token validation](https://dev.twitch.tv/docs/authentication/validate-tokens/).

WebSocket user-token integration requests only `user:read:chat`, with the authorizing broadcaster also the reading user. OAuth state is single-use and browser-bound. Tokens remain server-side in memory. TLS authenticates outbound Twitch sockets; WebSocket events do not use webhook HMAC signatures. Handle welcome, keepalive, notification, reconnect and revocation; resubscribe after unexpected loss. Twitch does not replay missed events.
