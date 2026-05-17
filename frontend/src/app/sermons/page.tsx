'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Sermon } from '@/types';

export default function SermonsPage() {
  const [sermons, setSermons] = useState<Sermon[]>([]);
  const [q, setQ] = useState('');
  const [tag, setTag] = useState('');

  async function load() {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (tag) params.set('tag', tag);
    const { data } = await api.get<Sermon[]>(`/sermons?${params.toString()}`);
    setSermons(data);
  }

  useEffect(() => { void load(); }, []);

  return (
    <main>
      <h1 className='mb-3 text-2xl font-semibold'>Проповеди</h1>
      <div className='mb-4 flex flex-wrap gap-2'>
        <input value={q} onChange={(e) => setQ(e.target.value)} className='rounded border px-3 py-2' placeholder='Поиск по названию/спикеру' />
        <input value={tag} onChange={(e) => setTag(e.target.value)} className='rounded border px-3 py-2' placeholder='Тематика (тег)' />
        <button onClick={() => void load()} className='rounded bg-brand-500 px-3 py-2 text-white'>Фильтровать</button>
      </div>
      <div className='space-y-2'>
        {sermons.map((s) => (
          <div key={s.id} className='rounded border bg-white p-3'>
            <div className='font-medium'>{s.title}</div>
            <div className='text-sm text-slate-600'>{new Date(s.preached_on).toLocaleDateString('ru-RU')}</div>
          </div>
        ))}
      </div>
    </main>
  );
}
