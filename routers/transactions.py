import requests
from fastapi import APIRouter, Depends, HTTPException, status, Path
from dependencies import verify_token, get_username, verify_receiver
from models.input_models import NewTransactionInput
from typing import Annotated
from repository import config
import json

router = APIRouter(
    prefix='/transactions',
    tags=['Transactions'],
    dependencies=[Depends(verify_token)]
)

@router.post('/create', description='Create a new transaction')
async def create_new_transaction(input : NewTransactionInput, username : Annotated[str, Depends(get_username)]):
    # verify receiver
    verify_receiver(input.receiver_id)

    # verify payer
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='One or more incorrect input')
    
    # check balance >= tuition
    if input.available_balance < input.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Insufficient balance')
    
    # check any pending transaction
    url = config.BANKING_URL + 'banking/receiver/check/' + input.receiver_id
    response = requests.get(url=url)

    r = response.json()

    if r['result'] == True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pending Transaction')
    
    
    # then create new transaction
    url = config.BANKING_URL + '/banking/transaction/create'
    data = {
        'payer_id' : input.payer_id,
        'receiver_id' : input.receiver_id.upper(),
        'debt_id' : input.debt_id
            }
    response = requests.post(url=url, data=json.dumps(data))

    if response.status_code == 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please check your input')
    
    r = response.json()
    transaction_id = r['transaction_id']

    # temporary
    return r

    # TODO : send transaction id to otp service

    # TODO : make requests to email service

@router.get('/me')
async def get_all_transactions(username : Annotated[str , Depends(get_username)]):
    url = config.BANKING_URL + '/banking/transactions/all/' + username
    response = requests.get(url=url)
    return response.json()
