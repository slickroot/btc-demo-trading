'use client';

import React from 'react';
import PriceDisplay from './components/PriceDisplay';
import AccountInfo from './components/AccountInfo';
import TradeButtons from './components/TradeButtons';
import OrdersTabs from './components/OrdersTabs';
import { useCryptoData } from './hooks/useCryptoData';

const BitcoinTradingApp = () => {
  const {
    btcPrice,
    priceDirection,
    account,
    openPositions,
    history,
    handleBuy,
    handleSell,
    closePosition,
  } = useCryptoData();

  return (
    <div className="bg-gray-900 text-gray-200 min-h-screen p-6 flex flex-col justify-between">
      <PriceDisplay btcPrice={btcPrice} priceDirection={priceDirection} />
      <AccountInfo account={account} btcPrice={btcPrice} />
      <TradeButtons onBuy={handleBuy} onSell={handleSell} />
      <OrdersTabs 
        openPositions={openPositions} 
        history={history} 
        onClosePosition={closePosition} 
      />
    </div>
  );
};

export default BitcoinTradingApp;
