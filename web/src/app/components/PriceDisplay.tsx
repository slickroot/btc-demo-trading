'use client';

import React from 'react';

type PriceDisplayProps = {
  btcPrice: number;
  priceDirection: string;
};

const PriceDisplay = ({ btcPrice, priceDirection }: PriceDisplayProps) => {
  const getPriceClass = () => {
    if (priceDirection === 'up') return 'text-green-500';
    if (priceDirection === 'down') return 'text-red-500';
    return 'text-white';
  };

  return (
    <div className="flex flex-col items-center justify-center my-16">
      <h2 className="text-xl">Bitcoin Price (USDT)</h2>
      <p className={`text-6xl font-bold transition-colors ${getPriceClass()}`}>
        ${btcPrice > 0 ? btcPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : ''}
      </p>
    </div>
  );
};

export default PriceDisplay;
