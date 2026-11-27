from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil


class RegistroForm(UserCreationForm):
    """Formulario de registro de clientes con correo único y creación de perfil."""

    first_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: Camila Soto',
            'class': 'input-formulario',
            'autocomplete': 'name',
        }),
        error_messages={
            'required': 'Ingresa tu nombre completo.',
        },
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@correo.cl',
            'class': 'input-formulario',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.',
        },
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Ej: camilasoto',
            'class': 'input-formulario',
            'autocomplete': 'username',
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'input-formulario',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Repite tu contraseña',
            'class': 'input-formulario',
            'autocomplete': 'new-password',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta registrada con este correo electrónico.')
        return email

    def clean_first_name(self):
        nombre = self.cleaned_data.get('first_name', '').strip()
        if not nombre:
            raise forms.ValidationError('Ingresa tu nombre completo.')
        return nombre

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data['first_name']
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
            Perfil.objects.get_or_create(usuario=usuario)
        return usuario


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión con mensajes y placeholders en español (es-cl)."""

    error_messages = {
        'invalid_login': 'Usuario o contraseña incorrectos. Verifica tus datos e intenta nuevamente.',
        'inactive': 'Esta cuenta está inactiva.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Tu nombre de usuario',
            'class': 'input-formulario',
            'autocomplete': 'username',
        })
        self.fields['password'].label = 'Contraseña'
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Tu contraseña',
            'class': 'input-formulario',
            'autocomplete': 'current-password',
        })


class UsuarioUpdateForm(forms.ModelForm):
    """Formulario para actualizar nombre completo y correo electrónico del usuario."""

    first_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre completo',
            'class': 'input-formulario',
        }),
        error_messages={'required': 'El nombre completo es obligatorio.'},
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@correo.cl',
            'class': 'input-formulario',
        }),
        error_messages={
            'required': 'El correo electrónico es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.',
        },
    )

    class Meta:
        model = User
        fields = ('first_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este correo electrónico ya está siendo usado por otra cuenta.')
        return email


class PerfilForm(forms.ModelForm):
    """Formulario para actualizar los datos de contacto y despacho del perfil."""

    class Meta:
        model = Perfil
        fields = ('telefono', 'direccion', 'comuna', 'region')
        labels = {
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'comuna': 'Comuna',
            'region': 'Región',
        }
        widgets = {
            'telefono': forms.TextInput(attrs={
                'placeholder': '+56 9 0000 0000',
                'class': 'input-formulario',
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Calle, número, depto.',
                'class': 'input-formulario',
            }),
            'comuna': forms.TextInput(attrs={
                'placeholder': 'Ej: Providencia',
                'class': 'input-formulario',
            }),
            'region': forms.TextInput(attrs={
                'placeholder': 'Ej: Región Metropolitana',
                'class': 'input-formulario',
            }),
        }


class ContactoForm(forms.Form):
    """Formulario de contacto para clientes, biodistribuidores, maquila e I+D+i."""

    TIPOS_CONSULTA = [
        ('B2C / Cliente', 'B2C / Cliente'),
        ('Biodistribuidor DK', 'Biodistribuidor DK'),
        ('Maquila ISP', 'Maquila ISP'),
        ('I+D+i / Empresa', 'I+D+i / Empresa'),
    ]

    nombre = forms.CharField(
        label='Nombre',
        max_length=120,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre completo',
            'class': 'input-formulario',
        }),
        error_messages={'required': 'Por favor ingresa tu nombre.'},
    )
    correo = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@correo.cl',
            'class': 'input-formulario',
        }),
        error_messages={
            'required': 'Por favor ingresa tu correo electrónico.',
            'invalid': 'Ingresa un correo electrónico válido.',
        },
    )
    telefono = forms.CharField(
        label='Teléfono (opcional)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '+56 9 0000 0000',
            'class': 'input-formulario',
        }),
    )
    tipo_consulta = forms.ChoiceField(
        label='Tipo de consulta',
        choices=TIPOS_CONSULTA,
        required=True,
        widget=forms.Select(attrs={
            'class': 'input-formulario',
        }),
    )
    mensaje = forms.CharField(
        label='Mensaje',
        required=True,
        widget=forms.Textarea(attrs={
            'placeholder': 'Cuéntanos en qué podemos ayudarte',
            'class': 'input-formulario',
            'rows': 5,
        }),
        error_messages={'required': 'Por favor escribe tu mensaje.'},
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('Por favor ingresa tu nombre.')
        return nombre

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if not mensaje:
            raise forms.ValidationError('Por favor escribe tu mensaje.')
        return mensaje
