'use client';

import Link from 'next/link';

export default function PublicHomePage() {
  return (
    <main>
      <h1 className='mb-2 text-4xl font-bold text-brand-900'>Церковь «Новая жизнь»</h1>
      <p className='mb-6 text-slate-700'>Саранск: новости общины, проповеди, молитвенные нужды и календарь событий.</p>
      <div className='grid gap-3 md:grid-cols-2'>
        <Link href='/sermons' className='rounded border bg-white p-4 hover:bg-brand-50'>Проповеди: архив и фильтры</Link>
        <Link href='/news' className='rounded border bg-white p-4 hover:bg-brand-50'>Новости и репортажи</Link>
        <Link href='/holidays' className='rounded border bg-white p-4 hover:bg-brand-50'>Ближайшие праздники</Link>
        <Link href='/prayers' className='rounded border bg-white p-4 hover:bg-brand-50'>Молитвенные нужды и «Я молюсь»</Link>
      </div>
      <div className='mt-6'>
        <Link href='/dashboard' className='rounded bg-brand-500 px-4 py-2 text-white'>Внутренняя система управления</Link>
      </div>
    </main>
  );
}
