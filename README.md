# Limpiador-de-Correos-Gmail
Este script autentica al usuario en Gmail mediante OAuth 2.0, busca todos los correos que no son importantes ni destacados, y los elimina. Usa la API de Gmail para listar y eliminar correos de manera segura, manejando la autenticación y paginación para procesar todos los correos, no solo los primeros 50.


# Script para limpiar correos en Gmail

Este script se conecta a Gmail a través de la API de Gmail para eliminar automáticamente los correos electrónicos que **no son importantes** y **no están destacados**. Se puede personalizar para eliminar correos no leídos o leídos según las preferencias del usuario.

## ¿Cómo funciona?

El script:
1. Autentica al usuario mediante OAuth 2.0 utilizando la API de Gmail.
2. Busca correos que no son importantes y no están destacados (tanto leídos como no leídos).
3. Elimina los correos en lotes (se maneja la paginación) hasta que todos los correos que coincidan con los criterios sean eliminados.

## Requisitos previos

- Python 3.x instalado en tu sistema.
- Gmail API habilitada en tu proyecto de Google Cloud.
- Archivo `client_secret.json` con las credenciales de Google Cloud.
- Las siguientes bibliotecas de Python instaladas:
    - `google-api-python-client`
    - `google-auth-httplib2`
    - `google-auth-oauthlib`

Puedes instalar las bibliotecas necesarias ejecutando el siguiente comando:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Cómo habilitar la API de Gmail en Google Cloud

### Paso 1: Crear un proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea un nuevo proyecto haciendo clic en el botón de menú y selecciona **Nuevo Proyecto**.
3. Asigna un nombre a tu proyecto (por ejemplo, `LimpiezaDeCorreosGmail`) y selecciona **Crear**.

### Paso 2: Habilitar la API de Gmail
1. Una vez creado el proyecto, dirígete a **APIs y servicios** > **Biblioteca**.
2. En la barra de búsqueda, busca "Gmail API" y selecciona la opción **Gmail API**.
3. Haz clic en el botón **Habilitar**.

### Paso 3: Crear credenciales de OAuth 2.0
1. Después de habilitar la API de Gmail, verás un botón que te sugiere crear credenciales. Haz clic en **Crear credenciales**.
2. Elige **API de Gmail** y selecciona **Datos del usuario** cuando se te pregunte qué tipo de datos quieres acceder.
3. Luego selecciona **Aplicación de escritorio** como tipo de aplicación.
4. Descarga el archivo `client_secret.json` generado.

### Paso 4: Configurar la pantalla de consentimiento OAuth
1. Antes de utilizar la API, debes configurar la pantalla de consentimiento OAuth. Ve a **Pantalla de consentimiento de OAuth** en la consola de Google Cloud.
2. Completa los campos obligatorios, como el nombre de la aplicación y la dirección de correo electrónico de soporte.
3. Agrega tu cuenta de correo electrónico como **usuario de prueba** para que solo tú puedas usar esta aplicación.

### Paso 5: Usar las credenciales en el script
1. Descarga el archivo `client_secret.json` y colócalo en la misma carpeta donde tienes tu script de Python.
2. Al ejecutar el script por primera vez, se te pedirá que inicies sesión y otorgues los permisos necesarios para acceder a tu cuenta de Gmail.

## Explicación del script

```python
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
```

- **Importaciones**: 
  - `os.path`: Maneja las rutas de archivos.
  - `pickle`: Se utiliza para guardar y cargar credenciales (`token.pickle`).
  - `google.auth.transport.requests.Request`: Maneja solicitudes HTTP para actualizar credenciales.
  - `google.oauth2.credentials.Credentials`: Administra las credenciales de OAuth 2.0.
  - `google_auth_oauthlib.flow.InstalledAppFlow`: Maneja el flujo de autenticación OAuth 2.0.
  - `googleapiclient.discovery.build`: Se utiliza para crear un cliente de la API de Gmail.

```python
# Scope que proporciona acceso completo a Gmail
SCOPES = ['https://mail.google.com/']
```

- **`SCOPES`**: Define los permisos necesarios para el script. `https://mail.google.com/` otorga acceso completo a la cuenta de Gmail (leer, modificar y eliminar correos).

```python
def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
```

- **Autenticación**:
  - La función comprueba si existen credenciales válidas guardadas en el archivo `token.pickle`. Si no, se activa el flujo de OAuth 2.0 y se guardan las credenciales para futuras ejecuciones.

```python
def delete_unread_non_important():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    query = "-is:important -is:starred"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    total_deleted = 0

    while 'nextPageToken' in results or messages:
        if messages:
            print(f'Se encontraron {len(messages)} correos para eliminar.')
            for message in messages:
                try:
                    service.users().messages().delete(userId='me', id=message['id']).execute()
                    total_deleted += 1
                    print(f'Correo {message["id"]} eliminado.')
                except Exception as e:
                    print(f'Error eliminando el correo {message["id"]}: {str(e)}')

        if 'nextPageToken' in results:
            results = service.users().messages().list(userId='me', q=query, pageToken=results['nextPageToken']).execute()
            messages = results.get('messages', [])
        else:
            break

    print(f'Se eliminaron un total de {total_deleted} correos.')
```

- **Eliminación de correos**:
  - Esta función construye un servicio de la API de Gmail y realiza una búsqueda utilizando la consulta `-is:important -is:starred`, que busca correos que no son ni importantes ni destacados.
  - Usa paginación (`nextPageToken`) para procesar los correos en lotes y los elimina uno por uno.

```python
if __name__ == '__main__':
    delete_unread_non_important()
```

- **Principal**:
  - Este es el punto de entrada del script. Cuando se ejecuta el script, llama a la función `delete_unread_non_important()`.

## Personalización

Puedes modificar este script según tus necesidades. Aquí te muestro algunas maneras en que puedes personalizarlo:

### 1. Eliminar solo correos no leídos
Para eliminar **solo correos no leídos** que no son importantes ni destacados, cambia la consulta a:

```python
query = "is:unread -is:important -is:starred"
```

Esto buscará correos que estén sin leer, que no sean importantes ni estén destacados.

### 2. Eliminar solo correos leídos
Para eliminar **solo correos leídos** que no son importantes ni destacados, modifica la consulta de la siguiente manera:

```python
query = "-is:unread -is:important -is:starred"
```

Esto buscará correos que hayan sido leídos y que no sean ni importantes ni destacados.

### 3. Eliminar correos importantes o destacados
Si deseas dirigirte a correos que sean importantes o estén destacados, cambia la consulta a:

```python
query = "is:important is:starred"
```

Esto eliminará correos que sean tanto importantes como destacados.

## Ejecución del script

1. Guarda el script como `delete_emails.py`.
2. Asegúrate de que el archivo `client_secret.json` esté en el mismo directorio.
3. Ejecuta el script:

```bash
python delete_emails.py
```

La primera vez que lo ejecutes, se abrirá una ventana del navegador para que inicies sesión y autorices la cuenta de Google.

## Conclusión

Este script es una manera sencilla de automatizar el proceso de limpieza de tu bandeja de entrada de Gmail basado en criterios personalizables. Puedes modificar la cadena de consulta para dirigirte a correos específicos y garantizar que tu bandeja de entrada se mantenga organizada.

Si tienes alguna pregunta o problema, ¡no dudes en ponerte en contacto!
