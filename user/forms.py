from django import forms
from .models import Appointment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.core.validators import RegexValidator, EmailValidator
from django.conf import settings
from .encryption import encrypt_aes256, decrypt_aes256
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



# user/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape
from datetime import date, time
from .models import Appointment, Doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        appointment_date = self.cleaned_data['date']
        if appointment_date < date.today():
            raise ValidationError("Appointment cannot be in the past.")
        return appointment_date

    def clean_time(self):
        appointment_time = self.cleaned_data['time']
        start_time = time(10, 0)
        end_time = time(17, 0)
        if not (start_time <= appointment_time <= end_time):
            raise ValidationError("Appointment must be between 10:00 and 17:00.")
        return appointment_time

    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()
        if len(reason) > 500:
            raise ValidationError("Reason too long.")

        # Block dangerous SQL/XSS patterns
        forbidden = ["<", ">", "--", ";", "/*", "*/", "DROP", "SELECT", "INSERT", "DELETE", "UPDATE", " OR ", " AND "]
        for word in forbidden:
            if word.lower() in reason.lower():
                raise ValidationError("Invalid input detected.")

        # Escape anything remaining for safety
        return escape(reason)


import re
from django import forms
from django.contrib.auth.models import User
from .models import Profile
  # Make sure this import is correct

# user/forms.py
import re
import base64
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile
from .encryption import encrypt_aes256

class RegisterForm(forms.ModelForm):
    # Custom fields
    ic = forms.CharField(max_length=12, required=True)
    phone = forms.CharField(max_length=11, required=True)
    address = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    # Field-level validation
    def clean_ic(self):
        ic = self.cleaned_data.get("ic")
        if not re.fullmatch(r"\d{12}", ic):
            raise forms.ValidationError("IC must be exactly 12 digits.")
        return ic

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.fullmatch(r"\d{9,11}", phone):
            raise forms.ValidationError("Phone number must be 9–11 digits.")
        return phone

    def clean_address(self):
        address = self.cleaned_data.get("address", "").strip()
        if "<" in address or ">" in address:
            raise forms.ValidationError("Address contains invalid characters.")

        # Block dangerous SQL keywords (defense-in-depth)
        forbidden = ["--", ";", "/*", "*/", " OR ", " AND ", " DROP ", " SELECT ", " INSERT ", " DELETE ", " UPDATE "]
        for keyword in forbidden:
            if keyword.lower() in address.lower():
                raise forms.ValidationError("Invalid input detected.")
        return address

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.isalnum():
            raise forms.ValidationError("Username can only contain letters and numbers.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        return email

    # Password validation
    def clean_password(self):
        password = self.cleaned_data.get("password")
        user_instance = User(username=self.cleaned_data.get("username") or "")
        validate_password(password, user=user_instance)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    # Save method with encryption
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]

        # Validate password again before saving
        try:
            validate_password(password, user)
        except ValidationError as e:
            self.add_error('password', e)
            raise

        user.set_password(password)

        if commit:
            user.save()
            # Encrypt sensitive fields
            try:
                Profile.objects.create(
                    user=user,
                    ic=encrypt_aes256(self.cleaned_data['ic']),
                    phone=encrypt_aes256(self.cleaned_data['phone']),
                    email=encrypt_aes256(self.cleaned_data['email']),
                    address=encrypt_aes256(self.cleaned_data['address']),
                )
            except Exception as e:
                raise RuntimeError(f"Failed to save encrypted profile data: {e}")

        return user
