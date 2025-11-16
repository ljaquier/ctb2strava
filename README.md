# ctb2strava
Simple Python script that allows to create activities on Strava from a [Climbing Tracker](https://play.google.com/store/apps/details?id=freudenmann.climbing_track&hl=en) backup file.

## How to get credentials from Strava

1. Create a "My API Application"\
   https://www.strava.com/settings/api

2. Retrieve the `<client_id>` and `<client_secret>`

3. Request and allow access from a browser\
   `https://www.strava.com/oauth/authorize?client_id=<client_id>&response_type=code&redirect_uri=http://localhost/exchange_token&scope=activity:write,read`

4. Retrieve the `<authorization_code>` that is in the browser URL bar\
   `http://localhost/exchange_token?state=&code=<authorization_code>&scope=activity:write,read`

5. Exchange the `<authorization_code>` for a `<refresh_token>`\
   `curl -s -X POST https://www.strava.com/oauth/token -d client_id="<client_id>" -d client_secret="<client_secret>" -d code="<authorization_code>" -d grant_type=authorization_code`

6. Create a `config.json` with the credentials
   ```json
   {
     "client_id": "<client_id>",
     "client_secret": "<client_secret>",
     "refresh_token": "<refresh_token>",
     "last_export": "1900-01-01T00:00:00.000"
   }
   ```

## Usage
As a script:
```bash
pip3 install -r requirements.txt -t lib
PYTHONPATH=./lib python3 ctb2strava.py config.json ctb.json
```

As a Docker container:
```
docker build -t ctb2strava .
docker run -it --rm -v config.json:/usr/src/app/config.json -v ctb.json:/usr/src/app/ctb.json --name ctb2strava ctb2strava
```
