export type Role = 'admin' | 'editor' | 'ministry_lead' | 'staff' | 'member';

export interface UserSession {
  accessToken: string;
  email: string;
  fullName: string;
  avatar?: string;
  roles: Role[];
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  fullName: string;
}

export interface AuthResponse {
  accessToken: string;
  user: {
    email: string;
    fullName: string;
    avatar?: string;
    roles: Role[];
  };
}

export interface Sermon {
  id: string;
  title: string;
  body?: string;
  preached_on: string;
  tags: string[];
}

export interface Prayer {
  id: string;
  category: string;
  content: string;
  status: 'active' | 'closed';
  is_moderated: boolean;
  support_count: number;
}

export interface Task {
  id: string;
  title: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high' | 'critical';
  deadline?: string;
}
