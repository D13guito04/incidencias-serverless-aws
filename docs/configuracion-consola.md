# Configuración en AWS

## Fase de Preparación
- Región de trabajo: eu-west-1.
- Acceso a la CLI con aws login y un usuario IAM.
- Presupuestos mensuales de 1 $ y 10 $, con aviso por correo.
- Alertas de uso del nivel gratuito activadas.

## Fase 1: frontend
- Bucket S3: incidencias-frontend-d13guito04, en eu-west-1.
- Acceso público bloqueado.
- Archivo subido: frontend/index.html.
- Distribución de CloudFront con el bucket como origen y control de acceso OAC.
- Política del bucket: permite leer los archivos solo a CloudFront.
- Viewer protocol policy: redirección de HTTP a HTTPS.
- Default root object: index.html.
- Prueba: la web carga por HTTPS y el acceso directo al bucket devuelve AccessDenied.

## Fase 2: autenticación

- Grupo de usuarios de Cognito en eu-west-1, con plan Básico.
- Inicio de sesión por correo electrónico, con autorregistro y verificación por correo.
- Cliente de aplicación sin secreto, porque la web se ejecuta en el navegador.
- Flujo de concesión de código de autorización, con los ámbitos OpenID, correo electrónico y perfil.
- Prueba: registro e inicio de sesión completados, con redirección a CloudFront.
