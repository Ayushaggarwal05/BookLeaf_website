import React from 'react';
import { formatINR } from '../../utils/formatters';

interface CurrencyFormatterProps {
  amount: number | null | undefined;
  className?: string;
  showDecimals?: boolean;
}

export const CurrencyFormatter: React.FC<CurrencyFormatterProps> = ({
  amount,
  className = '',
  showDecimals = true,
}) => {
  return <span className={`font-mono ${className}`}>{formatINR(amount, showDecimals)}</span>;
};
