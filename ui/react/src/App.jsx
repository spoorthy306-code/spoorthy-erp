import { Link, Route, Routes, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Inventory from './pages/Inventory';

function App() {
  const navigate = useNavigate();
  const session = localStorage.getItem('erp_user');

  if (!session) {
    return <Login onSuccess={() => navigate('/app')} />;
  }

  return (
    <div className="min-h-screen flex bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Inventory />} />
          <Route path="/app" element={<Inventory />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
