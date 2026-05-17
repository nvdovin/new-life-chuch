'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSessionStore } from '@/store/session';
import { Nav } from '@/components/nav';

export default function AdminPage() {
  const router = useRouter();
  const session = useSessionStore((s) => s.session);

  useEffect(() => {
    // Redirect if not authenticated or not admin
    if (!session) {
      router.push('/');
    } else if (!session.roles.includes('admin')) {
      router.push('/');
    }
  }, [session, router]);

  if (!session || !session.roles.includes('admin')) {
    return (
      <div className='min-h-screen flex items-center justify-center bg-gray-50'>
        <div className='bg-white p-8 rounded-lg shadow-md'>
          <h2 className='text-xl font-bold text-gray-800 mb-4'>Доступ запрещён</h2>
          <p className='text-gray-600'>У вас нет прав доступа к этой странице.</p>
        </div>
      </div>
    );
  }

  return (
    <main className='site-shell'>
      <div className='container py-8'>
        <h1 className='text-3xl font-bold text-gray-800 mb-6'>Админ-панель</h1>
        <p className='text-gray-600 mb-8'>
          Добро пожаловать, <span className='font-medium'>{session.fullName}</span>!
        </p>

        <div className='bg-white rounded-lg shadow-md p-6'>
          <h2 className='text-xl font-semibold text-gray-800 mb-4'>Быстрые действия</h2>
          <Nav />
        </div>

        <div className='mt-8 bg-white rounded-lg shadow-md p-6'>
          <h2 className='text-xl font-semibold text-gray-800 mb-4'>Статистика</h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
            <div className='bg-gray-50 rounded-lg p-4 text-center'>
              <p className='text-2xl font-bold text-gray-800'>0</p>
              <p className='text-sm text-gray-600'>Пользователей</p>
            </div>
            <div className='bg-gray-50 rounded-lg p-4 text-center'>
              <p className='text-2xl font-bold text-gray-800'>0</p>
              <p className='text-sm text-gray-600'>Проповедей</p>
            </div>
            <div className='bg-gray-50 rounded-lg p-4 text-center'>
              <p className='text-2xl font-bold text-gray-800'>0</p>
              <p className='text-sm text-gray-600'>Новостей</p>
            </div>
            <div className='bg-gray-50 rounded-lg p-4 text-center'>
              <p className='text-2xl font-bold text-gray-800'>0</p>
              <p className='text-sm text-gray-600'>Молитв</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
