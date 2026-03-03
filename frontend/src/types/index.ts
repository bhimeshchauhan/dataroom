export interface Dataroom {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: string;
  dataroom_id: string;
  parent_id: string | null;
  name: string;
  path: string;
  created_at: string;
  updated_at: string;
}

export interface FileItem {
  id: string;
  dataroom_id: string;
  folder_id: string | null;
  name: string;
  mime_type: string;
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

export interface Breadcrumb {
  id: string | null;
  name: string;
}

export interface ContentsResponse {
  folder: Folder | null;
  breadcrumbs: Breadcrumb[];
  folders: Folder[];
  files: FileItem[];
  pagination: Pagination;
}

export interface Pagination {
  page: number;
  per_page: number;
  total_folders?: number;
  total_files?: number;
  total?: number;
}

export interface TreeNode {
  id: string;
  name: string;
  children: TreeNode[];
}
