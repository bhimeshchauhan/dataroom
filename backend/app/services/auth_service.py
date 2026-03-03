import os
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import db
from app.models.user import User
from app.utils.errors import ConflictError, NotFoundError, ValidationError


class AuthService:

    @staticmethod
    def _jwt_secret():
        return os.environ.get('JWT_SECRET', 'dev-secret-change-me')

    @staticmethod
    def _jwt_exp_minutes():
        return int(os.environ.get('JWT_EXP_MINUTES', '1440'))

    @staticmethod
    def _validate_email(email):
        if not email or not isinstance(email, str):
            raise ValidationError('Email is required')
        email = email.strip().lower()
        if '@' not in email or len(email) > 255:
            raise ValidationError('Email is invalid')
        return email

    @staticmethod
    def _validate_password(password):
        if not password or not isinstance(password, str):
            raise ValidationError('Password is required')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters')
        return password

    @staticmethod
    def _issue_token(user):
        now = datetime.now(timezone.utc)
        payload = {
            'sub': user.id,
            'email': user.email,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=AuthService._jwt_exp_minutes())).timestamp()),
        }
        return jwt.encode(payload, AuthService._jwt_secret(), algorithm='HS256')

    @staticmethod
    def register(email, password):
        email = AuthService._validate_email(email)
        password = AuthService._validate_password(password)

        existing = User.query.filter(User.email == email).first()
        if existing:
            raise ConflictError('Email is already registered')

        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return {'user': user, 'token': AuthService._issue_token(user)}

    @staticmethod
    def login(email, password):
        email = AuthService._validate_email(email)
        password = AuthService._validate_password(password)

        user = User.query.filter(User.email == email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValidationError('Invalid email or password')

        return {'user': user, 'token': AuthService._issue_token(user)}

    @staticmethod
    def get_user_from_token(token):
        if not token:
            raise ValidationError('Missing token')
        try:
            payload = jwt.decode(
                token,
                AuthService._jwt_secret(),
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise ValidationError('Token has expired')
        except jwt.InvalidTokenError:
            raise ValidationError('Invalid token')

        user_id = payload.get('sub')
        user = User.query.filter(User.id == str(user_id)).first()
        if not user:
            raise NotFoundError('User not found')
        return user
