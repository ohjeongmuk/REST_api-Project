from flask import Blueprint, request, Flask, jsonify, make_response
from google.cloud import datastore
import json
import constants
import requests
from load_validation import valid_creation_date, valid_item, valid_volume

project_id = "cs493-assignment3-403322"
client = datastore.Client(project = project_id)

ld = Blueprint('loads', __name__, url_prefix='/loads')

# 모든 리스트를 보여주고, 생성
@ld.route('', methods=['POST', 'GET'])
def creating_listing_loads():
    if request.method == 'POST':
        content = request.get_json() 
        new_load = datastore.entity.Entity(key=client.key(constants.Load))
        token = request.headers.get('Authorization')
        # 비유저
        if token is None:
            print("here is for non-user")
            if (set(content.keys()) != {'volume', 'item', 'creation_date'}):
                return (jsonify({"Error": "The request object is missing at least one of the required attributes"}) ,400)
            # 엔터티를 추가합니다.
            client.put(new_load)
            # 추가된 엔터티의 키 정보를 추출합니다.
            new_load_key = new_load.key
            # 엔터티의 ID를 추출합니다.
            entity_key_id = new_load_key.id
            # self URL을 생성합니다.
            self_url = f"https://cs493-assignment3-403322.uw.r.appspot.com/loads/{entity_key_id}"
            new_load.update({"volume": content["volume"], "item": content["item"], "creation_date": content["creation_date"], "carrier" : None, "self": self_url, "protected": False})
            client.put(new_load)

            # application/json 검증
            if 'application/json' not in request.accept_mimetypes:
                return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

            json_data = jsonify({
                    "id": new_load.key.id,
                    "volume": new_load["volume"],
                    "item": new_load["item"],
                    "creation_date": new_load["creation_date"],
                    "carrier": new_load["carrier"],
                    "self": new_load["self"],
                    "protected": new_load["protected"]
                })
            
            res = make_response(json_data)
            res.mimetype = 'application/json'
            res.status_code = 201
            return res

        # 유저
        else:
            print("here is for user")
            headers= {
            'Content-Type': 'application/json',
            "Authorization": request.headers.get('Authorization')
            }
            url = 'https://cs493-assignment3-403322.uw.r.appspot.com/decode'
            r = requests.get(url, headers = headers)   
            # 유효하지 않은 경우
            if r.status_code != 200:
                return (jsonify({"Error": "Invalid JWT."}), 401) 
            # sub 정보 얻어오기
            user = r.json()
            sub = user['sub']

            if (set(content.keys()) != {'volume', 'item', 'creation_date'}):
                return (jsonify({"Error": "The request object is missing at least one of the required attributes"}) ,400)
            
            client.put(new_load)
            new_load_key = new_load.key
            entity_key_id = new_load_key.id
            # self URL을 생성합니다.
            self_url = f"https://cs493-assignment3-403322.uw.r.appspot.com/loads/{entity_key_id}"
            new_load.update({"volume": content["volume"], "item": content["item"], "creation_date": content["creation_date"], "carrier" : None, "self": self_url, "protected": True, "sub": sub})
            client.put(new_load)

            if 'application/json' not in request.accept_mimetypes:
                return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

            json_data = jsonify({
                    "id": new_load.key.id,
                    "volume": new_load["volume"],
                    "item": new_load["item"],
                    "creation_date": new_load["creation_date"],
                    "carrier": new_load["carrier"],
                    "self": new_load["self"],
                    "protected": new_load["protected"],
                    "sub": new_load["sub"]
                })
            
            res = make_response(json_data)
            res.mimetype = 'application/json'
            res.status_code = 201
            return res
        
    # 모든 load 리스트 제공
    elif request.method == 'GET':
        token = request.headers.get('Authorization')
        # 비유저
        if token is None:
            # query는 데이터베이스에서 얻는 정보
            query = client.query(kind=constants.Load)
            # limit과 offset은 request 되어진 arguments에서 
            query.add_filter('protected', '=', False)
            q_limit = int(request.args.get('limit', '5'))
            q_offset = int(request.args.get('offset', '0'))
            # fetch => 가져오다, 검색하다 데이터 베이스나 다른 데이터 저장소에서 데이터를 가져오거나 검색하는 작업을 수행
            l_iterator = query.fetch(limit= q_limit, offset=q_offset)
            pages = l_iterator.pages
            results = list(next(pages))
            if l_iterator.next_page_token:
                next_offset = q_offset + q_limit
                next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
            else:
                next_url = None
            for e in results:
                e["id"] = e.key.id
            output = {"loads": results}
            if next_url:
                output["next"] = next_url

            if 'application/json' not in request.accept_mimetypes:
                return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

            res = make_response(output)
            res.mimetype = 'application/json'
            res.status_code = 200
            return res
        # 유저
        else:
            # 검증
            headers= {
                'Content-Type': 'application/json',
                "Authorization": request.headers.get('Authorization')
            }
            url = 'https://cs493-assignment3-403322.uw.r.appspot.com/decode'
            r = requests.get(url, headers = headers)
            # 유효하지 않은 경우
            if r.status_code != 200:
                return (jsonify({"Error": "Invalid JWT."}), 401)
            # sub 구하기
            user = r.json()
            sub = user['sub']

            # query는 데이터베이스에서 얻는 정보
            query = client.query(kind=constants.Load)
            query.add_filter('sub', '=', sub)
            q_limit = int(request.args.get('limit', '5'))
            q_offset = int(request.args.get('offset', '0'))
            l_iterator = query.fetch(limit= q_limit, offset=q_offset)
            pages = l_iterator.pages
            results = list(next(pages))

            if l_iterator.next_page_token:
                next_offset = q_offset + q_limit
                # request.base_url은 현재 요청의 url을 나타낸다. 그리고 뒤에는 다음 페이지로 넘어가기 위한 쿼리 요청
                next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
            else:
                next_url = None

            for e in results:
                e["id"] = e.key.id
            output = {"boats": results}
            if next_url:
                output["next"] = next_url
                
            if 'application/json' not in request.accept_mimetypes:
                return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

            res = make_response(output)
            res.mimetype = 'application/json'
            res.status_code = 200
            return res
    else:
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)

# 특정 load를 보여주고, DELETE
@ld.route('/<l_id>', methods=['GET', 'DELETE'])
def get_load(l_id):
    if (request.method != 'GET' and request.method != 'DELETE'):
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)
    # Google Cloud Datastore에서 데이터를 검색하기 위한 Query 객체. 
    load_key = client.key(constants.Load, int(l_id))
    load = client.get(key=load_key)

    token = request.headers.get('Authorization')
    # 비사용자
    if token is None:
        # READ
        if request.method == 'GET':
            if load is not None and load['protected'] == False:

                if 'application/json' not in request.accept_mimetypes:
                    return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

                json_data = jsonify({
                    "id": load.key.id,
                    "volume": load["volume"],
                    "item": load["item"],
                    "creation_date": load["creation_date"],
                    "carrier": load["carrier"],
                    "self": load["self"],
                    "protected": load["protected"]
                })
                res = make_response(json_data)
                res.mimetype = 'application/json'
                res.status_code = 200
                return res
            return jsonify({"Error": "No load with this load_id exists"}), 404
        # DELETE
        elif request.method == 'DELETE':
            # 아이디 검증
            if load is not None and load['protected'] == False:
                if load["carrier"] is not None:
                    loaded_boat = load["carrier"]
                    boat_key = client.key(constants.Boat, loaded_boat["id"])
                    boat = client.get(key=boat_key)
                    # 보트가 보호되지 않는지 확인
                    if boat['protected'] == False:
                        for e in boat["loads"]:
                            if e["id"] == int(l_id):
                                # e 원소를 boat["loads"] 리스트에서 삭제하고 업데이트 
                                boat["loads"].remove(e)
                                boat.update({"loads": boat["loads"]})
                                client.put(boat)
                client.delete(load_key)
                return '', 204

            return jsonify({"Error": "No load with this load_id exists or the ID of the load is not valid."}), 404
    # 사용자일경우
    else:
        # 검증
        headers= {
            'Content-Type': 'application/json',
            "Authorization": request.headers.get('Authorization')
        }
        url = 'https://cs493-assignment3-403322.uw.r.appspot.com/decode'
        r = requests.get(url, headers = headers)
        # 유효하지 않은 경우
        if r.status_code != 200:
            return (jsonify({"Error": "Invalid JWT."}), 401)
        user = r.json()
        sub = user['sub']
        if request.method == 'GET':
            # 아이디 검증
            if load is not None and load["protected"] == True and load["sub"] == sub:

                if 'application/json' not in request.accept_mimetypes:
                    return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

                json_data = jsonify({
                    "id": load.key.id,
                    "volume": load["volume"],
                    "item": load["item"],
                    "creation_date": load["creation_date"],
                    "carrier": load["carrier"],
                    "self": load["self"],                        
                    "protected": load["protected"],
                    "sub": load["sub"]
                })
                res = make_response(json_data)
                res.mimetype = 'application/json'
                res.status_code = 200
                return res
            return jsonify({"Error": "No load with this load_id exists"}), 404
        # Delete
        elif request.method == 'DELETE':
            # 아이디 검증
            if load is not None and load["protected"] == True and load["sub"] == sub:
                if load["carrier"] is not None:
                    # load["carrier"] 은 실제 보트 정보하고는 다름
                    loaded_boat = load["carrier"]
                    boat_key = client.key(constants.Boat, loaded_boat["id"])
                    boat = client.get(key=boat_key)
                    # 보트가 보호되지는 확인한다 -> 보호된다면 sub를 검사한다.
                    if boat['protected'] == True and boat['sub'] == sub:
                        for e in boat["loads"]:
                            if e["id"] == int(l_id):
                                # e 원소를 boat["loads"] 리스트에서 삭제하고 업데이트 
                                boat["loads"].remove(e)
                                boat.update({"loads": boat["loads"]})
                                client.put(boat)
                client.delete(load_key)
                return '', 204
            return jsonify({"Error": "No load with this load_id exists or the ID of the load is not valid."}), 404

    
# 특정 load PUT(ALL), PATCH(PART)
@ld.route('/<l_id>', methods=['PUT', 'PATCH'])
def edit_load(l_id):
    if (request.method != 'PUT' and request.method != 'PATCH'):
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)
    
    load_key = client.key(constants.Load, int(l_id))
    load = client.get(key=load_key)
    token = request.headers.get('Authorization')
    sub = str()
    # 유저인 경우, 검증 -> 유효한 아이디를 검사하는지 확인
    if token is not None:
        # 검증
        print('here is for User')
        headers= {
            'Content-Type': 'application/json',
            "Authorization": request.headers.get('Authorization')
        }
        url = 'https://cs493-assignment3-403322.uw.r.appspot.com/decode'
        r = requests.get(url, headers = headers)
        # 유효하지 않은 경우
        if r.status_code != 200:
            return (jsonify({"Error": "Invalid JWT."}), 401)
        
        user = r.json()
        sub = user['sub']
        # 유효한 boat id를 검사하는지 확인
        if load is None or load['protected'] != True or load['sub'] != sub:
            return jsonify({"Error": "No load with this load_id exists"}), 404
    # 유저가 아닌 경우, 검증 -> 보호되지 않는지 확인
    else: 
        print("here is for Non-User")
        # 유효한 boat id를 검사하는지 확인
        if load is None or load['protected'] != False:
            return jsonify({"Error": "No load with this load_id exists"}), 404

    # PUT method
    if request.method == 'PUT':
        #if request.headers['Content-Type'] != 'application/json':
        #    return (jsonify({"Error": "The content type of the request by Client is not a json file"}), 415)
        return put(request.get_json(), load, request)
    # PATCH method
    elif request.method == 'PATCH':
        # if request.headers['Content-Type'] != 'application/json':
        #    return (jsonify({"Error": "The content type of the request by Client is not a json file"}), 415)
        return patch(request.get_json(), load, request)
    
# 부분 수정
def patch(content, load, request):
    # 부분 집합
    if not set(content.keys()).issubset({'creation_date', 'item', 'volume'}):
        return (jsonify({"Error": "The attributes client provided are not valid"}), 400)

    # 만약 creation_date 이 content 안에 포함된 속성일 경우: 유효성 검사 1
    if 'creation_date' in content:
        if not valid_creation_date(content['creation_date']):
            return (jsonify({"Error": "The creatiion_date is not valid"}), 403)
    # 만약 item가 content 안에 포함된 속성일 경우: 유효성 검사 2
    if 'item' in content:
        if not valid_item(content['item']):
            return (jsonify({"Error": "The item is not valid"}), 400)   

    # 만약 volume가 content 안에 포함된 속성이 경우: 유효성 검사 3
    if 'volume' in content:
        if not valid_volume(content['volume']):
            return (jsonify({"Error": "The volume is not valid"}), 400)  

    
    if 'application/json' in request.accept_mimetypes:
        # data는 나중에 json_data로 변환됨 content에 포함된 속성을 추가시킴
        data = {}
        for key in content:
            load[key] = content[key]
            data[key] = content[key]
        client.put(load)

        # json_data로 return
        json_data = jsonify(data)
        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.status_code = 303
        return res
    else:
        return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

# 모든 속성(attributes) 수정(Edit)
def put(content, load, request):
    # 모든 속성(Attributes)이 포함되지 않거나, 불필요한 속성이 포함됨
    if set(content.keys()) != {'creation_date', 'volume', 'item'}:
        return (jsonify({"Error": "The attributes client provided are not valid"}), 400)

    # 수정될 속성들(Attributes)의 유효성 검사
    if not (valid_creation_date(content['creation_date']) and valid_item(content['item']) and valid_volume(content['volume'])): 
        return (jsonify({"Error": "Some values of the attributes in the body request are not valid"}), 400)


    if 'application/json' in request.accept_mimetypes:
        # 보트 업데이트
        load.update({"creation_date": content["creation_date"], "volume": content["volume"], "item": content["item"]})
        client.put(load)

        json_data = jsonify({
            "creation_date": load["creation_date"],
            "item": load["item"],
            "volume": load["volume"]
        })

        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.headers['Location'] = load['self']
        res.status_code = 303
        return res
    else:
        return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)