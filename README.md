<div align="center">

# 🌿 BioProductos DK

### Plataforma web para la formulación y comercialización de bioproductos sustentables

*Biotecnología · Nanotecnología verde · Economía circular*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST_API-A30000?style=for-the-badge&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-Caja_Blanca_%2B_Negra-success?style=for-the-badge&logo=checkmarx&logoColor=white)

</div>

---

## 📖 Descripción

**`django-bioproductosdk`** es la plataforma web de **BioProductos DK SpA**, empresa dedicada a la formulación y comercialización de productos de **limpieza y cuidado personal sustentables**. El sistema integra una tienda en línea completa, páginas institucionales, gestión de usuarios y una **API REST** para consumo externo.

---

## ✨ Características principales

| Módulo | Descripción |
|---|---|
| 🛍️ **Catálogo y tienda** (`online/`) | Productos destacados, filtrado por categorías, búsqueda, detalle con productos relacionados y carga inicial con el comando `cargar_productos`. |
| 🏢 **Páginas institucionales** | Inicio, Nosotros, Ciencia, Colaboradores y formulario de Contacto. |
| 👤 **Usuarios y perfiles** | Registro, login/logout, visualización y edición de perfil (`Perfil` con datos de contacto y dirección de despacho). |
| 🛒 **Carrito y compra** | Carrito con soporte de sesión y **fusión al autenticarse**, resumen con impuestos y despacho, checkout y confirmación. |
| 🔌 **API REST** | Endpoints de productos, categorías, colaboradores, autenticación/registro, perfil y carrito. |
| 🧪 **Pruebas automatizadas** | Suite organizada en pruebas de **caja blanca** y **caja negra**. |

---

## 🛠️ Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend** | Python, Django, Django REST Framework |
| **Frontend** | Plantillas Django (MVT), HTML5, CSS3 |
| **Base de datos** | SQLite (desarrollo) |
| **Medios** | Django `MEDIA` para imágenes de productos |
| **Testing** | Django Test Framework (`manage.py test`) |
| **Arquitectura** | MVT + API REST |



---

## 📂 Estructura del proyecto

```
django-bioproductosdk/
├── 📁 bioproductosdk/          # Configuración principal del proyecto Django
├── 📁 media/                   # Archivos multimedia cargados (ej. media/productos/)
├── 📁 online/                  # Aplicación principal (MVT + API + pruebas)
│   ├── 📁 management/commands/ # Comandos personalizados (cargar_productos.py)
│   ├── 📁 migrations/          # Migraciones de base de datos
│   ├── 📁 static/              # Hojas de estilo CSS e imágenes estáticas
│   ├── 📁 templates/           # Plantillas HTML
│   ├── 📁 tests/               # Pruebas de caja blanca y caja negra
│   ├── 📄 api_views.py         # Vistas de la API REST
│   └── 📄 serializers.py       # Serializadores DRF
├── 📁 recursos/                # Recursos de apoyo e imágenes de referencia
├── 📄 manage.py                # Utilidad de administración de Django
└── 📄 requirements.txt         # Dependencias del proyecto
```

---

## 🚀 Puesta en marcha local

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/django-bioproductosdk.git
cd django-bioproductosdk
```

### 2️⃣ Crear y activar un entorno virtual

```bash
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Migrar la base de datos y cargar productos iniciales

```bash
python manage.py migrate
python manage.py cargar_productos
```

### 5️⃣ Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

🌐 Abre tu navegador en **http://127.0.0.1:8000/**

---

## 🧪 Ejecutar pruebas

```bash
python manage.py test online
```

### Organización de la suite

| Tipo | Archivos | Enfoque |
|---|---|---|
| ⚪ **Caja blanca** | `test_modelos.py`, `test_helpers_vistas.py` | Lógica interna: modelos y funciones auxiliares |
| ⚫ **Caja negra** | `test_api.py`, `test_carrito.py`, `test_catalogo.py`, `test_paginas.py`, `test_usuarios.py` | Comportamiento externo: API, carrito, catálogo, páginas y usuarios |

---

## 🔌 API REST

La API expone recursos para:

- 📦 Productos y categorías
- 🤝 Colaboradores
- 🔐 Autenticación y registro
- 👤 Perfil de usuario
- 🛒 Carrito de compras



---

## 🌱 Sobre BioProductos DK

BioProductos DK SpA desarrolla soluciones sustentables basadas en:

- 🧬 **Biotecnología**
- 🔬 **Nanotecnología verde**
- ♻️ **Economía circular**

---
## Integrantes
- **Adrieel Rubilar**
- **Jared Briones**
- **Fabian Nuñez**
- **Alejandra Guajardo**


---

<div align="center">

Hecho con 💚 y Django para un futuro más sustentable

</div>
