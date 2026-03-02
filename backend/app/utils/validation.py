from app.utils.errors import ValidationError


def validate_name(name, max_length=255):
    """Validate a resource name. Returns stripped name."""
    if name is None:
        raise ValidationError('Name is required')

    if not isinstance(name, str):
        raise ValidationError('Name must be a string')

    name = name.strip()

    if len(name) == 0:
        raise ValidationError('Name cannot be empty')

    if len(name) > max_length:
        raise ValidationError(f'Name must be {max_length} characters or fewer')

    return name


def validate_folder_name(name):
    """Validate a folder name. Rejects path separators and null bytes."""
    name = validate_name(name)

    if '/' in name:
        raise ValidationError('Folder name cannot contain "/"')

    if '\\' in name:
        raise ValidationError('Folder name cannot contain "\\"')

    if '\x00' in name:
        raise ValidationError('Folder name cannot contain null bytes')

    return name


def validate_pagination(args):
    """Extract and validate pagination parameters from request args."""
    try:
        page = int(args.get('page', 1))
    except (ValueError, TypeError):
        raise ValidationError('page must be a positive integer')

    try:
        per_page = int(args.get('per_page', 20))
    except (ValueError, TypeError):
        raise ValidationError('per_page must be a positive integer')

    if page < 1:
        raise ValidationError('page must be a positive integer')

    if per_page < 1 or per_page > 100:
        raise ValidationError('per_page must be between 1 and 100')

    return page, per_page


def validate_sort(args, allowed_fields=('name', 'created_at', 'updated_at')):
    """Extract and validate sort parameters from request args."""
    sort_by = args.get('sort_by', 'name')
    sort_order = args.get('sort_order', 'asc')

    if sort_by not in allowed_fields:
        raise ValidationError(f'sort_by must be one of: {", ".join(allowed_fields)}')

    if sort_order not in ('asc', 'desc'):
        raise ValidationError('sort_order must be "asc" or "desc"')

    return sort_by, sort_order
