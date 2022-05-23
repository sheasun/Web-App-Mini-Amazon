# ERSS-project-ac692-ss1316

## Production Deployment
- **WARNING** DO NOT use docker-compose, networking issues still under investigation

## Testing Deployment
1. for the front end, install dependencies and run the development server
```
cd frontend
npm i
cd ..
```

2. for the back end, create python virtual environment and install dependencies
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

3. change [config.py](backend/config.py)

4. launch the socket server, http server and the UI server
```
cd frontend
npm run dev
cd ../backend
source venv/bin/activate
python socket_server.py
python server.py
```