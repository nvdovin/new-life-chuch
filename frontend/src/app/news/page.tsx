'use client';

import { useEffect, useState } from 'react';
import { Nav } from '@/components/nav';
import { api } from '@/lib/api';

interface NewsItem { id: string; title: string; publish_at: string }

export default function NewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);

  async function load() {
    const { data } = await api.get<NewsItem[]>('/news');
    setNews(data);
  }

  useEffect(() => { void load(); }, []);

  return (
    <main>
      <Nav />
      <h1 className='mb-3 text-2xl font-semibold'>Новости и дни рождения</h1>
      <div className='space-y-2'>
        {news.map((n) => <div key={n.id} className='rounded border bg-white p-3'>{n.title}</div>)}
      </div>
    </main>
  );
}
