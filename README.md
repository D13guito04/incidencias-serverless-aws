# Incidencias serverless en AWS

Aplicación de gestión de incidencias desplegada con servicios serverless de AWS.

## Estado del proyecto

En desarrollo. Hasta ahora he completado:

- Web estática servida desde S3 con CloudFront por HTTPS, con el bucket privado mediante OAC.
- Autenticación con Cognito: registro con verificación por correo e inicio de sesión con PKCE, sin secreto de cliente.
- API con HTTP API y autorizador JWT de Cognito, y tres funciones Lambda para crear, listar y cambiar el estado de las incidencias.
- Datos en DynamoDB, cifrados con una clave KMS gestionada por el cliente.
- Aislamiento entre usuarios en el código de las funciones, a partir del identificador del token.

## Documentación

- [Configuración paso a paso en AWS](docs/configuracion-consola.md)
