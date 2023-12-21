from flask import Blueprint, request, Flask, jsonify, make_response
from google.cloud import datastore
from json2html import json2html
import json
import constants

project_id = "cs493-assignment3-403322"
client = datastore.Client(project = project_id)

def unique_name(boat_name, client = client):
    # query 객체는 DataStore에 존재하는 Boat 객체들
    query = client.query(kind = constants.Boat)
    results = list(query.fetch())
    # results 는 Boat 객체들의 리스트
    for e in results:
        # 만약 똑같은 이름이 존재하면 return False 
        if e['name'] == boat_name:
            return False
    return True

def valid_name(boat_name):
    # 만약 문자열이 스트링이 아닐 경우
    if not isinstance(boat_name, str):
        return False
    # 모든 문자열을 검사해서 문자열이 대문자와 소문자로 이루어졌는지 확인한다.
    for e in boat_name:
        if not ('A' <= e <= 'Z' or 'a' <= e <= 'z' or e.isspace()):
            return False
    return True

def valid_length(boat_length):
    if not isinstance(boat_length, int):
        return False
    if boat_length < 0:
        return False
    return True

def valid_type(boat_type):
    if not isinstance(boat_type, str):
        return False
    # 모든 문자열의 문자를 검사: 대문자  & 소문자 조합
    for e in boat_type:
        if not ('A' <= e <= 'Z' or 'a' <= e <= 'z' or e.isspace()):
            return False
    return True
