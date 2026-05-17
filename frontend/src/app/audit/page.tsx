'use client';

import { useEffect, useState } from 'react';
import { Nav } from '@/components/nav';
import { api } from '@/lib/api';

interface LogItem { id: number; action: string; entity_type: string; entity_id: string }

export default function AuditPage() {
  const [logs, setLogs] = useState<LogItem[]>([]);

  useEffect(() => {
    api.get<LogItem[]>('/audit-logs').then((r) => setLogs(r.data)).catch(() => setLogs([]));
  }, []);

  return (
    <main>
      <Nav />
      <h1 className='mb-3 text-2xl font-semibold'>Audit Log</h1>
      <div className='space-y-2'>
        {logs.map((l) => <div key={l.id} className='rounded border bg-white p-3'>{l.action} {l.entity_type} {l.entity_id}</div>)}
      </div>
    </main>
  );
}
