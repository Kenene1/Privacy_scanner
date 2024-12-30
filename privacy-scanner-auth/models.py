from app import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
import uuid

class User(db.Model, UserMixin):
    """Database model for storing user details."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # 'user', 'admin', etc.

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify the hashed password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def confirm_email(self):
        """Mark the user's email as confirmed."""
        self.email_confirmed = True

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

class RevokedToken(db.Model):
    """Database model for storing revoked tokens (optional for JWT implementations)."""
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<RevokedToken {self.jti}>"
