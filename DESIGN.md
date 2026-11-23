---
version: alpha
name: "Gestión de incidencias"
description: "Mesa de trabajo compacta para registrar y seguir incidencias."
typography:
  font-family: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
colors:
  primary: "#173B47"
  accent: "#E17B44"
  background: "#EFF3F2"
  surface: "#FFFFFF"
  text: "#173139"
  muted: "#5E7074"
  border: "#D7E1DF"
  danger: "#A64036"
  success: "#2F7056"
rounded:
  DEFAULT: "0.75rem"
  sm: "0.45rem"
  md: "0.75rem"
  lg: "1rem"
spacing:
  section-gap: "1.5rem"
  page-max: "76rem"
components:
  button: {}
  panel: {}
  form-field: {}
  incident-card: {}
---

# Gestión de incidencias — sistema visual

## Overview

### Creative North Star

Una mesa de operaciones pequeña y legible: registros claros, marcas de prioridad con significado y controles de herramienta, no de página promocional.

### Product context and register

- **Audience and primary job:** persona que registra y sigue incidencias propias en un portfolio cloud junior.
- **Target market(s) and evidence:** interfaz en español; el contexto del proyecto está en castellano.
- **Locale(s) and language policy:** español de España (es-ES), sin selector de idioma.
- **Usage scene:** navegador de escritorio y móvil, consultas breves y cambios de estado puntuales.
- **Register:** producto de una sola página.
- **Memorable signature:** banda lateral de color por prioridad, siempre acompañada de su etiqueta textual.
- **Restraint:** legibilidad, etiquetas explícitas y controles nativos.
- **Anti-references:** gradientes decorativos, estados comunicados solo con color y ventanas modales para tareas simples.
- **Token ownership/runtime mapping:** las variables CSS de frontend/index.html son fuente de ejecución; este archivo documenta sus valores semánticos.

## Colors

Azul petróleo #173B47 estructura el encabezado y las acciones; naranja #E17B44 resalta la acción principal y prioridad alta. Fondo #EFF3F2, superficies blancas, texto #173139, secundario #5E7074 y borde #D7E1DF separan grupos. Error #A64036 y éxito #2F7056 se acompañan de texto visible. En alto contraste se conservan el foco y los controles del sistema.

## Typography

La interfaz usa la pila de sistema sin descargar fuentes. Los encabezados y controles usan system-ui; las fechas usan una pila monoespaciada. Se conserva un cuerpo legible y una jerarquía clara de etiquetas.

## Layout

La página tiene cabecera, introducción y dos paneles: formulario y lista. En escritorio, el formulario ocupa la columna menor; a menos de 940px los paneles se apilan y a menos de 620px también se apilan cabecera y tarjetas. Ancho máximo 76rem; scroll natural y reflujo en móvil.

## Elevation & Depth

Las superficies se separan con borde fino y sombra discreta. No hay fondos difuminados ni elevación en campos. En alto contraste, el borde del sistema y el foco sustituyen diferencias sutiles.

## Shapes

Paneles con radio de 1rem, controles de 0.45rem y etiquetas redondeadas. La banda de prioridad es estrecha y nunca sustituye el nombre textual.

## Components

### Foundational visual states

Los controles tienen estados normal, hover, foco visible, pulsado, deshabilitado y ocupado. Los errores aparecen junto al campo o acción. La carga conserva los datos mostrados hasta recibir una respuesta válida.

### Buttons and actions

El botón sólido azul petróleo es la acción principal; acciones secundarias tienen borde y fondo blanco. Durante una escritura el botón se deshabilita y anuncia estado ocupado.

### Navigation and data display

La navegación se limita al encabezado de sesión. Las incidencias se muestran como lista semántica adaptable y ordenada por fecha descendente. Cada ficha incluye título, descripción, fecha, estado y controles.

### Forms and overlays

El formulario usa etiquetas visibles y controles nativos. La prioridad usa un select nativo. La validación es propia y asocia cada error al campo. No se usan diálogos ni se guardan tokens en almacenamiento persistente.

### Iconography

No hay librería de iconos. La marca de cabecera es un motivo CSS; los botones conservan texto visible.

### Motion

Los cambios duran 140ms; no hay animaciones de carga. Movimiento reducido desactiva el desplazamiento suave y reduce transiciones.

### Content and data visualization

El tono es directo. Los estados son Abierta, En curso y Cerrada; las prioridades son Baja, Media y Alta. Las fechas se formatean en es-ES. Los errores orientan sin exponer mensajes internos.

## Do's and Don'ts

- **Do:** combina color con etiqueta textual para comunicar prioridad y estado.
- **Do:** conserva el texto escrito si una creación falla.
- **Don't:** representa un error solo con color o interpreta datos del usuario como HTML.
- **Don't:** persiste el JWT en localStorage ni llames a la API sin sesión autenticada.
