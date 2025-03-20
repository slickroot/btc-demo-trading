'use client';

import React from 'react';
import { Position } from '../../types';

type PositionsTableProps = {
  positions: Position[];
  onClosePosition: (position: Position) => void;
};

const PositionsTable = ({ positions, onClosePosition }: PositionsTableProps) => {
  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Open Positions</h3>
      <div className="overflow-auto" style={{ height: '250px', scrollbarWidth: 'thin', scrollbarColor: '#4B5563 #1F2937' }}>
        <table className="w-full">
          <thead className="sticky top-0 bg-gray-800">
            <tr className="text-gray-400 text-xs border-b border-gray-700">
              <th className="text-left py-2 px-4">Type</th>
              <th className="text-right py-2 px-4">Price</th>
              <th className="text-right py-2 px-4">Amount</th>
              <th className="text-right py-2 px-4">Value (USDT)</th>
              <th className="text-right py-2 px-4">Timestamp</th>
              <th className="text-right py-2 px-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {positions.length > 0 ? (
              positions.map(position => (
                <tr key={position.id} className="border-b border-gray-700 hover:bg-gray-700">
                  <td className={`py-2 px-4 ${position.type === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                    {position.type.toUpperCase()}
                  </td>
                  <td className="text-right py-2 px-4">${position.price.toLocaleString()}</td>
                  <td className="text-right py-2 px-4">{position.amount}</td>
                  <td className="text-right py-2 px-4">${(position.amount * position.price).toLocaleString()}</td>
                  <td className="text-right py-2 px-4">{new Date(position.timestamp).toLocaleTimeString()}</td>
                  <td className="text-right py-2 px-4">
                    <button 
                      onClick={() => onClosePosition(position)}
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
  );
};

export default PositionsTable;

