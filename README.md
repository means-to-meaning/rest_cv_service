# REST service using Python Flask - accepting multipart/form-data image uploads

## Dependencies

pip install flask

## Run server

```
python rest_service.py
```

## Test server

```
curl http://127.0.0.1:5000/
curl -F "image=@img1.jpg" http://127.0.0.1:5000/upload
```

