'use client';

import { Nav } from '@/components/nav';
import { useSessionStore } from '@/store/session';

export default function DashboardPage() {
  const setSession = useSessionStore((s) => s.setSession);

  return (
    <main>
      <h1 className='mb-2 text-3xl font-bold text-brand-900'>Внутренняя панель</h1>
      <p className='mb-5 text-slate-700'>Демо-переключение ролей для ERP-модуля.</p>
      <div className='mb-4 flex flex-wrap gap-2'>
        <button className='rounded bg-brand-500 px-3 py-2 text-white' onClick={() => setSession({ accessToken: '', role: 'admin', email: 'admin@local' })}>Admin</button>
        <button className='rounded border px-3 py-2' onClick={() => setSession({ accessToken: '', role: 'editor', email: 'editor@local' })}>Editor</button>
        <button className='rounded border px-3 py-2' onClick={() => setSession({ accessToken: '', role: 'staff', email: 'staff@local' })}>Staff</button>
      </div>
      <Nav />
    </main>
  );
}
