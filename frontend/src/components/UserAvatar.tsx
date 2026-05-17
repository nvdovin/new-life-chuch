'use client';

import { useState, useRef, useEffect } from 'react';

interface UserAvatarProps {
  name: string;
  avatar?: string;
  onLogout: () => void;
}

export function UserAvatar({ name, avatar, onLogout }: UserAvatarProps) {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const initials = name
    .split(' ')
    .map((part) => part[0]?.toUpperCase())
    .join('')
    .slice(0, 2);

  return (
    <div className='relative' ref={dropdownRef}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className='flex items-center gap-2 p-1 rounded-full hover:bg-gray-100 transition-colors'
        aria-label='Профиль пользователя'
      >
        {avatar ? (
          <img
            src={avatar}
            alt={name}
            className='w-10 h-10 rounded-full object-cover'
          />
        ) : (
          <div className='w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm'>
            {initials}
          </div>
        )}
        <span className='text-sm font-medium text-gray-700'>{name}</span>
      </button>

      {showDropdown && (
        <div className='absolute right-0 top-full mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-2 z-50'>
          <div className='px-4 py-2 border-b border-gray-200'>
            <p className='font-medium text-gray-900'>{name}</p>
          </div>
          <button
            onClick={() => {
              onLogout();
              setShowDropdown(false);
            }}
            className='w-full px-4 py-2 text-left text-red-600 hover:bg-gray-50 transition-colors'
          >
            Выйти
          </button>
        </div>
      )}
    </div>
  );
}
