import os
import zipfile
import shutil
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = "1bV0oOqbcMOPoO0HN83WwoYvgxzxSOEke"
ZIP_NAME = "dataset.zip"

# ---------------- AUTH ----------------
def authenticate():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials/client_credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

# ---------------- DOWNLOAD ZIP ----------------
def download_zip(service):
    results = service.files().list(
        q=f"name='{ZIP_NAME}' and '{FOLDER_ID}' in parents",
        fields="files(id, name)"
    ).execute()

    files = results.get('files', [])
    if not files:
        print("❌ dataset.zip not found")
        return None

    file_id = files[0]['id']

    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(ZIP_NAME, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    print("Downloaded dataset.zip")
    return ZIP_NAME

# ---------------- UNZIP ----------------
def unzip_file(zip_path, extract_to="dataset"):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Unzipped")

# ---------------- MERGE ----------------
def merge_folders():
    test_path = "test"
    dataset_path = "dataset"

    for category in ["car", "unknown"]:
        src = os.path.join(test_path, category)
        dst = os.path.join(dataset_path, category)

        if not os.path.exists(src):
            continue

        os.makedirs(dst, exist_ok=True)

        for file in os.listdir(src):
            shutil.copy(
                os.path.join(src, file),
                os.path.join(dst, file)
            )

    print("✅ Merged test → dataset")

# ---------------- ZIP AGAIN ----------------
def zip_folder(folder_path, zip_name):
    shutil.make_archive(zip_name.replace(".zip", ""), 'zip', folder_path)
    print("Zipped updated dataset")

# ---------------- UPLOAD ----------------
def upload_zip(service, zip_name):
    file_metadata = {
        'name': "dataset_updated.zip",
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(zip_name, mimetype='application/zip',
    resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()

    print("Uploaded updated zip")
# ---------------- CLEANUP ----------------
def cleanup():
    if os.path.exists("token.json"):
        os.remove("token.json")
        print("token.json deleted")
    if os.path.exists("dataset"):
        shutil.rmtree("dataset")
        print(" dataset folder deleted")

    if os.path.exists("dataset.zip"):
        os.remove("dataset.zip")
        print("dataset.zip deleted")

    if os.path.exists("dataset_updated.zip"):
        os.remove("dataset_updated.zip")
        print("dataset_updated.zip deleted")
# ---------------- MAIN ----------------
if __name__ == "__main__":
    service = authenticate()

    zip_file = download_zip(service)

    if zip_file:
        unzip_file(zip_file)
        merge_folders()
        zip_folder("dataset", "dataset_updated.zip")
        upload_zip(service, "dataset_updated.zip")

    cleanup()