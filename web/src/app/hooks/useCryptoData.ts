'use client';

import { useState, useEffect } from 'react';
import { Position, HistoryPosition, OrderDto, Account } from '../../types';

export const useCryptoData = () => {
  const [btcPrice, setBtcPrice] = useState(0);
  const [priceDirection, setPriceDirection] = useState('');
  const [account, setAccount] = useState<Account>({ usdt: 0, btc: 0 });
  const [openPositions, setOpenPositions] = useState<Position[]>([]);
  const [history, setHistory] = useState<HistoryPosition[]>([]);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetch("http://localhost:8000/orders");
        if (!response.ok) {
          throw new Error("Failed to fetch orders");
        }
        
        const data = await response.json();
        
        const openPositions = data
          .filter((order: OrderDto) => order.status === "open")
          .map((order: OrderDto) => ({
            id: order.id,
            type: order.type,
            price: order.price,
            amount: order.amount,
            timestamp: order.created_at,
          }));

        const closedPositions = data
          .filter((order: OrderDto) => order.status === "closed")
          .map((order: OrderDto) => ({
            id: order.id,
            type: order.type,
            price: order.price,
            amount: order.amount,
            timestamp: order.closed_at,
            status: "closed",
          }));

        setOpenPositions(openPositions);
        setHistory(closedPositions);
      } catch (error) {
        console.error("Error fetching orders:", error);
      }
    };

    fetchOrders();
  }, []);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await fetch('http://localhost:8000/price');
        const data = await response.json();
        const newPrice = parseFloat(parseFloat(data.price).toFixed(2));

        // Determine the price change direction
        const change = newPrice - btcPrice;
        setPriceDirection(change > 0 ? 'up' : (change < 0 ? 'down' : ''));
        setBtcPrice(newPrice);

        // Reset price direction after 500ms for the color change effect
        setTimeout(() => {
          setPriceDirection('');
        }, 500);
      } catch (error) {
        console.error('Error fetching price:', error);
      }
    };

    const fetchAccount = async () => {
      try {
        const response = await fetch('http://localhost:8000/account');
        const data = await response.json();

        setAccount({
          usdt: parseFloat(parseFloat(data["cash_balance"]).toFixed(2)),
          btc: parseFloat(parseFloat(data["btc_balance"]).toFixed(8)),
        });
      } catch (error) {
        console.error('Error fetching account:', error);
      }
    };

    fetchAccount();
    fetchPrice();

    // Set interval to fetch the price every 5 seconds
    const interval = setInterval(fetchPrice, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleBuy = async () => {
    const amount = 0.01;

    try {
      const response = await fetch("http://localhost:8000/trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "buy", amount }),
      });

      if (!response.ok) {
        throw new Error("Trade failed");
      }

      const data = await response.json();

      setOpenPositions([{ type: "buy", amount, id: data.order_id, price: data.price, timestamp: data.timestamp }, ...openPositions]);
      setAccount({
        usdt: parseFloat(parseFloat(data["account"]["cash_balance"]).toFixed(2)),
        btc: parseFloat(parseFloat(data["account"]["btc_balance"]).toFixed(8)),
      });
    } catch (error) {
      console.error("Buy failed:", error);
    }
  };

  const handleSell = async () => {
    const amount = 0.01;

    try {
      const response = await fetch("http://localhost:8000/trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "sell", amount }),
      });

      if (!response.ok) {
        throw new Error("Trade failed");
      }

      const data = await response.json();

      setOpenPositions([{ type: "sell", amount, id: data.order_id, price: data.price, timestamp: data.timestamp }, ...openPositions]);
      setAccount({
        usdt: parseFloat(parseFloat(data["account"]["cash_balance"]).toFixed(2)),
        btc: parseFloat(parseFloat(data["account"]["btc_balance"]).toFixed(8)),
      });
    } catch (error) {
      console.error("Sell failed:", error);
    }
  };

  const closePosition = async (position: Position) => {
    try {
      const response = await fetch("http://localhost:8000/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: position.id }),
      });

      if (!response.ok) {
        throw new Error("Failed to close position");
      }
      
      const data = await response.json();

      // Remove the closed position from openPositions
      const updatedPositions = openPositions.filter((p) => p.id !== position.id);
      setOpenPositions(updatedPositions);
      
      setAccount({
        usdt: parseFloat(parseFloat(data["account"]["cash_balance"]).toFixed(2)),
        btc: parseFloat(parseFloat(data["account"]["btc_balance"]).toFixed(8)),
      });

      // Add the closed position to history; update timestamp if needed
      const closedPosition = { ...position, status: "closed", timestamp: data.timestamp };
      setHistory([closedPosition, ...history]);
    } catch (error) {
      console.error("Error closing position:", error);
    }
  };

  return {
    btcPrice,
    priceDirection,
    account,
    openPositions,
    history,
    handleBuy,
    handleSell,
    closePosition,
  };
};
