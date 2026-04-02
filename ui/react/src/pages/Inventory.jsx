import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useState } from 'react';

function fetchProducts() {
  return fetch('/inventory/products').then(r => r.json());
}

function createProduct(payload) {
  return fetch('/inventory/products', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).then(r => r.json());
}

export default function Inventory() {
  const queryClient = useQueryClient();
  const { data = [], isLoading } = useQuery('products', fetchProducts);
  const mutation = useMutation(createProduct, {
    onSuccess: () => queryClient.invalidateQueries('products'),
  });

  const [name, setName] = useState('');
  const [code, setCode] = useState('');

  if (isLoading) return <p>Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl mb-4">Inventory Products</h1>
      <div className="mb-4 bg-white p-4 rounded shadow-sm">
        <input className="border p-2 mr-2" placeholder="Code" value={code} onChange={e => setCode(e.target.value)} />
        <input className="border p-2 mr-2" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
        <button className="bg-blue-600 text-white px-3 py-2 rounded" onClick={() => mutation.mutate({ code, name })}>Add</button>
      </div>
      <div className="bg-white p-4 rounded shadow-sm">
        <table className="w-full text-left border-collapse">
          <thead><tr><th className="p-2 border">Code</th><th className="p-2 border">Name</th><th className="p-2 border">Stock</th></tr></thead>
          <tbody>
            {data.map(item => (
              <tr key={item.id} className="even:bg-slate-50">
                <td className="p-2 border">{item.code}</td>
                <td className="p-2 border">{item.name}</td>
                <td className="p-2 border">{item.current_stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
