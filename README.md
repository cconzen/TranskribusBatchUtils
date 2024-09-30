# Transkribus PageXML Updater

This Python script automates the process of updating one or multiple documents in Transkribus by exchanging their PageXML files. 
It interacts with the Transkribus REST-API to log in, retrieve documents, and update the XML content of specific pages within a collection.

## Features

- Login to Transkribus: Authenticates using your Transkribus credentials to obtain a session ID.
- Fetch Full Document Metadata: Retrieves the full metadata for a document from Transkribus.
- Update Page XML: Updates individual PageXML files for each page in a document, allowing batch updates for multiple pages.
- Batch Processing: Loops through documents in a directory and updates the corresponding PageXML files based on metadata and document IDs.
  
## Requirements

- Python 3.x
- requests library

You can install the required libraries using:

```
pip install requests
```

Clone the repository:

```
git clone https://github.com/cconzen/TranskribusUpdatePageXML.git
```

### Edit the script:

Open the script and update the following placeholders with your actual Transkribus account details and document information:

- **collection_id**: The ID of the collection in Transkribus.
- **doc_id**: The document ID (if updating only one document).
- **username**: Your Transkribus account email.
- **password**: Your Transkribus account password.
- **status**: The status the document should be after you updated the XML (default: IN_PROGRESS).

### Set Base Directory:

Update the base_dir variable to point to the base directory where your XML and metadata files are stored locally.

### Run the script:

Use the following command to execute the script:

```
python transkribus_updater.py
```
The script will log in to Transkribus, fetch the document metadata, and update the corresponding PageXML files for each page based on the content of your local XML files.

### Script Details

**login_transkribus()**

Logs into the Transkribus API and retrieves a session ID.

**get_full_document()**

Fetches the full metadata of a document using the document ID.

**load_xml()**

Loads the content of a local XML file from a given path.

**update_page_xml()**

Updates the XML content of a specific page in Transkribus.

**batch_update_document_xmls()**

Batch processes all documents in the specified base directory, updating the PageXML for each page.

## Example Directory Structure
Make sure your base directory follows this structure for the script to work properly:

```
/BASE_DIR/
    /Document_1/
        metadata.xml
        /page/
            Page_1.xml
            Page_2.xml
    /Document_2/
        metadata.xml
        /page/
            Page_1.xml
            Page_2.xml
```

# License
This project is licensed under the MIT License.
