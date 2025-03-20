'use client'

import React, { useState, useEffect } from 'react';

type Position = {
  id: number,
  type: string,
  price: number,
  amount: number,
  timestamp: string,
}

type OrderDto = {
  id: number,
  type: string,
  price: number,
  amount: number,
  created_at: string,
  closed_at: string,
  status: string,
}

const BitcoinTradingApp = () => {
  const [btcPrice, setBtcPrice] = useState(0);
  const [priceDirection, setPriceDirection] = useState('');
  const [account, setAccount] = useState({ usdt: 10000, btc: 0.5 });
  const [openPositions, setOpenPositions] = useState<Position[]>([]);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('positions');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetch("http://localhost:8000/orders");
          if (!response.ok) {
          throw new Error("Failed to fetch orders");
        }
        const data = await response.json();
        // Map orders to your Position type:
        // For open orders, use created_at as the timestamp.
        // For closed orders, use closed_at as the timestamp.
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
          }));

    setOpenPositions(openPositions);
    setHistory(closedPositions);
      } catch (error) {
        console.error("Error fetching orders:", error);
      }
    };

    // Fetch immediately on component mount
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
        console.error('Error fetching price:', error);
      }
    };

    fetchAccount();
    fetchPrice();

    // Set interval to fetch the price every 10 seconds
    const interval = setInterval(fetchPrice, 10000);
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

  const handleSell = () => {
    // Simple implementation - sell 0.01 BTC at current price
    const amount = 0.01;
    const revenue = amount * btcPrice;
    
    if (account.btc >= amount) {
      const newTransaction = {
        id: Date.now(),
        type: 'sell',
        price: btcPrice,
        amount: amount,
        timestamp: new Date().toISOString()
      };
      
      setOpenPositions([newTransaction, ...openPositions]);
      setAccount({
        usdt: parseFloat((account.usdt + revenue).toFixed(2)),
        btc: parseFloat((account.btc - amount).toFixed(8))
      });
    }
  };
  
  const closePosition = (position: Position) => {
    // Close a position (either buy back or sell)
    const updatedPositions = openPositions.filter(p => p.id !== position.id);
    const closedPosition = {...position, status: 'closed'};
    
    setOpenPositions(updatedPositions);
    setHistory([closedPosition, ...history]);
    
    // Update account based on position type
    if (position.type === 'buy') {
      // Selling a buy position
      const revenue = position.amount * btcPrice;
      setAccount({
        usdt: parseFloat((account.usdt + revenue).toFixed(2)),
        btc: parseFloat((account.btc - position.amount).toFixed(8))
      });
    } else {
      // Buying back a sell position
      const cost = position.amount * btcPrice;
      setAccount({
        usdt: parseFloat((account.usdt - cost).toFixed(2)),
        btc: parseFloat((account.btc + position.amount).toFixed(8))
      });
    }
  };

  const getPriceClass = () => {
    if (priceDirection === 'up') return 'text-green-500';
    if (priceDirection === 'down') return 'text-red-500';
    return 'text-white';
  };

  return (
    <div className="bg-gray-900 text-gray-200 min-h-screen p-6">
      {/* Price Display */}
      <div className="flex flex-col items-center justify-center my-16">
        <h2 className="text-xl">Bitcoin Price (USDT)</h2>
        <p className={`text-6xl font-bold transition-colors ${getPriceClass()}`}>
          ${btcPrice > 0 ? btcPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ''}
        </p>
      </div>
      
      {/* Account Info */}
      <div className="absolute top-6 right-6 bg-gray-800 p-4 rounded shadow">
        <h3 className="text-lg font-medium mb-2">Account Balance</h3>
        <p>USDT: ${account.usdt.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        <p>BTC: {account.btc.toFixed(8)}</p>
        <p className="text-sm text-gray-400">≈ ${(account.btc * btcPrice).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
      </div>
      
      {/* Buy/Sell Buttons */}
      <div className="absolute top-6 left-6">
        <button onClick={handleBuy} className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded mr-2">
          BUY
        </button>
        <button onClick={handleSell} className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded">
          SELL
        </button>
      </div>
      
      {/* Tabbed Interface */}
      <div className="mt-8 bg-gray-800 rounded shadow">
        {/* Tab Navigation */}
        <div className="flex border-b border-gray-700">
          <button
            className={`px-6 py-3 text-sm font-medium ${activeTab === 'positions' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
            onClick={() => setActiveTab('positions')}
          >
            Open Positions
          </button>
          <button
            className={`px-6 py-3 text-sm font-medium ${activeTab === 'history' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-700'}`}
            onClick={() => setActiveTab('history')}
          >
            Transaction History
          </button>
        </div>
        
        {/* Tab Content */}
        <div className="p-4">
          {activeTab === 'positions' && (
            <div>
              <h3 className="text-lg font-medium mb-3">Open Positions</h3>
              <div className="overflow-y-auto max-h-64">
                <table className="w-full">
                  <thead>
                    <tr className="text-gray-400 text-xs border-b border-gray-700">
                      <th className="text-left py-2">Type</th>
                      <th className="text-right py-2">Price</th>
                      <th className="text-right py-2">Amount</th>
                      <th className="text-right py-2">Value (USDT)</th>
                      <th className="text-right py-2">Timestamp</th>
                      <th className="text-right py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {openPositions.length > 0 ? (
                      openPositions.map(position => (
                        <tr key={position.id} className="border-b border-gray-700">
                          <td className={`py-2 ${position.type === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                            {position.type.toUpperCase()}
                          </td>
                          <td className="text-right py-2">${position.price.toLocaleString()}</td>
                          <td className="text-right py-2">{position.amount}</td>
                          <td className="text-right py-2">${(position.amount * position.price).toLocaleString()}</td>
                          <td className="text-right py-2">{new Date(position.timestamp).toLocaleTimeString()}</td>
                          <td className="text-right py-2">
                            <button 
                              onClick={() => closePosition(position)}
                              className={`px-2 py-1 rounded text-xs ${position.type === 'buy' ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}
                            >
                              {position.type === 'buy' ? 'SELL' : 'BUY'}
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-4 text-center text-gray-400">No open positions</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
          
          {activeTab === 'history' && (
            <div>
              <h3 className="text-lg font-medium mb-3">Transaction History</h3>
              <div className="overflow-y-auto max-h-64">
                <table className="w-full">
                  <thead>
                    <tr className="text-gray-400 text-xs border-b border-gray-700">
                      <th className="text-left py-2">Type</th>
                      <th className="text-right py-2">Price</th>
                      <th className="text-right py-2">Amount</th>
                      <th className="text-right py-2">Value (USDT)</th>
                      <th className="text-right py-2">Status</th>
                      <th className="text-right py-2">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.length > 0 ? (
                      history.map(tx => (
                        <tr key={tx.id} className="border-b border-gray-700">
                          <td className={`py-2 ${tx.type === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                            {tx.type.toUpperCase()}
                          </td>
                          <td className="text-right py-2">${tx.price.toLocaleString()}</td>
                          <td className="text-right py-2">{tx.amount}</td>
                          <td className="text-right py-2">${(tx.amount * tx.price).toLocaleString()}</td>
                          <td className="text-right py-2">{tx.status}</td>
                          <td className="text-right py-2">{new Date(tx.timestamp).toLocaleString()}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-4 text-center text-gray-400">No transaction history</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BitcoinTradingApp;
