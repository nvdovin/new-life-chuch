'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Holiday { id: string; title: string; event_date: string; description?: string }

export default function HolidaysPage() {
  const [items, setItems] = useState<Holiday[]>([]);

  useEffect(() => {
    api.get<Holiday[]>('/holidays?public_only=true').then((r) => setItems(r.data)).catch(() => setItems([]));
  }, []);

  return (
    <main>
      <h1 className='mb-3 text-2xl font-semibold'>Ближайшие праздники</h1>
      <div className='space-y-2'>
        {items.map((h) => (
          <div key={h.id} className='rounded border bg-white p-3'>
            <div className='font-medium'>{h.title}</div>
            <div className='text-sm text-slate-600'>{new Date(h.event_date).toLocaleDateString('ru-RU')}</div>
            {h.description ? <div className='text-sm text-slate-700'>{h.description}</div> : null}
          </div>
        ))}
      </div>
    </main>
  );
}
