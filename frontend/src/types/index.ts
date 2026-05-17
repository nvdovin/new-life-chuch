export type Role = 'admin' | 'editor' | 'staff' | 'member';

export interface UserSession {
  accessToken: string;
  role: Role;
  email: string;
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
