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
- Tras cada subida de la web, invalidar /* en CloudFront. Si no, el navegador o la caché pueden seguir mostrando la versión anterior; podria solucionarse eliminando caché de CLoudfront, pero en un entorno real quizá sea poco práctico. 

## Fase 2: autenticación

- Grupo de usuarios de Cognito en eu-west-1, con plan Básico.
- Inicio de sesión por correo electrónico, con autorregistro y verificación por correo.
- Cliente de aplicación sin secreto, porque la web se ejecuta en el navegador.
- Flujo de concesión de código de autorización, con los ámbitos OpenID, correo electrónico y perfil.
- Prueba: registro e inicio de sesión completados, con redirección a CloudFront.
- Mejoras posibles: activar MFA y limitar el registro si la aplicación fuera de uso real, por ejemplo, para que solo se puedan registrar personas de una organizacion con un correo especifico.

- ## Fase 3: datos

- Clave KMS gestionada por el cliente, con alias incidencias-dynamo. Cifra la tabla. Cuesta alrededor de 1 $ al mes.
- Tabla incidencias en eu-west-1: clave de partición userId, clave de orden incidentId, modo on-demand y cifrado con KMS.
- Aislamiento por usuario: no se controla con IAM, porque IAM no conoce qué usuario de Cognito hace cada petición. Lo hará el código de la Lambda, comprobando el userId del token, en la fase 4.

-**## Fase 4: API y funciones** 

- API HTTP con autorizador JWT de Cognito, que valida el ID token.
- Rutas: POST /incidencias para crear, GET /incidencias para listar y PATCH /incidencias/{incidentId} para cambiar el estado. Las tres exigen token.
- Funciones Lambda con rol y permisos mínimos:
  - crear-incidencia: escribir en la tabla y usar la clave KMS.
  - listar-incidencias: consultar la tabla y descifrar con la clave KMS.
  - cambiar-estado: actualizar filas de la tabla y usar la clave KMS. Solo modifica incidencias que existan para el usuario del token.
- Sin token, la API responde 401 antes de llegar al código de las funciones.
- CORS limitado al origen de CloudFront.
- Pruebas: sin token, 401. Con token válido, crear devuelve 201, listar devuelve solo las incidencias del usuario y cambiar estado devuelve 200. 
