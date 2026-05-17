'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useSessionStore } from '@/store/session';
import { AuthModal } from './AuthModal';
import { UserAvatar } from './UserAvatar';

export function Header() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const session = useSessionStore((s) => s.session);
  const clearSession = useSessionStore((s) => s.clearSession);

  const handleLogout = () => {
    clearSession();
  };

  return (
    <header className='site-header'>
      <div className='container nav-wrap'>
        <div className='brand'>
          <div className='brand-logo' aria-hidden='true'>
            ✝
          </div>
          <div>
            <p className='brand-title'>Баптисты</p>
            <p className='brand-subtitle'>ВЕРА · СЕМЬЯ · СЛУЖЕНИЕ</p>
          </div>
        </div>

        <nav className='main-nav' aria-label='Главное меню'>
          <Link href='/' className='active'>
            ГЛАВНАЯ
          </Link>
          <Link href='#about'>О НАС</Link>
          <Link href='#'>УЧЕНИЕ</Link>
          <Link href='#'>НОВОСТИ</Link>
          <Link href='#'>МЕРОПРИЯТИЯ</Link>
          <Link href='#'>РЕСУРСЫ</Link>
          <Link href='#'>КОНТАКТЫ</Link>
        </nav>

        <div className='flex items-center gap-4'>
          {session ? (
            <>
              <UserAvatar
                name={session.fullName}
                avatar={session.avatar}
                onLogout={handleLogout}
              />
              {session.roles.includes('admin') && (
                <Link href='/admin' className='btn-secondary px-4 py-2 text-sm font-medium'>
                  АДМИН
                </Link>
              )}
            </>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className='btn-primary px-6 py-2 text-sm font-medium'
            >
              ВОЙТИ
            </button>
          )}
        </div>
      </div>

      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </header>
  );
}
