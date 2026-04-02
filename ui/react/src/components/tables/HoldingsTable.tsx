import React from 'react';
import { DataTable, Column } from './DataTable';

export interface Holding {
  symbol: string;
  name: string;
  asset_class: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  unrealised_pnl: number;
  weight_pct: number;
}

interface HoldingsTableProps {
  holdings: Holding[];
  loading?: boolean;
}

const formatINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const pnlStyle = (v: number): string =>
  v >= 0 ? 'text-green-700 font-semibold' : 'text-red-600 font-semibold';

const columns: Column<Holding>[] = [
  { key: 'symbol',         header: 'Symbol',       className: 'font-mono text-xs font-bold' },
  { key: 'name',           header: 'Name' },
  { key: 'asset_class',    header: 'Class' },
  { key: 'quantity',       header: 'Qty',           className: 'text-right' },
  {
    key: 'avg_cost',
    header: 'Avg Cost',
    render: (v) => formatINR(Number(v)),
    className: 'text-right',
  },
  {
    key: 'current_price',
    header: 'LTP',
    render: (v) => formatINR(Number(v)),
    className: 'text-right',
  },
  {
    key: 'market_value',
    header: 'Mkt Value',
    render: (v) => <span className="font-semibold">{formatINR(Number(v))}</span>,
    className: 'text-right',
  },
  {
    key: 'unrealised_pnl',
    header: 'Unrealised P&L',
    render: (v) => {
      const n = Number(v);
      return <span className={pnlStyle(n)}>{n >= 0 ? '+' : ''}{formatINR(n)}</span>;
    },
    className: 'text-right',
  },
  {
    key: 'weight_pct',
    header: 'Weight',
    render: (v) => `${Number(v).toFixed(1)}%`,
    className: 'text-right',
  },
];

export const HoldingsTable: React.FC<HoldingsTableProps> = ({ holdings, loading }) => (
  <DataTable<Holding>
    columns={columns}
    data={holdings}
    rowKey="symbol"
    loading={loading}
    searchKeys={['symbol', 'name', 'asset_class']}
    emptyMessage="No holdings found."
  />
);

export default HoldingsTable;
