export type Position = {
  id: number;
  type: string;
  price: number;
  amount: number;
  timestamp: string;
};

export type HistoryPosition = Position & { status: string };

export type OrderDto = {
  id: number;
  type: string;
  price: number;
  amount: number;
  created_at: string;
  closed_at: string;
  status: string;
};

export type Account = {
  usdt: number;
  btc: number;
};
