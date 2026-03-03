"""Marshmallow schemas for API request/response documentation."""

from marshmallow import Schema, fields


# ── Dataroom ──────────────────────────────────────────────────────────────────

class DataroomCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(load_default=None)


class DataroomUpdateSchema(Schema):
    name = fields.String(load_default=None)
    description = fields.String(load_default=None)


class DataroomSchema(Schema):
    id = fields.String()
    name = fields.String()
    description = fields.String(allow_none=True)
    user_id = fields.String(allow_none=True)
    created_at = fields.String()
    updated_at = fields.String()
    deleted_at = fields.String(allow_none=True)


class PaginationSchema(Schema):
    total = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()


class ContentsPaginationSchema(Schema):
    total_folders = fields.Integer()
    total_files = fields.Integer()
    total_items = fields.Integer()
    page = fields.Integer()
    per_page = fields.Integer()
    pages = fields.Integer()


class DataroomListSchema(Schema):
    datarooms = fields.List(fields.Nested(DataroomSchema))
    pagination = fields.Nested(PaginationSchema)


# ── Folder ────────────────────────────────────────────────────────────────────

class FolderCreateSchema(Schema):
    name = fields.String(required=True)
    parent_id = fields.String(load_default=None)


class FolderSchema(Schema):
    id = fields.String()
    dataroom_id = fields.String()
    parent_id = fields.String(allow_none=True)
    name = fields.String()
    path = fields.String()
    created_at = fields.String()
    updated_at = fields.String()
    deleted_at = fields.String(allow_none=True)


# ── File ──────────────────────────────────────────────────────────────────────

class FileSchema(Schema):
    id = fields.String()
    dataroom_id = fields.String()
    folder_id = fields.String(allow_none=True)
    name = fields.String()
    mime_type = fields.String()
    size_bytes = fields.Integer()
    created_at = fields.String()
    updated_at = fields.String()
    deleted_at = fields.String(allow_none=True)


# ── Contents ──────────────────────────────────────────────────────────────────

class BreadcrumbSchema(Schema):
    id = fields.String()
    name = fields.String()


class ContentsSchema(Schema):
    folder = fields.Nested(FolderSchema, allow_none=True)
    breadcrumbs = fields.List(fields.Nested(BreadcrumbSchema))
    folders = fields.List(fields.Nested(FolderSchema))
    files = fields.List(fields.Nested(FileSchema))
    pagination = fields.Nested(ContentsPaginationSchema)


# ── Tree ──────────────────────────────────────────────────────────────────────

class TreeNodeSchema(Schema):
    id = fields.String()
    name = fields.String()
    dataroom_id = fields.String()
    parent_id = fields.String(allow_none=True)
    path = fields.String()
    created_at = fields.String()
    updated_at = fields.String()
    deleted_at = fields.String(allow_none=True)
    children = fields.List(fields.Nested(lambda: TreeNodeSchema()))


class TreeSchema(Schema):
    tree = fields.List(fields.Nested(TreeNodeSchema))


# ── Rename ────────────────────────────────────────────────────────────────────

class RenameSchema(Schema):
    name = fields.String(required=True)


# ── Pagination query params ───────────────────────────────────────────────────

class PaginationQuerySchema(Schema):
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=20)


class ContentQuerySchema(Schema):
    page = fields.Integer(load_default=1)
    per_page = fields.Integer(load_default=20)
    sort_by = fields.String(load_default='name')
    sort_order = fields.String(load_default='asc')
    search = fields.String(load_default=None)


# ── Error ─────────────────────────────────────────────────────────────────────

class AppErrorSchema(Schema):
    error = fields.String()


class StorageUsageSchema(Schema):
    used_bytes = fields.Integer()
    quota_bytes = fields.Integer()
    remaining_bytes = fields.Integer()
    usage_percent = fields.Integer()


class AuthRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class AuthLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserSchema(Schema):
    id = fields.String()
    email = fields.Email()
    created_at = fields.String()
    updated_at = fields.String()


class AuthResponseSchema(Schema):
    user = fields.Nested(UserSchema)
    token = fields.String()


class HealthSchema(Schema):
    status = fields.String()
