import os
import requests
import xml.etree.ElementTree as ET
import argparse
import json
import re

from login import login_transkribus

fulldoc_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/{}/fulldoc'
update_page_xml_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/{}/{}/text'
all_docs_in_collection_url = 'https://transkribus.eu/TrpServer/rest/collections/{}/list'
create_upload_url = 'https://transkribus.eu/TrpServer/rest/uploads'

def get_full_document(session_id, collection_id, doc_id):

    headers = {'Cookie': f"JSESSIONID={session_id}"}
    response = requests.get(fulldoc_url.format(collection_id, doc_id), headers=headers)
   
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve document: {response.status_code} - {response.text}")

def load_xml(xml_path):

    if os.path.exists(xml_path):
        with open(xml_path, 'r', encoding='UTF-8') as xml_file:
            return xml_file.read()
    else:
        return None

def update_page_xml(session_id, collection_id, doc_id, page_nr, xml_content, status="IN_PROGRESS", overwrite=True):
    """Updates the XML for a specific page."""
    headers = {'Cookie': f"JSESSIONID={session_id}", 'Content-Type': 'application/xml'}
    params = {'status': status, 'overwrite': str(overwrite).lower()}  # true or false as lowercase string
    
    response = requests.post(update_page_xml_url.format(collection_id, doc_id, page_nr), headers=headers, params=params, data=xml_content)

    if response.status_code == 200:
        print(f"Page {page_nr} XML updated successfully.")
    else:
        print(xml_content)
        print(f"Failed to update XML for page {page_nr}: {response.status_code} - {response.text}")

def batch_update_document_xmls(base_dir, collection_id):
    """Updates the XML for multiple documents in a base directory."""
  
    session_id = login_transkribus()
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    response = requests.get(all_docs_in_collection_url.format(collection_id), headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve documents in collection: {response.status_code} - {response.text}")

    all_docs = response.json()
    
    for doc in all_docs:
        doc_id = doc['docId']
        doc_title = doc['title']
        metadata_file = os.path.join(base_dir, doc_title, "metadata.xml")
        
        if os.path.exists(metadata_file):
            tree = ET.parse(metadata_file)
            root = tree.getroot()
            
            metadata_doc_id = root.findtext('docId')
            
            if metadata_doc_id == str(doc_id):
                print(f"Updating document {doc_title} with ID {doc_id}")
                document = get_full_document(session_id, collection_id, doc_id)
                pages = document['pageList']['pages']
                
                for page in pages:
                    page_nr = page['pageNr']
                    page_filename = page['imgFileName']
                    xml_path = None
                    
                    for filename in os.listdir(os.path.join(base_dir, doc_title, "page")):
                        split_filename = os.path.splitext(filename)
                        original_filename = re.sub(r'^\d+_', '', split_filename[0])
                        online_filename = os.path.splitext(page_filename)[0]

                        if original_filename == online_filename and split_filename[1] == ".xml":
                            xml_path = os.path.join(base_dir, doc_title, "page", filename)

                    if xml_path:
                        xml_content = load_xml(xml_path)
                        if xml_content:
                            update_page_xml(session_id, collection_id, doc_id, page_nr, xml_content.encode("utf-8"), status="IN_PROGRESS", overwrite=True)
                        else:
                            print(f"Failed to load XML content for page {page_nr}.")
                    else:

                        print(f"No matching PageXML found for page {page_nr} in document {doc_title}.")
            else:
                print(f"Metadata docId {metadata_doc_id} does not match document {doc_id}. Skipping...")
        else:
            print(f"Could not find metadata.xml for document {doc_title}. Did you export the documents from Transkribus?")


### BATCH UPLOAD

def create_upload(session_id, collection_id, doc_name, pages):
    """
    Creates a new upload in the specified Transkribus collection.

    Args:
        session_id (str): The session ID from the login.
        collection_id (str): The ID of the collection to upload the document to.
        doc_name (str): The name of the document.
        pages (list): A list of pages (image files and metadata) to be uploaded.

    Returns:
        str: The ID of the created upload.

    Raises:
        Exception: If the upload creation fails, an exception is raised with the error details.
    """
    headers = {'Cookie': f"JSESSIONID={session_id}", 'Content-Type': 'application/json'}
    body = {
        "md": {
            "title": doc_name
        },
        "pageList": {"pages": pages}
    }

    response = requests.post(f'{create_upload_url}?collId={collection_id}', headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        upload_id = root.find('uploadId').text
        return upload_id
    else:
        raise Exception(f"Failed to create upload: {response.status_code}, {response.text}")

def upload_page(session_id, upload_id, page_data, image_path, xml_path=None):
    """
    Uploads a single page (image and optional XML metadata) to the created upload.

    Args:
        session_id (str): The session ID from the login.
        upload_id (str): The ID of the created upload.
        page_data (dict): Metadata about the page being uploaded, including the filename and page number.
        image_path (str): The path to the image file.
        xml_path (str, optional): The path to the XML file, if available.

    Raises:
        Exception: If the upload fails, an error message is printed.
    """
    headers = {'Cookie': f"JSESSIONID={session_id}"}
    files = {'img': (page_data['fileName'], open(image_path, 'rb'), 'application/octet-stream')}
    
    if xml_path and os.path.exists(xml_path):
        files['xml'] = (page_data['pageXmlName'], open(xml_path, 'rb'), 'application/octet-stream')
    else:
        print(f"XML file not found: {xml_path}")
        return

    response = requests.put(f'https://transkribus.eu/TrpServer/rest/uploads/{upload_id}', headers=headers, files=files)

    if response.status_code == 200:
        print(f"Page {page_data['pageNr']} uploaded successfully.")
    else:
        print(f"Failed to upload page {page_data['pageNr']}: {response.status_code}, {response.text}")

def process_directory(base_dir, collection_id):
    """
    Processes a directory of documents and uploads their pages to Transkribus.

    Args:
        base_dir (str): The base directory containing documents to be uploaded.

    Directory Structure:
        base_dir/
        └── document_name/
            ├── image1.jpg
            ├── image2.jpg
            └── page/
                ├── image1.xml
                └── image2.xml
    """
    for dirpath, _, filenames in os.walk(base_dir):
        if dirpath == base_dir:
            continue

        doc_name = os.path.basename(dirpath)
        if not doc_name == "page":
            print(f"Processing directory {doc_name}...")
        else:
            print("Skipping page directory...")

        pages = []

        # Sort filenames to ensure proper page order
        sorted_filenames = sorted((filename for filename in filenames if not filename.endswith('.done')))

        for filename in sorted_filenames:
            if filename.lower().endswith('.jpg'):
                base_filename = os.path.splitext(filename)[0]

                image_path = os.path.join(dirpath, filename)
                xml_path = os.path.join(dirpath, "page", f"{base_filename}.xml")

                page_data = {
                    "fileName": filename,
                    "pageNr": len(pages) + 1,
                    "pageXmlName": f"{base_filename}.xml"
                }
                pages.append(page_data)

        if pages:
            session_id = login_transkribus()
            upload_id = create_upload(session_id, collection_id, doc_name, pages)

            for page in pages:
                image_path = os.path.join(dirpath, page['fileName'])
                xml_path = os.path.join(dirpath, "page", page['pageXmlName'])
                upload_page(session_id, upload_id, page, image_path, xml_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Transkribus API Batch Utils")
    subparsers = parser.add_subparsers(dest='command', help='Commands: upload, update')

    upload_parser = subparsers.add_parser('upload', help='Batch upload all documents of a directory as a document in a collection')
    upload_parser.add_argument('base_dir', type=str, help='Base directory with document directories inside')
    upload_parser.add_argument('collection_id', type=str, help='Collection ID to add documents to')

    update_parser = subparsers.add_parser('update', help='Batch update all documents in a collection')
    update_parser.add_argument('base_dir', type=str, help='Base directory with document directories inside')
    update_parser.add_argument('collection_id', type=str, help='Collection ID to batch update')
    args = parser.parse_args()


    if args.command == 'upload':

        base_dir = args.base_dir
        collection_id = args.collection_id

        print(f"Uploading directory {base_dir} to Collection with ID {collection_id}...")

        process_directory(base_dir, collection_id)

        print(f"Done.")

    elif args.command == 'update':

        base_dir = args.base_dir
        collection_id = args.collection_id
        
        print(f"Using PageXMLs of {base_dir} to update Collection with ID {collection_id}...")

        batch_update_document_xmls(base_dir, collection_id)

        print(f"Done.")
        
