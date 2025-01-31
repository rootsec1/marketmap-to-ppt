# MarketMap to PPT converter

This is a simple tool to convert a MarketMap to a PPT file. It uses the `python-pptx` library to create the PPT file.

# How it works

1. The image is passed to a VLM (here, Gemini 2.0 Flash) to extract out all the companies and then map them to their domains.
2. These domains are later passed to [https://logo.dev](https://logo.dev) to get the logos of the companies.
3. High quality logos are then downloaded concurrently.
4. Using the python-pptx library, the logos are added to the PPT file in a grid like format dynamically arranging the icon size
5. The presigned URL of the PPT file is returned to the user.
6. The user can download the PPT file using the presigned URL.
7. All assets such as user image uploads and presentations are stored in an S3 bucket.

# How to run

1. Clone the repository
2. Setup minio server (minio runs on port `9000`)
NOTE: Download the binary from [https://min.io/docs/minio/macos/index.html#procedure](https://min.io/download)
```bash
./minio server /data
```
- Upon running this command, it will output the web console URL, go to it, default creds: `minioadmin:minioadmin`
- Create an API key and secret in the settings page of minio.

3. Setup backend (& secrets in `backend/constants.py`)

```bash
cd backend
pip install -r requirements.txt
fastapi dev app.py
```

4. Setup frontend
Optionally adjust API_URL in `constants.js` (defaults to localhost)
```bash
cd web-ui
npm install
npm run dev
```

