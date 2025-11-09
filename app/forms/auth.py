"""
Authentication Forms for Laser OS Tier 1

This module contains all authentication-related forms:
- LoginForm: User login
- ChangePasswordForm: Change password for logged-in users
- ResetPasswordForm: Admin password reset
- UserForm: Create/edit user accounts
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models.auth import User
import re


class LoginForm(FlaskForm):
    """Form for user login."""
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    
    remember_me = BooleanField('Remember Me')
    
    submit = SubmitField('Log In')


class ChangePasswordForm(FlaskForm):
    """Form for users to change their own password."""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, field):
        """Validate password strength."""
        password = field.data
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')


class ResetPasswordForm(FlaskForm):
    """Form for admin to reset user password."""
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm the password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    submit = SubmitField('Reset Password')
    
    def validate_new_password(self, field):
        """Validate password strength."""
        password = field.data
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')


class UserForm(FlaskForm):
    """Form for creating and editing user accounts."""
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address'),
        Length(max=120, message='Email must be less than 120 characters')
    ])
    
    full_name = StringField('Full Name', validators=[
        Optional(),
        Length(max=200, message='Full name must be less than 200 characters')
    ])
    
    password = PasswordField('Password', validators=[
        Length(min=8, message='Password must be at least 8 characters')
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    
    is_active = BooleanField('Active Account')
    
    is_superuser = BooleanField('Superuser (Full System Access)')
    
    roles = SelectMultipleField('Roles', coerce=int)
    
    submit = SubmitField('Save User')
    
    def __init__(self, user=None, *args, **kwargs):
        """
        Initialize form with optional user for editing.
        
        Args:
            user (User): User object for editing (None for new user)
        """
        super(UserForm, self).__init__(*args, **kwargs)
        self.user = user
        
        # Load role choices
        from app.models.auth import Role
        self.roles.choices = [(r.id, r.display_name) for r in Role.query.order_by(Role.name).all()]
    
    def validate_username(self, field):
        """Validate username is unique."""
        # Skip validation if editing existing user with same username
        if self.user and self.user.username == field.data:
            return
        
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different username.')
    
    def validate_email(self, field):
        """Validate email is unique."""
        # Skip validation if editing existing user with same email
        if self.user and self.user.email == field.data:
            return
        
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
    
    def validate_password(self, field):
        """Validate password strength (only if password is provided)."""
        # Password is optional for editing existing users
        if not field.data:
            # Password is required for new users
            if not self.user:
                raise ValidationError('Password is required for new users')
            return
        
        password = field.data
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character')

