# gdrive-dl
### Google Drive recursive folder contents downloader

* Clone the repo in the drive you want to download the GDrive folder.

* Install requirements.
	```
	pip install -r requirements.txt
	```

* Set `folder_url` under main function, to your desired one.

* Run the script.
	```
	python download.py
	```

## Important

If your downloads are just small files, most probably google is blocking your request.
Proxy implementation is left.