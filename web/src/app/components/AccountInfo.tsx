'use client';

import React from 'react';
import { Account } from '../../types';

type AccountInfoProps = {
  account: Account;
  btcPrice: number;
};

const AccountInfo = ({ account, btcPrice }: AccountInfoProps) => {
  return (
    <div className="absolute top-6 right-6 bg-gray-800 p-4 rounded shadow">
      <h3 className="text-lg font-medium mb-2">Account Balance</h3>
      <p>USDT: ${account.usdt.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
      <p>BTC: {account.btc.toFixed(8)}</p>
      <p className="text-sm text-gray-400">≈ ${(account.btc * btcPrice).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
    </div>
  );
};

export default AccountInfo;

