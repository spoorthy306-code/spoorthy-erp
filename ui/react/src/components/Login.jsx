import { useState } from 'react';

export default function Login({ onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const onSubmit = e => {
    e.preventDefault();
    if (username && password) {
      localStorage.setItem('erp_user', username);
      onSuccess();
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-slate-100">
      <form className="bg-white shadow-lg p-8 rounded-lg w-96" onSubmit={onSubmit}>
        <h2 className="text-2xl font-bold mb-4">Spoorthy ERP Login</h2>
        <input className="w-full mb-3 p-2 border rounded" placeholder="Username" onChange={e => setUsername(e.target.value)} />
        <input type="password" className="w-full mb-3 p-2 border rounded" placeholder="Password" onChange={e => setPassword(e.target.value)} />
        <button className="w-full py-2 rounded bg-blue-600 text-white">Sign in</button>
      </form>
    </div>
  );
}
