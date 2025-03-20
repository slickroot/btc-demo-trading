'use client'

import React, { useState, useEffect } from 'react';

type Position = {
  id: number,
  type: string,
  price: number,
  amount: number,
  timestamp: string,
}

const BitcoinTradingApp = () => {
  const [btcPrice, setBtcPrice] = useState(63452.18);
  const [priceDirection, setPriceDirection] = useState('');
  const [account, setAccount] = useState({ usdt: 10000, btc: 0.5 });
  const [openPositions, setOpenPositions] = useState<Position[]>([
    { id: 1, type: 'buy', price: 62100.25, amount: 0.2, timestamp: new Date().toISOString() },
    { id: 2, type: 'sell', price: 63200.50, amount: 0.1, timestamp: new Date().toISOString() }
  ]);
  const [history, setHistory] = useState([
    { id: 1, type: 'buy', price: 61000.75, amount: 0.3, status: 'closed', timestamp: new Date(Date.now() - 86400000).toISOString() },
    { id: 2, type: 'sell', price: 61500.50, amount: 0.3, status: 'closed', timestamp: new Date(Date.now() - 43200000).toISOString() }
  ]);
  const [activeTab, setActiveTab] = useState('positions');

  useEffect(() => {
    const interval = setInterval(() => {
      const change = (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 100);
      const newPrice = parseFloat((btcPrice + change).toFixed(2));
      
      // Set price direction for color change
      setPriceDirection(change > 0 ? 'up' : 'down');
      setBtcPrice(newPrice);
      
      // Reset price direction after 500ms
      setTimeout(() => {
        setPriceDirection('');
      }, 500);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [btcPrice]);

  const handleBuy = () => {
    // Simple implementation - buy 0.01 BTC at current price
    const amount = 0.01;
    const cost = amount * btcPrice;
    
    if (account.usdt >= cost) {
      const newTransaction = {
        id: Date.now(),
        type: 'buy',
        price: btcPrice,
        amount: amount,
        timestamp: new Date().toISOString()
      };
      
      setOpenPositions([newTransaction, ...openPositions]);
      setAccount({
        usdt: parseFloat((account.usdt - cost).toFixed(2)),
        btc: parseFloat((account.btc + amount).toFixed(8))
      });
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
          ${btcPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
