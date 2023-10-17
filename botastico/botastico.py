import requests
import os
import mimetypes
import logging
import httpx
import asyncio

class Botastico:
    def __init__(self, api_key, base_url, agent_id):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {api_key}'}
        self.agent_id = agent_id

    async def upload_file(self, file_path, file_name, file_type):
        MAX_RETRIES = 3
        TIMEOUT = 10  # Timeout in seconds
        for attempt in range(MAX_RETRIES):
            try:
                with open(file_path, 'rb') as f:
                    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                        upload_response = await client.post(
                            f'{self.base_url}/v1/agents/{self.agent_id}/kb/file',
                            files={'file': (file_name, f, file_type)},
                            headers=self.headers
                        )
                response_json = upload_response.json()
                kbdoc_id = response_json.get('kbdoc_id', None)  # get kbdoc_id from response

                # If server-side error related to postgresql, retry
                if upload_response.status_code == 500 and 'psycopg2.OperationalError' in upload_response.json().get('message'):
                    if attempt < MAX_RETRIES - 1:
                        logging.error(f"File upload failed due to database connection issue. Retrying... Error: {upload_response.json().get('message')}")
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
                        continue

                return {'status_code': upload_response.status_code, 'file_name': file_name, 'kbdoc_id': kbdoc_id, 'message': None}

            except httpx.RequestError as e:
                error_message = str(e)
                if 'remaining connection slots' in error_message or 'too many clients already' in error_message:
                    if attempt < MAX_RETRIES - 1:
                        logging.error(f"File upload failed due to database connection issue. Retrying... Error: {error_message}")
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
                        continue
                else:
                    logging.error(f"File upload failed after {MAX_RETRIES} attempts. Moving on to next file. Error: {error_message}")
                return {'status_code': None, 'file_name': file_name, 'kbdoc_id': None, 'message': error_message}
            except Exception as e:
                logging.error(f'Error occurred while uploading file: {file_name}. Error: {str(e)}')
                return {'status_code': None, 'file_name': file_name, 'kbdoc_id': None, 'message': str(e)}

    async def upload_folder(self, folder_path, max_concurrent_tasks=100):
        if not os.path.exists(folder_path):
            logging.error(f'Folder path: {folder_path} does not exist.')
            return

        semaphore = asyncio.Semaphore(max_concurrent_tasks)  # Change this to the maximum number of concurrent tasks you want to allow

        async def upload_with_semaphore(file_path, file_name, file_type):
            async with semaphore:
                return await self.upload_file(file_path, file_name, file_type)

        results = []
        tasks = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == ".DS_Store":
                    continue  # Skip .DS_Store files
                file_path = os.path.join(root, file)
                # Flattening the file path to use it as the filename
                file_name = os.path.relpath(file_path, folder_path).replace(os.path.sep, '_')
                file_type = mimetypes.guess_type(file_path)[0] or 'text/plain'  # Infer file type

                task = asyncio.ensure_future(upload_with_semaphore(file_path, file_name, file_type))
                tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response is not None:
                results.append(response) 
        return results

    def count_uploadable_files(self, folder_path):
        if not os.path.exists(folder_path):
            logging.error(f'Folder path: {folder_path} does not exist.')
            return 0  # Return 0 if the folder doesn't exist

        uploadable_file_count = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == ".DS_Store":
                    continue  # Skip .DS_Store files
                uploadable_file_count += 1

        return uploadable_file_count
    
    def get_uploadable_files(self, folder_path):
        if not os.path.exists(folder_path):
            logging.error(f'Folder path: {folder_path} does not exist.')
            return {}  # Return empty dictionary if the folder doesn't exist

        uploadable_files_dict = {}
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file == ".DS_Store":
                    continue  # Skip .DS_Store files
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)
                uploadable_files_dict[file_path] = file_name

        return uploadable_files_dict

    def extract_kbdoc_ids(self):
        list_response = requests.get(f'{self.base_url}/v1/agents?agent_ids={self.agent_id}', headers=self.headers)
        agent = list_response.json()
        kbdoc_ids = [file['kbdoc_id'] for dictionary in agent for file in dictionary['files'] if 'kbdoc_id' in file]
        return kbdoc_ids

    async def delete_agent_kbdocs(self):
        kbdoc_ids = self.extract_kbdoc_ids()
        MAX_RETRIES = 3
        async with httpx.AsyncClient() as client:
            for kbdoc_id in kbdoc_ids:
                for attempt in range(MAX_RETRIES):
                    try:
                        response = await client.delete(f'{self.base_url}/v1/agents/{self.agent_id}/kb/{kbdoc_id}', headers=self.headers)
                        response.raise_for_status()  # this will raise an exception for 4xx and 5xx status codes
                        break  # if the delete request was successful, we break the loop and don't retry
                    except httpx.HTTPStatusError as e:
                        if attempt < MAX_RETRIES - 1:  # if this wasn't the last attempt
                            logging.error(f'Failed to delete KB doc with id: {kbdoc_id}. Retrying... Error: {str(e)}')
                            continue
                        else:  # if it was the last attempt
                            logging.error(f'Failed to delete KB doc with id: {kbdoc_id} after {MAX_RETRIES} attempts. Error: {str(e)}')
                    except Exception as e:
                        logging.error(f'An error occurred during deletion of KB doc with id: {kbdoc_id}. Error: {str(e)}')

