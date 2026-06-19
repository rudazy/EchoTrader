export interface DashboardStatus {
  timestamp: string;
  agent_online: boolean;
  dry_run: boolean;
  chain: string;
  regime_label: string;
  regime: string;
  perception: PerceptionSnapshot | null;
  reasoner: ReasonerSnapshot | null;
  decision: DecisionSnapshot | null;
  risk: RiskSnapshot | null;
  signals: {
    fear_greed: number | null;
    fear_greed_label: string | null;
    divergence_score: string | null;
    btc_dominance: number | null;
    social_heat: number | null;
    onchain_flow: string | null;
  };
  perception_history: PerceptionHistoryEntry[];
  recent_trades: TradeRecord[];
  recent_echoes: EchoRecord[];
  portfolio: {
    allocated_capital_usd: number;
    deployed_pct: number;
    token: string;
    network: string;
  };
}

export interface PerceptionHistoryEntry {
  timestamp: string;
  fear_greed_index: number | null;
  divergence_score?: string;
  reasoning_hash?: string | null;
}

export interface PerceptionSnapshot {
  fear_greed_index: number | null;
  divergence_score: string;
  reasoning_hash: string | null;
  btc_dominance: number | null;
  on_chain_netflow: string | null;
  raw?: {
    global_metrics?: {
      total_market_cap?: number;
    };
  };
}

export interface ReasonerSnapshot {
  market_read: string;
  risk_notes: string;
  confidence_pct: number;
  reasoning?: string;
  reasoning_hash: string | null;
}

export interface DecisionSnapshot {
  action: string;
  token?: string | null;
  confidence?: number;
  size_pct?: number;
  thesis?: string;
}

export interface RiskSnapshot {
  approved: boolean;
  regime: string;
  adjusted_size_pct: number;
  reasons: string[];
}

export interface TradeRecord {
  timestamp: string;
  action: string;
  token: string;
  status: string;
  dry_run: boolean;
  quote_summary?: string;
  tx_hash?: string;
  reasoning_hash?: string;
}

export interface EchoRecord {
  id: string;
  timestamp: string;
  thesis: string;
  action: string;
  confidence: number;
  snapshot_summary: string;
}