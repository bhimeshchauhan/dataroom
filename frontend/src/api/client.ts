import type {
  Dataroom,
  Folder,
  FileItem,
  ContentsResponse,
  Pagination,
  TreeNode,
  StorageUsage,
} from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';
const AUTH_TOKEN_KEY = 'dataroom_auth_token';
export const AUTH_EXPIRED_EVENT = 'dataroom-auth-expired';

interface ApiError {
  error: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}/api/v1${path}`;
  const headers: Record<string, string> = {};
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(url, {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string>) },
  });

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
    }
    const data: ApiError = await res
      .json()
      .catch(() => ({ error: `HTTP ${res.status}` }));
    throw new Error(data.error);
  }

  if (res.status === 204) return null as T;
  return res.json();
}

export const api = {
  // Auth
  register: (email: string, password: string) =>
    request<{ user: { id: string; email: string }; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<{ user: { id: string; email: string }; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<{ id: string; email: string }>('/auth/me'),

  setToken: (token: string) => {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  },

  getToken: () => localStorage.getItem(AUTH_TOKEN_KEY),

  clearToken: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  },

  // Datarooms
  createDataroom: (name: string, description?: string) =>
    request<Dataroom>('/datarooms', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    }),

  listDatarooms: () =>
    request<{ datarooms: Dataroom[]; pagination: Pagination }>('/datarooms'),

  getDataroom: (id: string) => request<Dataroom>(`/datarooms/${id}`),

  updateDataroom: (id: string, data: { name?: string; description?: string }) =>
    request<Dataroom>(`/datarooms/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteDataroom: (id: string) =>
    request<null>(`/datarooms/${id}`, { method: 'DELETE' }),

  getDataroomContents: (
    id: string,
    sortBy = 'name',
    sortOrder = 'asc',
    page = 1,
    perPage = 20,
    search = ''
  ) => {
    const params = new URLSearchParams({
      sort_by: sortBy,
      sort_order: sortOrder,
      page: String(page),
      per_page: String(perPage),
    });
    if (search.trim()) params.set('search', search.trim());
    return request<ContentsResponse>(
      `/datarooms/${id}/contents?${params.toString()}`
    );
  },

  getTree: (dataroomId: string) =>
    request<{ tree: TreeNode[] }>(`/datarooms/${dataroomId}/tree`),

  getStorageUsage: () => request<StorageUsage>('/storage/usage'),

  // Folders
  createFolder: (
    dataroomId: string,
    name: string,
    parentId?: string | null
  ) =>
    request<Folder>(`/datarooms/${dataroomId}/folders`, {
      method: 'POST',
      body: JSON.stringify({ name, parent_id: parentId || null }),
    }),

  getFolderContents: (
    folderId: string,
    sortBy = 'name',
    sortOrder = 'asc',
    page = 1,
    perPage = 20,
    search = ''
  ) => {
    const params = new URLSearchParams({
      sort_by: sortBy,
      sort_order: sortOrder,
      page: String(page),
      per_page: String(perPage),
    });
    if (search.trim()) params.set('search', search.trim());
    return request<ContentsResponse>(
      `/folders/${folderId}/contents?${params.toString()}`
    );
  },

  renameFolder: (folderId: string, name: string) =>
    request<Folder>(`/folders/${folderId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    }),

  deleteFolder: (folderId: string) =>
    request<null>(`/folders/${folderId}`, { method: 'DELETE' }),

  // Files
  uploadFile: (
    dataroomId: string,
    file: File,
    folderId?: string | null
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) formData.append('folder_id', folderId);
    return request<FileItem>(`/datarooms/${dataroomId}/files`, {
      method: 'POST',
      body: formData,
    });
  },

  getFile: (fileId: string) => request<FileItem>(`/files/${fileId}`),

  getFileContentUrl: (fileId: string) =>
    `${API_BASE}/api/v1/files/${fileId}/content?token=${encodeURIComponent(
      localStorage.getItem(AUTH_TOKEN_KEY) || ''
    )}`,

  renameFile: (fileId: string, name: string) =>
    request<FileItem>(`/files/${fileId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    }),

  deleteFile: (fileId: string) =>
    request<null>(`/files/${fileId}`, { method: 'DELETE' }),
};
