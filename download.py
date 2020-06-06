import multiprocessing as mp
import requests, os, json, itertools
from getfilelistpy import getfilelist
from multiprocessing.dummy import Pool

def download_file(fileInfo, destination):
    id = fileInfo['id']
    name = fileInfo['name']
    destination = os.path.join(destination,name)
    if os.path.exists(destination):
        print("Already exists '"+destination+"'")
        return
    URL = "https://docs.google.com/uc?export=download"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36'
    }
    response = ""
    while True:
        try:
            session = requests.Session()
            response = session.get(URL, params = { 'id' : id }, stream = True)
            token = get_confirm_token(response)

            if token:
                params = { 'id' : id, 'confirm' : token }
                response = session.get(URL, params = params, stream = True)
            break
        except:
            continue
    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    print("Downloading '"+destination+"'")
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def refresh_download_list(ID):
    print("Fetching download list...")
    # using my API key
    # api_key = "AIzaSyCVfDC3KrWlV9d6fe5JMH9F6rgErX7CMOw"
    resource = {
        "drive_ipv4": "172.217.1.202",
        "api_key": "AIzaSyCVfDC3KrWlV9d6fe5JMH9F6rgErX7CMOw",
        "id": ID,
        "fields": "files(name,id)",
    }
    file_list = getfilelist.GetFileList(resource)
    with open ("file_list.json","w") as f:
        f.write(json.dumps(file_list, sort_keys=True, indent=4))


def folder_tree_map(file_list):
    folder_id_name_map = {}
    folderID = file_list["folderTree"]["folders"]
    folderNames = file_list["folderTree"]["names"]
    for ID,name in zip(folderID,folderNames):
        folder_id_name_map.update({ID:name})
    return folder_id_name_map

def stage_all_download(file_list,folder_id_name_map):
    folderList = file_list["fileList"]
    # print(len(folderList))
    for folder in folderList:
    # folder = folderList[6]
        if(len(folder["files"])):
            # replace folderID with folder_name
            for i,folderTree in enumerate(folder["folderTree"]):
                folder["folderTree"][i] = folder_id_name_map[folder["folderTree"][i]]
            folderPath = os.path.join(*folder["folderTree"])
            os.makedirs(folderPath, exist_ok = True)
            download_folder(folder,folderPath)

def download_folder(folder,folderPath):
    ## with multiprocessing
    # with Pool(processes=2*mp.cpu_count()) as pool:
    #     pool.starmap(download_file, zip(folder['files'], itertools.repeat(folderPath)))
    ## without multiprocessing
    for fileInfo in folder['files']:
        download_file(fileInfo,folderPath)


def main():
    # set folder ID to download
    folder_url = "https://drive.google.com/drive/folders/1BZuQhG2ElAOUYjcixUZQQ-f2DRqkNjn7"

    folder_ID = folder_url.split("/")[-1]
    if not os.path.exists("file_list.json"):
        refresh_download_list(folder_ID)

    with open ("file_list.json","r") as f:
        file_list = json.load(f)
    os.chdir('..')
    folder_id_name_map = folder_tree_map(file_list)
    stage_all_download(file_list,folder_id_name_map)
    # return

    # file_id = '1Jmf_dmfvEIq5Djt3JpXhjPgybx_KJdt5'
    # file_id = '1LRAiYToIwDjvIAn3nyfwV0qIcbbg2tnR'
    # destination = 'file.html'
    # download_file(file_id, destination)



if __name__ == "__main__":
    main()