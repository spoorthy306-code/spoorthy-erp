import { LoginForm } from '@/components/auth/LoginForm';
import { useDefaultAdmin } from '@/hooks/useDefaultAdmin';

export default function LoginPage() {
  const { error } = useDefaultAdmin();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-4">
      <LoginForm />
      <section className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
        <p className="font-medium text-slate-700">Default credentials (first login)</p>
        <p className="mt-1">Username: admin</p>
        <p>Password: admin123</p>
        {error ? <p className="mt-2 text-danger">Init error: {error}</p> : null}
      </section>
    </main>
  );
}
