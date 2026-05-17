'use client';

import { useEffect, useMemo, useState } from 'react';
import { Nav } from '@/components/nav';
import { api } from '@/lib/api';
import { Task } from '@/types';

export default function MinistriesPage() {
  const [tasks, setTasks] = useState<Task[]>([]);

  async function load() {
    const { data } = await api.get<Task[]>('/tasks');
    setTasks(data);
  }

  useEffect(() => { void load(); }, []);

  const columns = useMemo(() => ({
    todo: tasks.filter((t) => t.status === 'todo'),
    in_progress: tasks.filter((t) => t.status === 'in_progress'),
    done: tasks.filter((t) => t.status === 'done'),
  }), [tasks]);

  return (
    <main>
      <Nav />
      <h1 className='mb-3 text-2xl font-semibold'>Канбан служений</h1>
      <div className='grid gap-3 md:grid-cols-3'>
        {Object.entries(columns).map(([k, list]) => (
          <section key={k} className='rounded border bg-white p-3'>
            <h2 className='mb-2 font-semibold'>{k}</h2>
            <div className='space-y-2'>
              {list.map((t) => <div key={t.id} className='rounded border p-2'>{t.title}</div>)}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
