'use client';

type TradeButtonsProps = {
  onBuy: () => void;
  onSell: () => void;
};

const TradeButtons = ({ onBuy, onSell }: TradeButtonsProps) => {
  return (
    <div className="absolute top-6 left-6">
      <button onClick={onBuy} className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded mr-2">
        BUY
      </button>
      <button onClick={onSell} className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded">
        SELL
      </button>
    </div>
  );
};

export default TradeButtons;

