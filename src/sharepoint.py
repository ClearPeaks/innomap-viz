# import os
# import logging
# from io import BytesIO
# from urllib.parse import urlparse
#
# import requests
# from azure.identity import ClientSecretCredential
# from msgraph import GraphServiceClient
#
#
# class SharePoint:
#     """
#     Class to interact with SharePoint.
#     """
#
#     def __init__(self,
#                  hostname: str,
#                  site_name: str,
#                  client_id: str,
#                  client_secret: str,
#                  tenant_id: str) -> None:
#         self.hostname = hostname
#         self.site_name = site_name
#         # Initialize Microsoft Graph client
#         self.credentials = ClientSecretCredential(
#             tenant_id=tenant_id,
#             client_id=client_id,
#             client_secret=client_secret
#         )
#         scopes = ['https://graph.microsoft.com/.default']
#         self.graph_client = GraphServiceClient(self.credentials, scopes)
#         # Get SharePoint site id
#         self._acquire_access_token()
#         self.site_id = self._get_site_id()
#         self.synvert_drive_id = self._get_synvert_drive_id()
#
#     def _acquire_access_token(self) -> None:
#         """Generate a new access token for using """
#         scopes = ['https://graph.microsoft.com/.default']
#         logging.info("Generate SharePoint access token")
#         self.access_token = self.credentials.get_token(scopes[0]).token
#         logging.info("New access token acquired!")
#
#     def _make_msgraph_call(self, request_url: str) -> requests.Response:
#         """
#         Makes msgraph api call and checks for errors.
#         The request header is set using an access token, generated from the app registration credentials.
#         The access token is regenerated if expired.
#         :param request_url: msgraph url to perform the request call.
#         :return: request response object.
#         """
#         status_code = -1
#         attempt_count = 0
#         while status_code != 200:
#             attempt_count += 1
#             logging.info(f"Calling msgraph for SharePoint in url {request_url}. Attempt number {attempt_count}")
#             response = requests.get(request_url, headers={
#                 "Authorization": f"Bearer {self.access_token}",
#                 "Accept": "application/json",
#                 "Content-Type": "application/json"
#             }, timeout=60)
#             status_code = response.status_code
#
#             if attempt_count > 3:
#                 raise RuntimeError(
#                     f"SharePoint can't be accessed after {attempt_count} attempts. {status_code}: {response.text}")
#
#             if status_code == 401:
#                 logging.info("Token expired, generating new one.")
#                 self._acquire_access_token()
#             elif status_code == 302:
#                 logging.info("SharePoint Graph API request failed with 'Service Unavailable', retrying.")
#                 logging.debug(f"{status_code}: {response.text}")
#             elif status_code == 403:
#                 raise PermissionError(
#                     "Application credentials do not have sufficient privileges to access this resource"
#                     f"{status_code}: {response.text}"
#                 )
#             elif status_code == 404:
#                 # 404 NOT FOUND errors better handled outside this function
#                 logging.debug(f"Not found resource {request_url}")
#                 return response
#
#         return response
#
#     def _get_synvert_drive_id(self) -> str:
#         """
#         Retrieve drive id corresponding to the Synvert Shared Documents Drive using the SharePoint site name.
#         :return: drive id
#         """
#         url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives"
#         response = self._make_msgraph_call(url)
#         for drive in list(response.json().items())[1][1]:
#             if drive["name"] == "Synvert Shared Documents":
#                 return drive["id"]
#
#     def _get_site_id(self) -> str:
#         """
#         Retrieve site id using the SharePoint hostname and site name.
#         :return: site id
#         """
#         url = f"https://graph.microsoft.com/v1.0/sites/{self.hostname}:/{self.site_name}"
#         response = self._make_msgraph_call(url)
#         site_id = response.json()["id"]
#         logging.info(f"Retrieved site id '{site_id}' from host '{self.hostname}' and site '{self.site_name}'")
#         return site_id
#
#     def _get_file_content(self, url: str) -> bytes | None:
#         """
#         Read SharePoint file content as bytes from the given url.
#         :param relative_path: SharePoint file's url.
#         :return: content as bytes, or None if not found (or if the sharepoint drive isn't handled).
#         """
#
#         handled_drives = ["/Shared%20Documents/", "/Synvert%20Shared%20Documents/"]
#         if not any(drive in url for drive in handled_drives):
#             # If sharepoint drive is not handled, None is returned
#             return None
#
#         if f"https://{self.hostname}/Shared%20Documents/" in url:
#             relative_path = url.split(f"https://{self.hostname}/Shared%20Documents/")[1]
#             relative_path = relative_path.split('?')[0]
#             request_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drive/root:/{relative_path}:/content"
#
#         elif f"https://{self.hostname}/Synvert%20Shared%20Documents/" in url:
#             relative_path = url.split(f"https://{self.hostname}/Synvert%20Shared%20Documents/")[1]
#             relative_path = relative_path.split('?')[0]
#
#             request_url = (
#                 f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/drives/"
#                 f"{self.synvert_drive_id}/root:/{relative_path}:/content"
#             )
#
#         response = self._make_msgraph_call(request_url)
#         if response.status_code == 404:
#             # If not found return None
#             return None
#         # Return file content as bytes
#         return response.content
#
#     def download_xlsx(self, url: str, save_path: str) -> None:
#         """
#         Downloads an Excel (.xlsx) file from SharePoint using the given URL
#         and saves it to the specified local path.
#
#         :param url: The SharePoint file URL.
#         :param save_path: The local file path to save the downloaded file.
#         :raises FileNotFoundError: If the file does not exist at the given SharePoint URL.
#         :raises ValueError: If the file type is not .xlsx.
#         """
#         if not save_path.endswith(".xlsx"):
#             raise ValueError("Only .xlsx files are supported.")
#
#         logging.info(f"Attempting to download file from SharePoint: {url}")
#         file_bytes = self._get_file_content(url)
#
#         if file_bytes is None:
#             raise FileNotFoundError(f"File not found or unsupported drive in SharePoint URL: {url}")
#
#         dir_path = os.path.dirname(save_path)
#         if dir_path:
#             os.makedirs(dir_path, exist_ok=True)
#
#         with open(save_path, "wb") as f:
#             f.write(file_bytes)
#         logging.info(f"File successfully saved to: {save_path}")
