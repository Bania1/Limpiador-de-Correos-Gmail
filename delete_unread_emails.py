import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scope más amplio que da acceso completo a Gmail
SCOPES = ['https://mail.google.com/']

def authenticate_gmail():
    creds = None
    # El token.pickle almacena las credenciales de acceso del usuario
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Si no hay credenciales disponibles, pedirá autenticación
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar las credenciales para la próxima ejecución
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def delete_unread_non_important():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    # Consulta: correos no importantes, no destacados, leídos o no leídos
    query = "-is:important -is:starred"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    total_deleted = 0

    # Procesa todos los correos usando paginación
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

        # Si hay más correos en la siguiente página, obtener el siguiente lote
        if 'nextPageToken' in results:
            results = service.users().messages().list(userId='me', q=query, pageToken=results['nextPageToken']).execute()
            messages = results.get('messages', [])
        else:
            break

    print(f'Se eliminaron un total de {total_deleted} correos.')

if __name__ == '__main__':
    delete_unread_non_important()
