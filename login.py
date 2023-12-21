import requests
from functools import wraps
import json
from google.cloud import datastore
import constants
from six.moves.urllib.request import urlopen
from flask_cors import cross_origin
from jose import jwt
import json
from os import environ as env
from dotenv import load_dotenv, find_dotenv
from flask import jsonify
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import request
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode, quote_plus
import os
from flask import current_app as app


project_id = "cs493-assignment3-403322"
client = datastore.Client(project = project_id)
lg = Blueprint('login', __name__)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = env.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = env.get('AUTH0_CLIENT_SECRET')
AUTH0_API_URL = f'https://{AUTH0_DOMAIN}/api/v2/'

# OAuth 인증을 구현하기 위해서, Flask-OAuth 라이브러리의 객체를 생성한다. 
# oauth는 OAuth()클래스의 인스턴스. 이 객체를 사용하여 OAuth 프로바이더(Auth0)와 통신하고 사용자의 인증 및 권한을 부여한다.
oauth = OAuth(app)
# oauth 객체에 프로바이더에 대한 클라이언트 아이디, 시크릿, 액세스 토큰 URL, 토큰 URL등을 설정한다.
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    access_token_url="https://" + env.get("AUTH0_DOMAIN") + "/oauth/token",
    authorize_url="https://" + env.get("AUTH0_DOMAIN") + "/authorize",
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

ALGORITHMS = ["RS256"]

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@lg.route('/login', methods=['POST', 'GET'])
def login_user():
    if request.method == 'GET':
        return render_template('home.html')
    if request.method == 'POST':
        print(app.secret_key)
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("login.callback", _external=True)
        )

@lg.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    # user email과 고유 sub를 추출
    email = token['userinfo']['email']
    sub = token['userinfo']['sub']
    # 새로운 유저의 Entity 생성
    new_user = datastore.entity.Entity(key = client.key(constants.User))
    new_user.update({'email': email, 'sub': sub})
    client.put(new_user)
    return redirect("/")

@ lg.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET': 
        return render_template('signup.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Call Auth0 Management API to create a new user
        headers = {
            'Authorization': f'Bearer {get_auth0_access_token()}',
            'Content-Type': 'application/json'
        }

        data = {
            'connection': 'Username-Password-Authentication',
            'email': username,
            'password': password
        }

        response = requests.post(AUTH0_API_URL + 'users', headers=headers, json=data)
        print(response.status_code)
        print(response.text)
        if response.status_code == 201:
            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Failed to create account. Please try again.', 'danger')
            return redirect(url_for('login.signup'))

def get_auth0_access_token():
    # Obtain Auth0 Management API access token using client credentials grant
    url = f'https://{AUTH0_DOMAIN}/oauth/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'audience': AUTH0_API_URL
    }
    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(response.text)  # 이 부분 추가
        raise Exception('Failed to obtain Auth0 Management API access token')

@lg.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@lg.route('/users', methods = ['GET'])
def get_users_list():
    if request.method == 'GET':
    # Google Cloud Datastore에서 데이터를 검색하기 위한 Query 객체. 
        query = client.query(kind=constants.User)
        results = list(query.fetch())
        users_list = []

        for user_entity in results:
            user_data = {
                "GCP_id": user_entity.id,
                "email": user_entity['email'],
                "sub": user_entity['sub']
            }
            users_list.append(user_data)
        return jsonify(users_list), 200

@lg.route('/myaccount', methods = ['GET'])
def get_users():
    if request.method == 'GET':
        headers= {
            'Content-Type': 'application/json',
            "Authorization": request.headers.get('Authorization')
        }
        url = 'https://cs493-assignment3-403322.uw.r.appspot.com/decode'
        #url = 'http://localhost:8080/decode'
        r = requests.get(url, headers = headers)
        # 유효하지 않은 경우
        if r.status_code != 200:
            return (jsonify({"Error": "Invalid JWT."}), 401)
        
        user = r.json()
        if user is None:
            return jsonify({"Error": "There is no user looking for"}), 404
        
        sub = user['sub']

        query = client.query(kind=constants.User)
        results = list(query.fetch())
        for u in results:
            if (u['sub'] == sub):
                user_data = {
                    "GCP_id": u.id,
                    "email": user['email'],
                    "sub": user['sub']
                }
                return jsonify(user_data), 200
        return jsonify({"Error": "The user doesn't register for this application."}), 404

@lg.route('/non_user', methods = ['GET'])
def none_user():
    if request.method == 'GET':
        session['user'] = None
        return render_template('non_user.html')
    
@lg.route('/decode', methods=['GET'])
def decode_jwt():
    payload = verify_jwt(request)
    # return a type of dict 
    return payload

# Verify the JWT in the request's Authorization header
def verify_jwt(request):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization'].split()
        token = auth_header[1]
    else:
        raise AuthError({"code": "no auth header",
                            "description":
                                "Authorization header is missing"}, 401)
    
    jsonurl = urlopen("https://"+ env.get("AUTH0_DOMAIN")+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Invalid header. "
                            "Use an RS256 signed JWT Access Token"}, 401)
    if unverified_header["alg"] == "HS256":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Invalid header. "
                            "Use an RS256 signed JWT Access Token"}, 401)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=env.get("AUTH0_CLIENT_ID"),
                issuer="https://"+ env.get("AUTH0_DOMAIN")+"/"
            )
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                            "description": "token is expired"}, 401)
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                            "description":
                                "incorrect claims,"
                                " please check the audience and issuer"}, 401)
        except Exception:
            raise AuthError({"code": "invalid_header",
                            "description":
                                "Unable to parse authentication"
                                " token."}, 401)

        return payload
    else:
        raise AuthError({"code": "no_rsa_key",
                            "description":
                                "No RSA key in JWKS"}, 401)
