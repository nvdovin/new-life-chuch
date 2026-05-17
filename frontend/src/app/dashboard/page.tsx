'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { api, setAuthToken } from '@/lib/api';
import { Role, UserSession } from '@/types';

interface MeResponse {
  id: string;
  email: string;
  full_name: string;
  roles: Role[];
}

interface ManagedUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  roles: Role[];
}

const editableResources = [
  { key: 'sermons', label: 'Проповеди' },
  { key: 'news', label: 'Новости' },
  { key: 'holidays', label: 'Праздники' },
  { key: 'prayers', label: 'Молитвы' },
  { key: 'ministries', label: 'Служения' },
  { key: 'tasks', label: 'Задачи' },
  { key: 'knowledge', label: 'База знаний' },
] as const;

const allRoles: Role[] = ['admin', 'editor', 'ministry_lead', 'staff', 'member'];

function getStoredSession(): UserSession | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem('nlc-session');
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as { state?: { session?: UserSession | null } };
    return parsed.state?.session || null;
  } catch {
    return null;
  }
}

function setStoredSession(session: UserSession | null) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('nlc-session', JSON.stringify({ state: { session }, version: 0 }));
}

function RoleEditor({ value, onChange }: { value: Role[]; onChange: (roles: Role[]) => void }) {
  return (
    <div className='flex flex-wrap gap-2'>
      {allRoles.map((role) => {
        const checked = value.includes(role);
        return (
          <label key={role} className='flex items-center gap-1 rounded border bg-white px-2 py-1 text-xs'>
            <input
              type='checkbox'
              checked={checked}
              onChange={(e) => {
                if (e.target.checked) onChange([...value, role]);
                else onChange(value.filter((r) => r !== role));
              }}
            />
            {role}
          </label>
        );
      })}
    </div>
  );
}

function JsonCrudSection({
  endpoint,
  label,
  token,
}: {
  endpoint: string;
  label: string;
  token: string;
}) {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [createJson, setCreateJson] = useState('{}');
  const [patchId, setPatchId] = useState('');
  const [patchJson, setPatchJson] = useState('{}');
  const [deleteId, setDeleteId] = useState('');
  const [error, setError] = useState('');

  async function load() {
    try {
      const { data } = await api.get<Record<string, unknown>[]>(`/${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setItems(data);
      setError('');
    } catch (e: unknown) {
      setError('Не удалось загрузить раздел. Проверьте права доступа.');
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function createItem() {
    try {
      const payload = JSON.parse(createJson);
      await api.post(`/${endpoint}`, payload, { headers: { Authorization: `Bearer ${token}` } });
      await load();
    } catch {
      setError('Ошибка создания. Убедитесь, что JSON и поля корректны.');
    }
  }

  async function patchItem() {
    try {
      const payload = JSON.parse(patchJson);
      await api.patch(`/${endpoint}/${patchId}`, payload, { headers: { Authorization: `Bearer ${token}` } });
      await load();
    } catch {
      setError('Ошибка обновления. Проверьте ID, JSON и права.');
    }
  }

  async function deleteItem() {
    try {
      await api.delete(`/${endpoint}/${deleteId}`, { headers: { Authorization: `Bearer ${token}` } });
      await load();
    } catch {
      setError('Ошибка удаления. Проверьте ID и права.');
    }
  }

  return (
    <section className='rounded border bg-white p-4'>
      <h3 className='mb-3 text-lg font-semibold'>{label}</h3>
      {error ? <p className='mb-2 text-sm text-red-700'>{error}</p> : null}
      <div className='mb-3 overflow-auto rounded border bg-slate-50 p-2 text-xs'>
        <pre>{JSON.stringify(items, null, 2)}</pre>
      </div>
      <div className='grid gap-2 md:grid-cols-3'>
        <div className='rounded border p-2'>
          <p className='mb-2 text-sm font-medium'>Создать</p>
          <textarea value={createJson} onChange={(e) => setCreateJson(e.target.value)} className='h-28 w-full rounded border p-2 text-xs' />
          <button className='mt-2 rounded bg-brand-500 px-3 py-2 text-sm text-white' onClick={() => void createItem()}>
            Создать
          </button>
        </div>
        <div className='rounded border p-2'>
          <p className='mb-2 text-sm font-medium'>Изменить</p>
          <input value={patchId} onChange={(e) => setPatchId(e.target.value)} className='mb-2 w-full rounded border px-2 py-1 text-xs' placeholder='ID' />
          <textarea value={patchJson} onChange={(e) => setPatchJson(e.target.value)} className='h-24 w-full rounded border p-2 text-xs' />
          <button className='mt-2 rounded bg-brand-500 px-3 py-2 text-sm text-white' onClick={() => void patchItem()}>
            Обновить
          </button>
        </div>
        <div className='rounded border p-2'>
          <p className='mb-2 text-sm font-medium'>Удалить</p>
          <input value={deleteId} onChange={(e) => setDeleteId(e.target.value)} className='w-full rounded border px-2 py-1 text-xs' placeholder='ID' />
          <button className='mt-2 rounded border px-3 py-2 text-sm' onClick={() => void deleteItem()}>
            Удалить
          </button>
        </div>
      </div>
    </section>
  );
}

export default function DashboardPage() {
  const [session, setSession] = useState<UserSession | null>(null);
  const [me, setMe] = useState<MeResponse | null>(null);
  const [email, setEmail] = useState('admin@local');
  const [password, setPassword] = useState('ChangeMe123!');
  const [error, setError] = useState('');

  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserRoles, setNewUserRoles] = useState<Role[]>(['member']);

  useEffect(() => {
    const stored = getStoredSession();
    if (!stored) return;
    setSession(stored);
  }, []);

  useEffect(() => {
    if (!session?.accessToken) return;
    setAuthToken(session.accessToken);
    api
      .get<MeResponse>('/users/me')
      .then((res) => setMe(res.data))
      .catch(() => {
        setSession(null);
        setStoredSession(null);
        setAuthToken(undefined);
      });
  }, [session?.accessToken]);

  const isAdmin = useMemo(() => me?.roles?.includes('admin') ?? false, [me]);

  async function login(e: FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const { data } = await api.post<{ access_token: string }>('/auth/login', { email, password });
      const token = data.access_token;
      setAuthToken(token);
      const meRes = await api.get<MeResponse>('/users/me');
      const nextSession: UserSession = {
        accessToken: token,
        email: meRes.data.email,
        fullName: meRes.data.full_name,
        roles: meRes.data.roles,
      };
      setStoredSession(nextSession);
      setSession(nextSession);
      setMe(meRes.data);
    } catch {
      setError('Неверный логин/пароль или у пользователя нет доступа.');
    }
  }

  async function loadUsers() {
    if (!session?.accessToken) return;
    const { data } = await api.get<ManagedUser[]>('/users', {
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });
    setUsers(data);
  }

  async function createUser() {
    if (!session?.accessToken) return;
    await api.post(
      '/users',
      {
        email: newUserEmail,
        full_name: newUserName,
        password: newUserPassword,
        roles: newUserRoles,
      },
      { headers: { Authorization: `Bearer ${session.accessToken}` } },
    );
    setNewUserEmail('');
    setNewUserName('');
    setNewUserPassword('');
    setNewUserRoles(['member']);
    await loadUsers();
  }

  async function updateUser(user: ManagedUser, updates: Record<string, unknown>) {
    if (!session?.accessToken) return;
    await api.patch(`/users/${user.id}`, updates, {
      headers: { Authorization: `Bearer ${session.accessToken}` },
    });
    await loadUsers();
  }

  useEffect(() => {
    if (isAdmin) void loadUsers();
  }, [isAdmin]);

  if (!session) {
    return (
      <main className='mx-auto max-w-xl p-6'>
        <h1 className='mb-2 text-3xl font-bold text-brand-900'>Вход в админ-панель</h1>
        <p className='mb-4 text-slate-700'>Авторизуйтесь, чтобы управлять пользователями, ролями и контентом сайта.</p>
        <form onSubmit={login} className='grid gap-2 rounded border bg-white p-4'>
          <input className='rounded border px-3 py-2' value={email} onChange={(e) => setEmail(e.target.value)} placeholder='Email' />
          <input type='password' className='rounded border px-3 py-2' value={password} onChange={(e) => setPassword(e.target.value)} placeholder='Пароль' />
          {error ? <p className='text-sm text-red-700'>{error}</p> : null}
          <button className='rounded bg-brand-500 px-3 py-2 text-white'>Войти</button>
        </form>
      </main>
    );
  }

  if (!isAdmin) {
    return (
      <main className='mx-auto max-w-2xl p-6'>
        <h1 className='mb-2 text-2xl font-semibold'>Доступ ограничен</h1>
        <p className='mb-4'>У вашей учётной записи нет роли `admin` для полной админ-панели.</p>
        <button
          onClick={() => {
            setSession(null);
            setStoredSession(null);
            setAuthToken(undefined);
          }}
          className='rounded border px-3 py-2'
        >
          Выйти
        </button>
      </main>
    );
  }

  return (
    <main className='mx-auto max-w-6xl space-y-5 p-6'>
      <section className='flex flex-wrap items-center justify-between gap-3 rounded border bg-white p-4'>
        <div>
          <h1 className='text-2xl font-bold text-brand-900'>Админ-панель</h1>
          <p className='text-sm text-slate-700'>Вы вошли как {me?.full_name} ({me?.email})</p>
        </div>
        <button
          onClick={() => {
            setSession(null);
            setStoredSession(null);
            setAuthToken(undefined);
          }}
          className='rounded border px-3 py-2'
        >
          Выйти
        </button>
      </section>

      <section className='rounded border bg-white p-4'>
        <h2 className='mb-3 text-xl font-semibold'>Пользователи и роли</h2>
        <div className='mb-4 grid gap-2 md:grid-cols-2'>
          <input className='rounded border px-3 py-2' value={newUserEmail} onChange={(e) => setNewUserEmail(e.target.value)} placeholder='Email нового пользователя' />
          <input className='rounded border px-3 py-2' value={newUserName} onChange={(e) => setNewUserName(e.target.value)} placeholder='ФИО нового пользователя' />
          <input className='rounded border px-3 py-2' value={newUserPassword} onChange={(e) => setNewUserPassword(e.target.value)} placeholder='Пароль (мин. 8 символов)' />
          <div>
            <RoleEditor value={newUserRoles} onChange={setNewUserRoles} />
          </div>
        </div>
        <button className='mb-4 rounded bg-brand-500 px-3 py-2 text-white' onClick={() => void createUser()}>
          Создать пользователя
        </button>
        <div className='space-y-2'>
          {users.map((user) => (
            <div key={user.id} className='rounded border p-3'>
              <div className='mb-2 text-sm font-medium'>{user.full_name} ({user.email})</div>
              <RoleEditor value={user.roles} onChange={(roles) => void updateUser(user, { roles })} />
              <div className='mt-2 flex flex-wrap gap-2'>
                <button className='rounded border px-2 py-1 text-xs' onClick={() => void updateUser(user, { is_active: !user.is_active })}>
                  {user.is_active ? 'Деактивировать' : 'Активировать'}
                </button>
                <button
                  className='rounded border px-2 py-1 text-xs'
                  onClick={() => {
                    const passwordValue = prompt('Новый пароль пользователя');
                    if (!passwordValue) return;
                    void updateUser(user, { password: passwordValue });
                  }}
                >
                  Сменить пароль
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {editableResources.map((resource) => (
        <JsonCrudSection key={resource.key} endpoint={resource.key} label={resource.label} token={session.accessToken} />
      ))}
    </main>
  );
}
