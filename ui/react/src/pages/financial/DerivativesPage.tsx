import React, { useState } from 'react';

interface Greeks {
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho_call: number;
  rho_put: number;
}

interface PricingResult {
  call_price: number;
  put_price:  number;
  greeks:     Greeks;
  d1:         number;
  d2:         number;
}

function stdNormalCDF(x: number): number {
  const a = [0.319381530, -0.356563782, 1.781477937, -1.821255978, 1.330274429];
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const poly = a.reduce((s, ai, i) => s + ai * Math.pow(t, i + 1), 0);
  const n = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-x * x / 2) * poly;
  return x >= 0 ? 1 - n : n;
}

function stdNormalPDF(x: number): number {
  return (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-x * x / 2);
}

function blackScholes(S: number, K: number, T: number, r: number, sigma: number): PricingResult {
  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T));
  const d2 = d1 - sigma * Math.sqrt(T);
  const C  = S * stdNormalCDF(d1) - K * Math.exp(-r * T) * stdNormalCDF(d2);
  const P  = K * Math.exp(-r * T) * stdNormalCDF(-d2) - S * stdNormalCDF(-d1);

  return {
    call_price: C,
    put_price:  P,
    d1, d2,
    greeks: {
      delta:    stdNormalCDF(d1),
      gamma:    stdNormalPDF(d1) / (S * sigma * Math.sqrt(T)),
      vega:     S * stdNormalPDF(d1) * Math.sqrt(T) / 100,   // per 1% vol move
      theta:    (-(S * sigma * stdNormalPDF(d1)) / (2 * Math.sqrt(T))
                 - r * K * Math.exp(-r * T) * stdNormalCDF(d2)) / 365,  // per day
      rho_call:  K * T * Math.exp(-r * T) * stdNormalCDF(d2)  / 100,   // per 1% rate move
      rho_put:  -K * T * Math.exp(-r * T) * stdNormalCDF(-d2) / 100,
    },
  };
}

const fmt4 = (v: number): string => v.toFixed(4);
const fmtINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(v);

interface GreekRowProps { name: string; value: number; description: string; positive?: boolean }
const GreekRow: React.FC<GreekRowProps> = ({ name, value, description, positive }) => (
  <tr className="border-b border-gray-50">
    <td className="py-2 pr-4 font-mono font-bold text-indigo-700">{name}</td>
    <td className={`py-2 pr-4 text-right font-semibold ${positive === undefined ? '' : value >= 0 === positive ? 'text-green-700' : 'text-red-600'}`}>
      {fmt4(value)}
    </td>
    <td className="py-2 text-xs text-gray-500">{description}</td>
  </tr>
);

export const DerivativesPage: React.FC = () => {
  const [S,     setS]     = useState('1800');
  const [K,     setK]     = useState('1850');
  const [T,     setT]     = useState('0.25');
  const [r,     setR]     = useState('0.065');
  const [sigma, setSigma] = useState('0.22');
  const [result, setResult] = useState<PricingResult | null>(null);

  const handlePrice = (): void => {
    const s = parseFloat(S), k = parseFloat(K), t = parseFloat(T),
          rr = parseFloat(r), sig = parseFloat(sigma);
    if ([s, k, t, rr, sig].some(isNaN) || t <= 0 || sig <= 0 || s <= 0 || k <= 0) {
      alert('All parameters must be positive numbers, T and sigma > 0');
      return;
    }
    setResult(blackScholes(s, k, t, rr, sig));
  };

  const inputCls = 'w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400';

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Derivatives Pricer</h1>
      <p className="text-sm text-gray-500 mb-6">Black-Scholes European Options + Full Greeks</p>

      <div className="rounded-xl border border-gray-100 shadow-sm bg-white p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Input Parameters</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {([
            ['Spot Price (S)', S, setS],
            ['Strike Price (K)', K, setK],
            ['Time to Expiry T (years)', T, setT],
            ['Risk-free Rate r', r, setR],
            ['Volatility sigma (annual)', sigma, setSigma],
          ] as [string, string, React.Dispatch<React.SetStateAction<string>>][]).map(([label, val, setter]) => (
            <div key={label}>
              <label className="block text-xs font-medium text-gray-500 mb-1">{label}</label>
              <input type="number" step="any" value={val}
                onChange={(e) => setter(e.target.value)}
                className={inputCls} />
            </div>
          ))}
        </div>
        <button onClick={handlePrice}
          className="mt-5 rounded-lg bg-indigo-600 px-6 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors">
          Price Option
        </button>
      </div>

      {result && (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div className="rounded-xl border border-gray-100 shadow-sm bg-white p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Option Prices</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-blue-50 p-4 text-center">
                <p className="text-xs text-blue-500 mb-1">Call Price</p>
                <p className="text-2xl font-bold text-blue-700">{fmtINR(result.call_price)}</p>
              </div>
              <div className="rounded-lg bg-rose-50 p-4 text-center">
                <p className="text-xs text-rose-500 mb-1">Put Price</p>
                <p className="text-2xl font-bold text-rose-700">{fmtINR(result.put_price)}</p>
              </div>
            </div>
            <div className="mt-4 text-xs text-gray-400 grid grid-cols-2 gap-2">
              <div>d1 = {fmt4(result.d1)}</div>
              <div>d2 = {fmt4(result.d2)}</div>
            </div>
          </div>

          <div className="rounded-xl border border-gray-100 shadow-sm bg-white p-6">
            <h2 className="text-sm font-semibold text-gray-700 mb-4">Greeks</h2>
            <table className="w-full text-sm">
              <tbody>
                <GreekRow name="Delta"    value={result.greeks.delta}    description="Price sensitivity per 1 spot move"       positive />
                <GreekRow name="Gamma"    value={result.greeks.gamma}    description="Delta change per 1 spot move"            positive />
                <GreekRow name="Vega"     value={result.greeks.vega}     description="Price change per 1% vol move"             positive />
                <GreekRow name="Theta"    value={result.greeks.theta}    description="Price decay per day (usually negative)" />
                <GreekRow name="Rho (C)"  value={result.greeks.rho_call} description="Call price change per 1% rate move"      positive />
                <GreekRow name="Rho (P)"  value={result.greeks.rho_put}  description="Put price change per 1% rate move" />
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DerivativesPage;
