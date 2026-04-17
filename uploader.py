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

    if os.path.exists('credentials.json'):
        creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials/client_credentials.json', SCOPES)
        creds = flow.run_console()

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
    source_path = "Data"   
    dataset_path = "dataset"          
    if not os.path.exists(source_path):
        print("❌ No captured_images folder found")
        return

    # Loop through ALL categories dynamically
    for category in os.listdir(source_path):
        src = os.path.join(source_path, category)
        dst = os.path.join(dataset_path, category)

        # Skip if not a folder
        if not os.path.isdir(src):
            continue

        os.makedirs(dst, exist_ok=True)

        for file in os.listdir(src):
            src_file = os.path.join(src, file)
            dst_file = os.path.join(dst, file)

            # Avoid overwriting existing files
            if os.path.exists(dst_file):
                base, ext = os.path.splitext(file)
                new_name = f"{base}_new{ext}"
                dst_file = os.path.join(dst, new_name)

            shutil.copy(src_file, dst_file)
    shutil.rmtree(source_path)
    os.makedirs(source_path, exist_ok=True)

    print("✅ Raspberry Pi images merged into dataset")

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

#----------------- DELETE --------------------
def delete_old_zip(service):
    results = service.files().list(
        q=f"name='dataset_updated.zip' and '{FOLDER_ID}' in parents",
        fields="files(id)"
    ).execute()

    for file in results.get('files', []):
        service.files().delete(fileId=file['id']).execute()
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
        delete_old_zip(service)
        upload_zip(service, "dataset_updated.zip")

    cleanup()