from flask import Blueprint, request, Flask, jsonify, make_response, session
from google.cloud import datastore
import requests
import json
import constants
from boat_validation import valid_length, unique_name, valid_type, valid_name


project_id = "cs493-assignment3-403322"
client = datastore.Client(project = project_id)

bp = Blueprint('boats', __name__, url_prefix='/boats')

@bp.route('', methods=['POST'])
def creating_deleting_boats():
    content = request.get_json() 
    token = request.headers.get('Authorization')
    print(token)
    # 유저가 아닌경우
    if token is None:
        new_boat = datastore.entity.Entity(key=client.key(constants.Boat))
        if (set(content.keys()) != {'name', 'type', 'length'}):
            return (jsonify({"Error": "The request object is missing at least one of the required attributes"}) ,400)
        client.put(new_boat)
        new_boat_key = new_boat.key
        entity_key_id = new_boat_key.id
        # self_url 생성
        self_url = f"https://cs493-assignment3-403322.uw.r.appspot.com/boats/{entity_key_id}"

        new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"], "loads" : [], "self": self_url, 'protected': False})
        client.put(new_boat)

        if 'application/json' not in request.accept_mimetypes:
            return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)
        
        json_data = jsonify({
            "id": new_boat.key.id,
            "name": new_boat["name"],
            "type": new_boat["type"],
            "length": new_boat["length"],
            "loads": new_boat["loads"],
            "self": new_boat["self"],
            "protected": new_boat["protected"]
        })
        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.status_code = 201
        return res

    # 유저인 경우    
    else: 
        new_boat = datastore.entity.Entity(key=client.key(constants.Boat))
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

        if (set(content.keys()) != {'name', 'type', 'length'}):
            return (jsonify({"Error": "The request object is missing at least one of the required attributes"}) ,400)
        
        client.put(new_boat)
        new_boat_key = new_boat.key
        entity_key_id = new_boat_key.id
        # self_url 생성
        self_url = f"https://cs493-assignment3-403322.uw.r.appspot.com/boats/{entity_key_id}"
        # 유저를 식별할수있는 sub를 추가하기
        user = r.json()
        sub = user['sub']
        new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"], "loads" : [], "self": self_url, 'protected': True, "sub": sub})
        client.put(new_boat)

        if 'application/json' not in request.accept_mimetypes:
            return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

        json_data = jsonify({
            "id": new_boat.key.id,
            "name": new_boat["name"],
            "type": new_boat["type"],
            "length": new_boat["length"],
            "loads": new_boat["loads"],
            "self": new_boat["self"],
            "protected": new_boat["protected"],
            "sub": new_boat["sub"]
        })

        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.status_code = 201
        return res


# 모든 보트 pagination
@bp.route('', methods=['GET'])
def list_all_boats():
    if (request.method != 'GET'):
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)

    token = request.headers.get('Authorization')
    # None-User
    if token is None:
        query = client.query(kind=constants.Boat)
        # 'protected' 속성이 False인 엔터티만 필터링
        query.add_filter('protected', '=', False)
        q_limit = int(request.args.get('limit', '5'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        # 첫번째 페이지에 담긴 정보들
        pages = l_iterator.pages
        # 그 다음 정보들
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

        res = make_response(jsonify(output))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res
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

        query = client.query(kind=constants.Boat)
        # 'protected' 속성이 False인 엔터티만 필터링
        user = r.json()
        sub = user['sub']
        # 필터한다
        query.add_filter('sub', '=', sub)

        q_limit = int(request.args.get('limit', '5'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        # 첫번째 페이지에 담긴 정보들
        pages = l_iterator.pages
        # 그 다음 정보들
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

        res = make_response(jsonify(output))
        res.mimetype = 'application/json'
        res.status_code = 200
        return res


@bp.route('/<b_id>', methods=['DELETE', 'GET'])
def get_delete_boat(b_id):
    if request.method == 'GET':
        token = request.headers.get('Authorization')
        # 비사용자
        if token is None:
            boat_key = client.key(constants.Boat, int(b_id))
            boat = client.get(key=boat_key)
            if boat is not None and boat['protected'] == False:
                if 'application/json' not in request.accept_mimetypes:
                    return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)
                
                json_data = jsonify({
                    "id": boat.key.id,
                    "name": boat["name"],
                    "type": boat["type"],
                    "length": boat["length"],
                    "self": boat["self"],
                    "protected": boat["protected"]
                })
                res = make_response(json_data)
                res.mimetype = 'application/json'
                res.status_code = 200
                return res
            return jsonify({"Error": "No boat with this boat_id exists"}), 404
        # 사용자
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

            # 보트 가져로기
            boat_key = client.key(constants.Boat, int(b_id))
            boat = client.get(key=boat_key)
            if boat is not None and boat["protected"] == True and boat["sub"] == sub:
                if 'application/json' not in request.accept_mimetypes:
                    return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)
            
                json_data = jsonify({
                    "id": boat.key.id,
                    "name": boat["name"],
                    "type": boat["type"],
                    "length": boat["length"],
                    "self": boat["self"],                        
                    "protected": boat["protected"],
                    "sub": boat["sub"]
                })
                res = make_response(json_data)
                res.mimetype = 'application/json'
                res.status_code = 200
                return res
            return jsonify({"Error": "No boat with this boat_id exists"}), 404


    elif request.method == 'DELETE':
        # 보트 삭제하기
        token = request.headers.get('Authorization')
        if token is None:
            print('none_user deleted')
            # boat 키를 생성한다.
            boat_key = client.key(constants.Boat, int(b_id))
            # 보트 키로 boat 찾는다
            boat = client.get(key=boat_key)
            if boat is not None and boat['protected'] == False:
                # boat['loads']에 포함된 각 load id를 가지고 load 가져오기
                for e in boat["loads"]:
                    # id 추출해서 
                    load_key = client.key(constants.Load, e["id"]) 
                    # load 찾는다
                    load = client.get(key=load_key)
                    load.update({"carrier": None})
                    client.put(load)
                client.delete(boat_key)
                return '', 204
            # 보트 아이디가 유효하지 않음.
            return jsonify({"Error": "No boat with this boat_id exists"}), 404
        else:
            print("user deleted")
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

            # boat 키를 생성한다.
            boat_key = client.key(constants.Boat, int(b_id))
            # 보트 키로 boat 찾는다
            boat = client.get(key=boat_key)
            if boat is not None and boat['protected'] == True and boat['sub'] == sub:
                # boat['loads']에 포함된 각 load id를 가지고 load 가져오기
                for e in boat["loads"]:
                    # id 추출해서 
                    load_key = client.key(constants.Load, e["id"]) 
                    # load 찾는다
                    load = client.get(key=load_key)
                    load.update({"carrier": None})
                    client.put(load)
                client.delete(boat_key)
                return '', 204
            # 보트 아이디가 유효하지 않음.
            return jsonify({"Error": "No boat with this boat_id exists"}), 404
    else:
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)

# Edition ------------------------------------------------------------------------------------------------
@bp.route('/<b_id>', methods = ['PUT', 'PATCH'])
def edit_boat(b_id):
    if (request.method != 'PUT' and request.method != 'PATCH'):
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)

    boat_key = client.key(constants.Boat, int(b_id))
    boat = client.get(key=boat_key)
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
        if boat is None or boat['protected'] != True or boat['sub'] != sub:
            return jsonify({"Error": "No boat with this boat_id exists"}), 404
    # 유저가 아닌 경우, 검증 -> 보호되지 않는지 확인
    else: 
        print("here is for Non-User")
        # 유효한 boat id를 검사하는지 확인
        if boat is None or boat['protected'] != False:
            return jsonify({"Error": "No boat with this boat_id exists"}), 404

    # PUT method
    if request.method == 'PUT':
        return put(request.get_json(), boat, request)
    # PATCH method
    elif request.method == 'PATCH':
        return patch(request.get_json(), boat, request)


# 부분 수정
def patch(content, boat, request):
    # 부분 집합
    if not set(content.keys()).issubset({'name', 'type', 'length'}):
        return (jsonify({"Error": "The attributes client provided are not valid"}), 400)

    # 만약 name이 content 안에 포함된 속성일 경우: 유효성 검사 1
    if 'name' in content:
        if not valid_name(content['name']):
            return (jsonify({"Error": "The attributes client provided are not valid"}), 400)

    # 만약 length가 content 안에 포함된 속성일 경우: 유효성 검사 2
    if 'length' in content:
        if not valid_length(content['length']):
            return (jsonify({"Error": "The attributes client provided are not valid"}), 400)   

    # 만약 type가 content 안에 포함된 속성이 경우: 유효성 검사 3
    if 'type' in content:
        if not valid_type(content['type']):
            return (jsonify({"Error": "The attributes client provided are not valid"}), 400)  

    if 'application/json' in request.accept_mimetypes:
        # data는 나중에 json_data로 변환됨 content에 포함된 속성을 추가시킴
        data = {}
        for key in content:
            boat[key] = content[key]
            data[key] = content[key]
        client.put(boat)
        # json_data로 return
        json_data = jsonify(data)
        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.status_code = 303
        return res
    else:
        return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)


# 모든 속성(attributes) 수정(Edit)
def put(content, boat, request):
    # 모든 속성(Attributes)이 포함되지 않거나, 불필요한 속성이 포함됨
    if set(content.keys()) != {'name', 'type', 'length'}:
        return (jsonify({"Error": "The attributes client provided are not valid"}), 400)

    # 수정될 속성들(Attributes)의 유효성 검사
    if not (valid_length(content['length']) and valid_name(content['name']) and valid_type(content['type'])): 
        return (jsonify({"Error": "Some values of the attributes in the body request are not valid"}), 400)

    if 'application/json' in request.accept_mimetypes:
        # 보트 업데이트
        boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
        client.put(boat)

        json_data = jsonify({
            "id": boat.key.id,
            "name": boat["name"],
            "type": boat["type"],
            "length": boat["length"],
            "self": boat["self"]
        })

        res = make_response(json_data)
        res.mimetype = 'application/json'
        res.headers['Location'] = boat['self']
        res.status_code = 303
        return res
    else:
        return (jsonify({"Error": "Accept Content Type user request can't be supported by server"}), 406)

# 여기는 수정 부분 ------------------------------------------------------------------------------------------------

# The relationship between Boat and Load
@bp.route('/<b_id>/loads/<l_id>', methods=['PUT', 'DELETE'])
def assign_load_to_boat(l_id,b_id):
    if (request.method != 'PUT' and request.method != 'DELETE'):
        return (jsonify({"Error": "HTTP method client requests is not valid"}), 405)
    # load
    load_key = client.key(constants.Load, int(l_id))
    load = client.get(key=load_key)
    # boat
    boat_key = client.key(constants.Boat, int(b_id))
    boat = client.get(key=boat_key)

    token = request.headers.get('Authorization')
    # 비유저
    if token is None:
        if request.method == 'PUT':
            # 성공적으로 객체 생성되었다면
            if (boat is not None and load is not None and boat['protected'] == False and load['protected'] == False):
                # 만약 load가 다른 보트에 담겨져 있다면?
                if load['carrier'] != None:
                    return (jsonify({"Error": "The load is already loaded on the boat"}), 403)

                # boat['loads']를 업데이트
                js_dic_1 = {"id": load.key.id, "self": load["self"]}
                boat['loads'].append(js_dic_1)
                client.put(boat)

                # load['carrier']를 업데이트
                js_dic_2 = {"id": boat.key.id, "name": boat["name"], "self": boat["self"]}
                load.update({"carrier": js_dic_2})
                client.put(load)
                return ('',204)
            else: 
                return (jsonify({"Error": "The specified boat and/or load does not exist or The IDs of either boat or load don't valid"}) ,404)
        # 보트에 담겨져 있는 load 삭제
        if request.method == 'DELETE':
            if (boat is not None and load is not None and boat['protected'] == False and load['protected'] == False):
                # i 는 특정 load
                for i in boat["loads"]:
                    if i["id"] == int(l_id):
                        # 보트 업데이트
                        boat["loads"].remove(i)
                        client.put(boat)
                        load.update({"carrier": None})
                        client.put(load)
                        return('',204)
                return (jsonify({"Error": "The load is already unassigned on the boat"}), 403)
            return (jsonify({"Error": "The specified boat and/or load does not exist or The IDs of either boat or load don't valid"}) ,404)
    # 사용자
    else:
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
        # PUT 
        if request.method == 'PUT':
            if (boat is not None and load is not None and boat['protected'] == True and boat['sub'] == sub and load['protected'] == True and load['sub'] == sub):
                # 만약 load가 다른 보트에 담겨져 있다면?
                if load['carrier'] != None:
                    return (jsonify({"Error": "The load is already loaded on other boat"}), 403)
                js_dic_1 = {"id": load.key.id, "self": load["self"]}
                boat['loads'].append(js_dic_1)
                client.put(boat)

                js_dic_2 = {"id": boat.key.id, "name": boat["name"], "self": boat["self"]}
                load.update({"carrier": js_dic_2})
                client.put(load)
                return ('',204)
            else: 
                return (jsonify({"Error": "The specified boat and/or load does not exist"}) ,404)
        # Delete
        if request.method == 'DELETE':
            # 성공적으로 객체 생성되었다면
            if (boat is not None and load is not None and boat['protected'] == True and boat['sub'] == sub and load['protected'] == True and load['sub'] == sub):
                for i in boat["loads"]:
                    print()
                    if i["id"] == int(l_id):
                        boat["loads"].remove(i)
                        client.put(boat)
                        load.update({"carrier": None})
                        client.put(load)
                        return('',204)
            return (jsonify({"Error": "No boat with this boat_id is loaded with the load with this load_id"}), 404)