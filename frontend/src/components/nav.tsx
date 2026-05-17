'use client';

import Link from 'next/link';
import { useSessionStore } from '@/store/session';

const roleLinks: Record<string, { href: string; label: string }[]> = {
  admin: [
    { href: '/dashboard', label: 'Дашборд' },
    { href: '/sermons', label: 'Проповеди' },
    { href: '/news', label: 'Новости' },
    { href: '/prayers', label: 'Молитвы' },
    { href: '/ministries', label: 'Служения' },
    { href: '/audit', label: 'Аудит' },
  ],
  editor: [
    { href: '/dashboard', label: 'Дашборд' },
    { href: '/sermons', label: 'Проповеди' },
    { href: '/news', label: 'Новости' },
    { href: '/prayers', label: 'Молитвы' },
  ],
  staff: [
    { href: '/dashboard', label: 'Дашборд' },
    { href: '/ministries', label: 'Служения' },
    { href: '/prayers', label: 'Молитвы' },
  ],
  member: [
    { href: '/dashboard', label: 'Дашборд' },
    { href: '/prayers', label: 'Молитвы' },
  ],
};

export function Nav() {
  const role = useSessionStore((s) => s.session?.role || 'member');
  const links = roleLinks[role] || roleLinks.member;
  return (
    <nav className='mb-6 flex flex-wrap gap-3'>
      {links.map((l) => (
        <Link key={l.href} className='rounded border bg-white px-3 py-2 hover:bg-brand-50' href={l.href}>
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
