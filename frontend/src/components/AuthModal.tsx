'use client';

import { useState } from 'react';
import { useSessionStore } from '@/store/session';
import { authApi } from '@/lib/api';
import { UserSession } from '@/types';

interface AuthModalProps {
  onClose: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const setSession = useSessionStore((s) => s.setSession);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authApi.login({ email, password });
        const userSession: UserSession = {
          accessToken: response.data.accessToken,
          email: response.data.user.email,
          fullName: response.data.user.fullName,
          avatar: response.data.user.avatar,
          roles: response.data.user.roles,
        };
        setSession(userSession);
      } else {
        const response = await authApi.register({ email, password, fullName });
        const userSession: UserSession = {
          accessToken: response.data.accessToken,
          email: response.data.user.email,
          fullName: response.data.user.fullName,
          avatar: response.data.user.avatar,
          roles: response.data.user.roles,
        };
        setSession(userSession);
      }
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Ошибка авторизации');
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4'
      onClick={handleOverlayClick}
    >
      <div className='bg-white rounded-lg shadow-xl max-w-md w-full p-8 relative'>
        <button
          onClick={onClose}
          className='absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl'
          aria-label='Закрыть'
        >
          ×
        </button>

        <h2 className='text-2xl font-bold text-center text-gray-800 mb-6'>
          {isLogin ? 'Вход' : 'Регистрация'}
        </h2>

        {error && (
          <div className='bg-red-50 text-red-600 p-3 rounded-md mb-4 text-sm'>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className='space-y-4'>
          {!isLogin && (
            <div>
              <label htmlFor='fullName' className='block text-sm font-medium text-gray-700 mb-1'>
                Полное имя
              </label>
              <input
                type='text'
                id='fullName'
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className='w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none'
                placeholder='Иван Иванов'
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label htmlFor='email' className='block text-sm font-medium text-gray-700 mb-1'>
              Email
            </label>
            <input
              type='email'
              id='email'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className='w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none'
              placeholder='email@example.com'
              required
            />
          </div>

          <div>
            <label htmlFor='password' className='block text-sm font-medium text-gray-700 mb-1'>
              Пароль
            </label>
            <input
              type='password'
              id='password'
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className='w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none'
              placeholder='Введите пароль'
              required
            />
          </div>

          <button
            type='submit'
            disabled={loading}
            className='w-full bg-blue-600 text-white py-2 px-4 rounded-md font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
          >
            {loading ? 'Загрузка...' : isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className='mt-4 text-center text-sm text-gray-600'>
          {isLogin ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className='text-blue-600 hover:text-blue-800 font-medium focus:outline-none'
          >
            {isLogin ? 'Зарегистрироваться' : 'Войти'}
          </button>
        </div>
      </div>
    </div>
  );
}
