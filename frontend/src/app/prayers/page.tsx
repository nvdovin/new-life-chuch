'use client';

import { useEffect, useMemo, useState } from 'react';
import { api } from '@/lib/api';
import { Prayer } from '@/types';

export default function PrayersPage() {
  const [items, setItems] = useState<Prayer[]>([]);
  const [name, setName] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('Общее');
  const fingerprint = useMemo(() => {
    if (typeof window === 'undefined') return 'server';
    const key = 'prayer-fingerprint';
    const existing = localStorage.getItem(key);
    if (existing) return existing;
    const created = crypto.randomUUID();
    localStorage.setItem(key, created);
    return created;
  }, []);

  async function load() {
    const { data } = await api.get<Prayer[]>('/prayers?public_only=true');
    setItems(data);
  }

  useEffect(() => { void load(); }, []);

  async function sendPrayer() {
    await api.post('/prayers', { category, content, is_anonymous: name.trim() === '' });
    setName('');
    setContent('');
    await load();
  }

  async function support(id: string) {
    await api.post(`/prayers/${id}/support`, { fingerprint });
    await load();
  }

  return (
    <main>
      <h1 className='mb-3 text-2xl font-semibold'>Молитвенные нужды</h1>
      <div className='mb-6 grid gap-2 rounded border bg-white p-4'>
        <input value={name} onChange={(e) => setName(e.target.value)} className='rounded border px-3 py-2' placeholder='Ваше имя (необязательно)' />
        <input value={category} onChange={(e) => setCategory(e.target.value)} className='rounded border px-3 py-2' placeholder='Категория' />
        <textarea value={content} onChange={(e) => setContent(e.target.value)} className='min-h-24 rounded border px-3 py-2' placeholder='Опишите молитвенную нужду' />
        <button onClick={() => void sendPrayer()} className='w-fit rounded bg-brand-500 px-3 py-2 text-white'>Отправить</button>
      </div>
      <div className='space-y-2'>
        {items.map((p) => (
          <div key={p.id} className='rounded border bg-white p-3'>
            <p className='font-medium'>{p.category}</p>
            <p className='text-sm text-slate-700'>{p.content}</p>
            <button className='mt-2 rounded border px-2 py-1' onClick={() => void support(p.id)}>Я молюсь ({p.support_count})</button>
          </div>
        ))}
      </div>
    </main>
  );
}
