import json
from fastapi import FastAPI
from starlette import requests
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
import requests
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],#http://localhost:3000
    allow_methods=['*'],
    allow_headers=['*']
)


GOOGLE_CLIENT_ID = "894307833243-qdqojkj9pd25aduconsfns23m9qo51rk.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
app.add_middleware(SessionMiddleware, secret_key="!secret")

oauth = OAuth()

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    return HTMLResponse('<a href="/login">Click here to login with Google...</a>')


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        response = requests.post('http://127.0.0.1:8000' + '/users/search-by-email', json=json.dumps(user))
        compare1 = response.json()
        if compare1 is None: # not find that person
            newUser = {"email": user["email"], "address": 'unknown'}
            addon = requests.post('http://127.0.0.1:8000' + '/users/json', json=json.dumps(newUser))
            compare2 = addon.json()
            userid2 = compare2['user'][0]['user_id']
            target = 'http://127.0.0.1:3000/'+str(userid2)
            return RedirectResponse(url=target)
        else:
            userid1 = compare1['user'][0]['user_id']
            target = 'http://127.0.0.1:3000/'+str(userid1)
            return RedirectResponse(url=target)

@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@app.post('/buy')
async def buy(request: Request):
    buy_detail = await request.json()
    book_id = buy_detail["book_id"]
    user_id = buy_detail["user_id"]
    quantity = buy_detail["quantity"]
    response = requests.patch('http://localhost:8001/books/buy/' + str(book_id), json=json.dumps(dict(quantity=buy_detail["quantity"])))
    response = response.json()
    book_id = str(response["book"]["book_id"])
    book_name = response["book"]["book_name"]
    price = response["book"]["price"]
    print(quantity)
    requests.post('http://localhost:8002/orders/buy', json = json.dumps({"user_id":user_id,"book_id":book_id,"book_name":book_name,"price":price,"quantity":quantity}))
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "price": price,
        "book_name":book_name
    })




if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)