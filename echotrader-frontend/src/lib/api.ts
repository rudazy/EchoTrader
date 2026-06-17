import type { DashboardStatus } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchStatus(refresh = false): Promise<DashboardStatus> {
  const url = `${API_URL}/api/status${refresh ? "?refresh=true" : ""}`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}