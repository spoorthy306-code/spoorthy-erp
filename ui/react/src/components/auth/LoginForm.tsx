import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<FormValues>({
    mode: 'onChange',
    resolver: zodResolver(schema),
    defaultValues: {
      username: import.meta.env.DEV ? 'admin' : '',
      password: import.meta.env.DEV ? 'admin123' : '',
    },
  });

  const onSubmit = async (values: FormValues) => {
    await login(values);
    navigate('/dashboard');
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-panel"
    >
      <h2 className="text-2xl font-bold text-ink">Welcome Back</h2>
      <p className="mt-1 text-sm text-slate-500">Sign in to manage accounting, GST, and reports.</p>

      <label className="mt-6 block text-sm font-medium text-slate-700" htmlFor="username">
        Username
      </label>
      <input
        id="username"
        className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        {...register('username')}
      />
      {errors.username && <p className="mt-1 text-xs text-danger">{errors.username.message}</p>}

      <label className="mt-4 block text-sm font-medium text-slate-700" htmlFor="password">
        Password
      </label>
      <input
        id="password"
        type="password"
        className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        {...register('password')}
      />
      {errors.password && <p className="mt-1 text-xs text-danger">{errors.password.message}</p>}

      <button
        type="submit"
        disabled={!isValid || isLoading}
        className="focus-ring mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-brand px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? <LoadingSpinner /> : null}
        Sign In
      </button>
    </form>
  );
}
