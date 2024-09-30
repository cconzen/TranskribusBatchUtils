# Transkribus Batch Utils

This project provides Python scripts to interact with the [Transkribus REST API](https://readcoop.eu/transkribus/docu/rest-api/). 

## Features

- **Batch Upload**: Upload multiple documents and their PageXMLs to a specified Transkribus collection.
- **Batch Update**: Update PageXMLs/transcriptions of documents already in a Transkribus collection.
  
## Prerequisites

- Python 3.7+
- An active Transkribus account

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/cconzen/TranskribusBatchUtils.git
   cd TranskribusBatchUtils
   ```
2. Install required dependencies:
   
   ```
   pip install -r requirements.txt
   ```
3. Set up your Transkribus Log in credentials in an ```.env``` file:
   ```
   TRANSKRIBUS_USER=<user@email.com>
   TRANSKRIBUS_PASSWORD=<password>
   ```

# Usage
## Batch Upload Documents

To upload a directory of documents to a Transkribus collection, use the following command:

   ```
   python main.py upload <base_directory> <collection_id>
   ```

_<base_directory>_: The base directory that contains the documents.

_<collection_id>_: The Transkribus collection ID to which you want to upload the documents.

## Batch Update Documents

To update the PageXMLs of all documents in a Transkribus collection, use:

   ```
  python main.py update <base_directory> <collection_id>
   ```

_<base_directory>_: The base directory that contains the documents.

_<collection_id>_: The Transkribus collection ID to which you want to upload the documents.

## Example Command

   ```
   python main.py upload documents 12345
   ```

This will upload the contents of the ```documents``` directory to the collection with ID 12345.

## Example Directory Structure

Make sure your base directory follows this structure for the script to work properly:

(metadata.xml is only required for updating existing Transkribus documents; it should be automatically created when exporting from Transkribus)

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
        ...
    ```

# License
This project is licensed under the MIT License.
