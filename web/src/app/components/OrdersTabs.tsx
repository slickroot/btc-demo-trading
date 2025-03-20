'use client';

import React from 'react';
import PositionsTable from './PositionsTable';
import HistoryTable from './HistoryTable';
import { Position, HistoryPosition } from '../../types';

type OrderTabsProps = {
  openPositions: Position[];
  history: HistoryPosition[];
  onClosePosition: (position: Position) => void;
};

const OrderTabs = ({ openPositions, history, onClosePosition }: OrderTabsProps) => {
  const [activeTab, setActiveTab] = React.useState('positions');

  return (
    <div className="w-full border-t border-gray-700 bg-gray-800">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-700 px-6">
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
      <div className="p-6">
        {activeTab === 'positions' && <PositionsTable positions={openPositions} onClosePosition={onClosePosition} />}
        {activeTab === 'history' && <HistoryTable history={history} />}
      </div>
    </div>
  );
};

export default OrderTabs;
