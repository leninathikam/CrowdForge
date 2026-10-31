import { useCallback, useEffect, useRef, useState } from "react";
import type { Session, State } from "./types";
import { decodeSnapshot } from "./wire";

export const overlay = location.pathname === "/overlay";
const params = new URLSearchParams(location.search);
const storageKey = "crowdforge.session.v1";

async function request(url: string, options: RequestInit = {}) {
  const response = await fetch(url, { credentials: "same-origin", ...options });
  const result = await response.json();
  if (!response.ok)
    throw new Error(
      result.detail || "The server could not complete that action.",
    );
  return result;
}

export function useGame() {
  const [session, setSession] = useState<Session | null>(null);
  const [state, setState] = useState<State | null>(null);
  const [connection, setConnection] = useState("connecting");
  const [error, setError] = useState("");
  const socket = useRef<WebSocket | null>(null);
  const busy = useRef(false);
  const pendingMove = useRef<Record<string, unknown> | null>(null);

  const create = useCallback(async (seed = 1847, allow_changes = true) => {
    const data = await request("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed, allow_changes }),
    });
    const next = { id: data.id, overlay_token: data.overlay_token };
    localStorage.setItem(storageKey, JSON.stringify(next));
    setSession(next);
    setState(decodeSnapshot(data.state));
    setError("");
    history.replaceState({}, "", "/?session=" + next.id);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        if (overlay) {
          const id = params.get("session"),
            token = params.get("token");
          if (!id || !token)
            throw new Error(
              "Open the overlay URL from your streamer controls.",
            );
          const data = await request(
            `/api/sessions/${id}?token=${encodeURIComponent(token)}`,
          );
          if (!cancelled) {
            setSession({ id, overlay_token: token });
            setState(decodeSnapshot(data));
          }
          return;
        }
        const raw = localStorage.getItem(storageKey);
        let previous: Session | null = null;
        try {
          previous = raw ? JSON.parse(raw) : null;
        } catch {
          localStorage.removeItem(storageKey);
        }
        if (
          previous?.id &&
          (!params.get("session") || params.get("session") === previous.id)
        ) {
          try {
            const data = await request("/api/sessions/" + previous.id);
            if (!cancelled) {
              setSession(previous);
              setState(decodeSnapshot(data));
            }
            return;
          } catch {
            localStorage.removeItem(storageKey);
          }
        }
        if (!cancelled) await create();
      } catch (failure) {
        if (!cancelled) setError(String((failure as Error).message));
      }
    }
    void boot();
    return () => {
      cancelled = true;
    };
  }, [create]);

  useEffect(() => {
    if (!session) return;
    let stopped = false,
      retry = 0,
      timer: ReturnType<typeof setTimeout>;
    function connect() {
      if (stopped) return;
      const scheme = location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(
        `${scheme}//${location.host}/api/sessions/${session!.id}/ws${overlay ? "?token=" + encodeURIComponent(session!.overlay_token) : ""}`,
      );
      socket.current = ws;
      ws.onopen = () => {
        retry = 0;
        setConnection("connected");
        setError("");
      };
      ws.onmessage = (message) => {
        try {
          const next = decodeSnapshot(JSON.parse(message.data));
          setState(next);
        } catch {
          setError("Could not read server state. Reload to synchronize.");
        }
      };
      ws.onclose = (event) => {
        if (stopped) return;
        setConnection("reconnecting");
        if (event.code === 1008) {
          setError(
            "This session expired or access was denied. Reload to create an arena.",
          );
          return;
        }
        timer = setTimeout(connect, Math.min(5000, 500 * 2 ** retry++));
      };
      ws.onerror = () => ws.close();
    }
    connect();
    return () => {
      stopped = true;
      clearTimeout(timer);
      socket.current?.close();
    };
  }, [session]);

  const action = useCallback(
    async function sendAction(
      action: string,
      extra: Record<string, unknown> = {},
    ) {
      if (!session || overlay) return;
      if (busy.current) {
        if (action === "move") pendingMove.current = extra;
        return;
      }
      busy.current = true;
      try {
        const data = await request(`/api/sessions/${session.id}/action`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action, ...extra }),
        });
        setState(decodeSnapshot(data));
      } catch (failure) {
        setError((failure as Error).message);
      } finally {
        busy.current = false;
        const queued = pendingMove.current;
        pendingMove.current = null;
        if (queued) void sendAction("move", queued);
      }
    },
    [session],
  );

  const replay = async () => {
    if (!session) return;
    try {
      const record = await request(`/api/sessions/${session.id}/replay`);
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(record, null, 2)], {
          type: "application/json",
        }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = `crowdforge-${state?.seed}-replay.json`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (failure) {
      setError((failure as Error).message);
    }
  };

  return {
    session,
    state,
    connection,
    error,
    setError,
    create,
    action,
    replay,
  };
}
