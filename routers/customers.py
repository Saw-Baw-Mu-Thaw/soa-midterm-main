from fastapi import APIRouter, HTTPException, Depends, Path
import requests
from repository import config
from typing import Annotated
from dependencies import verify_token
from models.Customer import Customer

router = APIRouter(
    prefix='/customers',
    tags = ['Customers'],
    dependencies=[Depends(verify_token)]
)

@router.get('/payer/{username}')
def get_customer_by_username(username : str):
    url = config.BANKING_URL + '/banking/payer/' + username
    response = requests.get(url=url)
    r = response.json()
    cust = Customer(**r)
    return cust

@router.get('/receiver/{student_id}')
def get_receiver_info(student_id : str):
    url = config.BANKING_URL + '/banking/receiver/' + student_id
    response = requests.get(url=url)
    r = response.json()
    return r

@router.get('/receiver/check/{receiver_id}', description="Check if anyone has started a transaction for receiver")
def check_pending_transaction(receiver_id : Annotated[str, Path(description='The student ID of the receiver')]):
    url = config.BANKING_URL + '/banking/receiver/check/' + receiver_id
    response = requests.get(url=url)
    r = response.json()
    return r