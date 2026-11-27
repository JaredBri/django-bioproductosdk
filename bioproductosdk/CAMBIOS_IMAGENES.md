# Cambios: integración del logo y banco de imágenes (24/11/2026)

## Imágenes agregadas en `online/static/images/`
Todas optimizadas para web (redimensionadas, JPG ~60–300 KB). Los nombres son los que ya esperaban los CSS, así que no hubo que cambiar rutas.

| Archivo | Dónde se ve |
|---|---|
| `logo.png` | Barra de navegación y pie de página (base.html) |
| `favicon.png` | Ícono de la pestaña del navegador |
| `heroPrincipal.jpg` | Banner de la página de inicio |
| `laboratorio.jpg` | Inicio (sección Ciencia) y Ciencia (I+D+i) |
| `nanotecnologia.jpg` | Ciencia (Nanotecnología verde) |
| `equipoTrabajo.jpg` | Nosotros (Nuestra historia) |
| `fundadoraSindy.jpg`, `fundadoraCarolina.jpg` | Inicio y Nosotros |
| `logoANID.jpg`, `logoCORFO.jpg` | Pie de página: "Proyecto apoyado por:" |
| `bioLogoNaturaleza.jpg` | Contacto (banner del encabezado) |
| `economiaCircular.jpg` | Ciencia (Economía circular) |
| `galeria/*.jpg` (8 fotos) | Galería "Nuestros productos" (Nosotros) y "Nuestro laboratorio" (Ciencia) |

## Fotos para los productos: `recursos/imagenes_productos/`
Fotos cuadradas listas para subir en el campo **imagen** de cada Producto desde `/admin/`
(detergentes, champú sólido, sales de baño). Al subirlas, Django las copia a `media/productos/`.

## Cambios en el código
- **base.html / base.css**: el logo ahora es una imagen real (antes era un cuadro amarillo con el logo de fondo). Se agregó el favicon.
- **views.py**: `inicio` ahora envía `productosDestacados` (productos con *destacado* = sí, máximo 4) y `colaboradores`; `colaboradores` envía la lista de colaboradores. Antes los templates los pedían pero la vista no los mandaba, por eso salían vacíos.
- **views.py**: `agregarCarrito(request, pk)` → `agregarCarrito(request, id)`, porque la ruta en urls.py es `<int:id>`. Con el nombre anterior, el botón "+" del inicio daba error.
- **index.html y detalleproducto.html**: la imagen del producto ahora usa `{{ producto.imagen.url }}` (igual que tienda.html). Antes buscaba en `static/images/` y la foto no aparecía, porque `imagen` es un ImageField que guarda en `media/productos/`.
- **404.html**: extendía `base.html`, que no existe; ahora extiende `componentes/base.html`.
- **admin.py**: se registró `Colaboradores` para editarlos desde el panel.
- **nosotros.html**: historia "Innovación & Sustentabilidad" (2020, fondo de innovación, nanoemulsiones), Misión y Visión oficiales, títulos de las fundadoras, logro 2020 y galería de productos.
- **ciencia.html**: texto de I+D+i, secciones nuevas "Hacer ciencia hoy" y "Economía circular", y galería del laboratorio.
- **colaboradores.html**: introducción de servicios para empresas y llamado "Vende Bioproductos DK" (biodistribuidores), con un botón que abre Contacto con la opción ya elegida.
- **contacto.html**: nueva opción "Quiero ser biodistribuidor DK" en el tipo de consulta (se marca sola si se llega desde ese botón, usando `?tipo=distribuidor`).
- **index.html**: mención a biodistribuidores en la sección final para empresas.
- **contacto.html / informacion.css**: imagen de marca en la columna derecha y estilos para el formulario, que antes se veía sin formato porque esos estilos estaban solo en cuenta.css.

## Para aplicar
```
python manage.py migrate
python manage.py runserver
```
Después, en `/admin/` → Productos: sube una foto de `recursos/imagenes_productos/` y marca **destacado** en los productos que quieran mostrar en el inicio.

## Ajustes de diseño (v3)
- Los CSS ahora se cargan con `?v=3` (ej. `informacion.css?v=3`). Así el navegador descarga la versión nueva y no usa una copia vieja guardada en caché. Si vuelven a cambiar un CSS, suban el número.
- Nosotros: la historia se muestra como línea de tiempo de 3 hitos; Misión y Visión muestran un resumen y el texto completo en "Leer … completa".
- Ciencia: "Hacer ciencia hoy" es un bloque verde con una cita y dos tarjetas; "Economía circular" muestra las 4 R y la explicación completa en un desplegable.

## Ajustes v4
- ANID y CORFO **no son colaboradores**: salieron de la página Colaboradores y del inicio, y ahora están en el pie de página de todas las páginas como "Proyecto apoyado por:", con enlace a sus sitios.
- Migraciones: la `0002` quedó vacía y la `0003` borra ANID y CORFO de la tabla de colaboradores, por si ya se habían creado. Corran `python manage.py migrate`.
- La sección "Colaboradores" del inicio solo aparece cuando hay colaboradores cargados en el admin.
- Contacto: la imagen del logo con vegetación ahora es un banner a la derecha del título "Hablemos", sin texto encima. En celular queda debajo del título.
- CSS en `?v=4`.
