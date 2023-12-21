from flask import Blueprint, request, Flask, jsonify, make_response
from google.cloud import datastore
from json2html import json2html
import json
import constants

project_id = "cs493-assignment3-403322"
client = datastore.Client(project = project_id)

def valid_creation_date(creation_date):
    # "MM/DD/YYYY" 형식의 날짜 문자열 검증
    parts = creation_date.split('/')
    
    # 날짜 문자열이 3 부분으로 이루어져 있는지 확인
    if len(parts) != 3:
        return False
    
    # 각 부분이 숫자로 이루어져 있는지 확인
    if not all(part.isdigit() for part in parts):
        return False

    # 달과 일의 범위를 확인
    month, day, year = map(int, parts)
    if 1 <= month <= 12 and 1 <= day <= 31:
        return True
    else:
        return False


def valid_item(item):
    if not isinstance(item, str):
        return False
    # 모든 문자열의 문자를 검사: 대문자  & 소문자 조합
    for e in item:
        if not ('A' <= e <= 'Z' or 'a' <= e <= 'z' or e.isdigit() or e.isspace()):
            return False
    return True


def valid_volume(volume):
    if not isinstance(volume, int):
        return False
    if volume < 0:
        return False
    return True
