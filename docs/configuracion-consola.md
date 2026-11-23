# Configuración en AWS

## Fase de preparación
- Región de trabajo: eu-west-1.
- Acceso a la CLI con `aws login` y un usuario IAM.
- Presupuestos mensuales de 1 $ y 10 $, con aviso por correo.
- Alertas de uso del nivel gratuito activadas.

## Fase 1: frontend
- Bucket S3: `incidencias-frontend-d13guito04`, en eu-west-1.
- Acceso público bloqueado.
- Archivo publicado: `frontend/index.html`.
- Distribución de CloudFront con el bucket como origen y control de acceso OAC.
- Política del bucket: permite leer los archivos solo a CloudFront.
- Viewer protocol policy: redirección de HTTP a HTTPS.
- Default root object: `index.html`.
- Prueba: la web carga por HTTPS y el acceso directo al bucket devuelve `AccessDenied`.
- Después de cada subida de `index.html`, crear una invalidación `/*` en CloudFront. La caché activa puede mostrar una versión anterior hasta que se invalide.

## Fase 2: autenticación
- Grupo de usuarios de Cognito en eu-west-1, con plan Básico.
- Inicio de sesión por correo electrónico, con autorregistro y verificación por correo.
- Cliente de aplicación sin secreto, porque la web se ejecuta en el navegador.
- Flujo de código de autorización con PKCE y ámbitos `openid` y `email`.
- La página valida el parámetro `state` al volver de Cognito. Los tokens permanecen en memoria y no se guardan en `localStorage`.
- Prueba: registro e inicio de sesión completados con redirección a CloudFront.
- Cerrar sesión en la página borra los tokens locales; no revoca la sesión de Cognito.
- Mejoras posibles si la aplicación fuera de uso real: activar MFA y limitar el autorregistro.

## Fase 3: datos
- Clave KMS gestionada por el cliente, con alias `incidencias-dynamo`. Cifra la tabla y cuesta alrededor de 1 $ al mes.
- Tabla `incidencias` en eu-west-1: clave de partición `userId`, clave de orden `incidentId`, modo on-demand y cifrado con KMS.
- Aislamiento por usuario: IAM no conoce qué usuario de Cognito hace cada petición; lo aplica la Lambda comprobando el `userId` del token.
- Se eliminaron las dos filas de prueba. Se conservó la incidencia real del usuario.

## Fase 4: API y funciones
- API HTTP con autorizador JWT de Cognito, que valida el ID token.
- Rutas: `POST /incidencias` para crear, `GET /incidencias` para listar y `PATCH /incidencias/{incidentId}` para cambiar el estado. Las tres exigen token.
- Funciones Lambda con rol y permisos mínimos:
  - `crear-incidencia`: escribir en la tabla y usar la clave KMS.
  - `listar-incidencias`: consultar la tabla y descifrar con la clave KMS.
  - `cambiar-estado`: actualizar filas de la tabla y usar la clave KMS. Solo modifica incidencias que existan para el usuario del token.
- El código de las tres funciones está guardado en el repositorio, en `lambdas/<nombre>/lambda_function.py`.
- El frontend llama a la API para crear, listar y cambiar estados. Maneja la caducidad de sesión (`401`) y las incidencias inexistentes (`404`).
- CORS limitado al origen de CloudFront.
- Pruebas: sin token, la API responde `401`; con token válido, crear devuelve `201` y listar devuelve solo las incidencias del usuario.
- Prueba real de PATCH: el cambio de estado de una incidencia temporal mostró «Estado actualizado». La fila temporal se eliminó al terminar; la incidencia real se conservó.
- Publicación: se subió `frontend/index.html` a S3, se invalidó `/*` en CloudFront y la URL pública respondió `HTTP 200`.

## Fase 5: procesamiento asíncrono (código preparado; AWS pendiente)
- El enunciado pide que cada alta genere una notificación o registro de auditoría, con reintentos y una DLQ después de tres recepciones.
- El commit de preparación está en GitHub. `crear-incidencia` guarda la incidencia y después envía a SQS un evento `INCIDENT_CREATED` con `eventId`, `userId`, `incidentId` y fecha.
- La nueva Lambda `procesar-notificacion` escribe un registro idempotente por `eventId` en la tabla de auditoría. Su código está en `lambdas/procesar-notificacion/lambda_function.py`.
- Nombres previstos: cola `incidencias-notificaciones`, DLQ `incidencias-notificaciones-dlq` y tabla de auditoría `incidencias-auditoria`. Estos recursos todavía no existen en AWS.
- Aún falta crear la DLQ y la cola con `maxReceiveCount=3`, crear la tabla cifrada con la clave KMS, crear el rol de la Lambda procesadora, conectar la cola como trigger, conceder `sqs:SendMessage` a `crear-incidencia`, configurar `NOTIFICATION_QUEUE_URL` y `AUDIT_TABLE_NAME`, y desplegar el código en AWS.
- `FORCE_EXCEPTION` queda desactivado por defecto; se usará temporalmente en la fase de pruebas de fallo y se dejará en `false` al terminar.
