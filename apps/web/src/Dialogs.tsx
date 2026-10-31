import {
  ArrowUpRight,
  Check,
  Copy,
  Gamepad2,
  Hammer,
  ShieldCheck,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";
import type { State, Session, GameAction } from "./types";
export type ModalKind = "help" | "settings" | "setup" | "overlay";
interface Props {
  modal: ModalKind;
  state: State;
  session: Session | null;
  action: GameAction;
  create: (seed?: number, changes?: boolean) => Promise<void>;
  sound: boolean;
  setSound: (sound: boolean) => void;
  setError: (message: string) => void;
  onClose: () => void;
}
export default function Dialogs({
  modal,
  state,
  session,
  action,
  create,
  sound,
  setSound,
  setError,
  onClose,
}: Props) {
  const [copied, setCopied] = useState(false);
  const [seed, setSeed] = useState(String(state.seed));
  const [changes, setChanges] = useState(state.vote.allow_changes);
  const overlayUrl = session
    ? `${location.origin}/overlay?session=${session.id}&token=${session.overlay_token}`
    : "";
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(overlayUrl);
      setCopied(true);
    } catch {
      setError("Clipboard unavailable. Select and copy the overlay URL below.");
    }
  };

  return (
    <div
      className="modal-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={modal + " dialog"}
      >
        <button
          className="modal-close"
          autoFocus
          onClick={() => onClose()}
          aria-label="Close dialog"
        >
          <X size={20} />
        </button>
        {modal === "help" && (
          <>
            <div className="eyebrow">RUNNER'S FIELD GUIDE</div>
            <h2>Welcome to the forge.</h2>
            <p>
              Reach the cyan exit before the 100-second timer ends. Lava deals
              22 damage per second. Stone walls block movement. Wooden bridges
              are safe.
            </p>
            <div className="help-row">
              <Gamepad2 />
              <div>
                <h3>You do the running.</h3>
                <p>
                  WASD or arrow keys to move. Space pauses the game and voting.
                  Emergency rescue restores 25 health and clears your tile; it's
                  recorded in the timeline.
                </p>
              </div>
            </div>
            <div className="help-row">
              <Users />
              <div>
                <h3>Chat does the forging.</h3>
                <p>
                  Viewers type !lava, !wall, !bridge, or !vote 1–3. Each window
                  lasts 15 seconds. One vote per viewer; changes have a
                  one-second cooldown. Ties rotate by window number. Empty
                  windows leave the world unchanged.
                </p>
              </div>
            </div>
            <div className="help-row">
              <ShieldCheck />
              <div>
                <h3>The world plays fair.</h3>
                <p>
                  The server rejects changes that block the last safe escape
                  route. Lava cannot appear on or next to you. All rejected
                  changes leave the map unchanged.
                </p>
              </div>
            </div>
            <button
              className="secondary"
              disabled={state.phase !== "running"}
              onClick={() => {
                void action("integrity_probe");
                onClose();
              }}
            >
              <ShieldCheck size={16} /> Run integrity diagnostic
            </button>
            <p className="fine-print">
              The diagnostic submits a wall on the protected exit and shows a
              real rejection. It is labeled as a streamer test, never an
              audience vote.
            </p>
            <p className="fine-print">
              !help is documented here; the read-only Twitch connection does not
              send chat replies. Simulation votes are synthetic and never
              presented as real chat.
            </p>
          </>
        )}
        {modal === "settings" && (
          <>
            <div className="eyebrow">MAKE IT YOUR ARENA</div>
            <h2>Forge settings.</h2>
            <label>
              World seed
              <input
                type="number"
                min="0"
                max="2147483647"
                value={seed}
                onChange={(event) => setSeed(event.target.value)}
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={changes}
                onChange={(event) => setChanges(event.target.checked)}
              />{" "}
              Allow viewers to change their vote
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={sound}
                onChange={(event) => setSound(event.target.checked)}
              />{" "}
              Mutation sound effects
            </label>
            <p className="fine-print">
              A new arena gets a new overlay URL. The current round continues
              until you switch. Animations respect your system's reduced-motion
              preference.
            </p>
            <button
              className="primary"
              onClick={async () => {
                const value = Number(seed);
                if (
                  !Number.isInteger(value) ||
                  value < 0 ||
                  value > 2147483647
                ) {
                  setError("Use an integer seed from 0 to 2147483647.");
                  return;
                }
                try {
                  await create(value, changes);
                  onClose();
                } catch (failure) {
                  setError((failure as Error).message);
                }
              }}
            >
              <Hammer size={16} /> Create new arena
            </button>
          </>
        )}
        {modal === "setup" && (
          <>
            <div className="eyebrow">BRING YOUR COMMUNITY</div>
            <h2>Connect your Twitch.</h2>
            <p>
              Register an application in the Twitch Developer Console. Configure
              these values on your server and restart it. Keep the client secret
              server-side.
            </p>
            <pre>
              TWITCH_CLIENT_ID
              <br />
              TWITCH_CLIENT_SECRET
              <br />
              TWITCH_REDIRECT_URI
            </pre>
            <p>Local redirect URL:</p>
            <input
              readOnly
              value={state.twitch_redirect_uri}
              aria-label="Twitch redirect URL"
            />
            <p className="fine-print">
              Authorize the broadcaster account. CrowdForge requests only
              user:read:chat, then subscribes to your channel's chat through
              EventSub WebSockets. Full setup is in README.md.
            </p>
            <a
              className="primary"
              href="https://dev.twitch.tv/console/apps"
              target="_blank"
              rel="noreferrer"
            >
              Open Twitch Developer Console <ArrowUpRight size={16} />
            </a>
          </>
        )}
        {modal === "overlay" && (
          <>
            <div className="eyebrow">READY FOR YOUR STREAM</div>
            <h2>The world, on screen.</h2>
            <p>
              Add a Browser source in OBS. Use 1920 × 1080, paste this URL, and
              keep your streamer tab open for movement and controls.
            </p>
            <label>
              Read-only overlay URL
              <input
                readOnly
                value={overlayUrl}
                onFocus={(event) => event.target.select()}
              />
            </label>
            <div className="modal-actions">
              <button className="primary" onClick={() => void copy()}>
                {copied ? <Check size={16} /> : <Copy size={16} />}{" "}
                {copied ? "Copied" : "Copy overlay URL"}
              </button>
              <a
                className="secondary"
                href={overlayUrl}
                target="_blank"
                rel="noreferrer"
              >
                Preview overlay <ArrowUpRight size={15} />
              </a>
            </div>
            <p className="fine-print">
              This URL can view your round but cannot control it. Treat it as a
              private viewing link. Reset keeps the URL; a new arena creates a
              new URL.
            </p>
          </>
        )}
      </section>
    </div>
  );
}
