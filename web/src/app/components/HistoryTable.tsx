'use client';

import React from 'react';
import { HistoryPosition } from '../../types';

type HistoryTableProps = {
  history: HistoryPosition[];
};

const HistoryTable = ({ history }: HistoryTableProps) => {
  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Transaction History</h3>
      <div className="overflow-auto" style={{ maxHeight: '250px', scrollbarWidth: 'thin', scrollbarColor: '#4B5563 #1F2937' }}>
        <table className="w-full">
          <thead className="sticky top-0 bg-gray-800">
            <tr className="text-gray-400 text-xs border-b border-gray-700">
              <th className="text-left py-2 px-4">Type</th>
              <th className="text-right py-2 px-4">Price</th>
              <th className="text-right py-2 px-4">Amount</th>
              <th className="text-right py-2 px-4">Value (USDT)</th>
              <th className="text-right py-2 px-4">Status</th>
              <th className="text-right py-2 px-4">Date</th>
            </tr>
          </thead>
          <tbody>
            {history.length > 0 ? (
              history.map(tx => (
                <tr key={tx.id} className="border-b border-gray-700 hover:bg-gray-700">
                  <td className={`py-2 px-4 ${tx.type === 'buy' ? 'text-green-500' : 'text-red-500'}`}>
                    {tx.type.toUpperCase()}
                  </td>
                  <td className="text-right py-2 px-4">${tx.price.toLocaleString()}</td>
                  <td className="text-right py-2 px-4">{tx.amount}</td>
                  <td className="text-right py-2 px-4">${(tx.amount * tx.price).toLocaleString()}</td>
                  <td className="text-right py-2 px-4">{tx.status}</td>
                  <td className="text-right py-2 px-4">{new Date(tx.timestamp).toLocaleString()}</td>
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
  );
};

export default HistoryTable;

