from typing import Any, Dict, List, cast, Union

from boa3.builtin import CreateNewEvent, NeoMetadata, metadata, public
from boa3.builtin.contract import abort
from boa3.builtin.interop.blockchain import Transaction
from boa3.builtin.interop.contract import GAS as GAS_SCRIPT, call_contract, destroy_contract, update_contract
from boa3.builtin.interop.runtime import calling_script_hash, check_witness, time, script_container, \
    executing_script_hash
from boa3.builtin.interop.storage import delete, get, put
from boa3.builtin.type import ECPoint, UInt160



# -------------------------------------------
# METADATA
# -------------------------------------------

@metadata
def manifest_metadata() -> NeoMetadata:
    meta = NeoMetadata()
    # meta.add_permission(contract='*', methods='*')
    meta.add_permission(contract='0x1c5789c06069d0a63b1b8447eb2aaa9942e8c096')
    meta.add_permission(contract='0xd2a4cff31913016155e38e474a2c06d08be276cf')
    meta.add_trusted_source('0xd2a4cff31913016155e38e474a2c06d08be276cf')
    return meta

# -------------------------------------------
# VARIABLES SETTINGS
# -------------------------------------------

DEPLOYED = b'deployed'
CAC_ADDRESS_OWNER = b'owner_address'

TOKEN_ADDRESS: bytes = b'token_address'
SALE_MARKET_ADDRESS: bytes = b'sale_market_address'
gaziki = b'gaziki'

# -------------------------------------------
# System Methods
# -------------------------------------------

@public
def verify() -> bool:
    return check_witness(cast(UInt160, get(CAC_ADDRESS_OWNER)))

@public
def _deploy(data: Any, update: bool):

    if get(DEPLOYED).to_bool():
        abort()

    if not update:
        tx = cast(Transaction, script_container)
        put(CAC_ADDRESS_OWNER, cast(UInt160, tx.sender))
        put(DEPLOYED, True)

@public
def update(script: bytes, manifest: bytes):
    update_contract(script, manifest)

@public
def destroy():
    destroy_contract()

# -------------------------------------------
# Structs
# -------------------------------------------

def Cutie(
        genes: int,
        birth_time: int,
        cooldown_end_time: int,
        dad_id: int,
        mom_id: int,
        cooldown_index: int,
        generation: int,
        optional: int,
) -> Dict[str, int]:
    cutie = {
        'genes': genes,
        'birth_time': birth_time,
        'mom_id': mom_id,
        'dad_id': dad_id,
        'cooldown_end_time': cooldown_end_time,
        'cooldown_index': cooldown_index,
        'generation': generation,
        'optional': optional
    }
    return cutie


# -------------------------------------------
# Methods
# -------------------------------------------

@public
def setup(token: UInt160) -> None:
    assert token != UInt160(), 'Zero address'
    put(TOKEN_ADDRESS, token)

@public
def set_sale_market_address(address: UInt160) -> None:
    assert address != UInt160(), 'Zero address'
    put(SALE_MARKET_ADDRESS, address)

@public
def set_gaziki(address: UInt160) -> None:
    assert address != UInt160(), 'Zero address'
    put(gaziki, address)

@public
def onNEP17Payment(t_from: UInt160, t_amount: int, data: List[Any]):
    assert t_amount > 0, 'no funds transferred'
    p_len = len(data)
    assert p_len > 1, 'incorrect data length'

    p_operation = cast(str, data[0])

    if p_operation == '_create_sale_auction':
        assert p_len == 5, 'incorrect arguments to createStream'
        cutie_id = cast(int, data[1])
        start_price = cast(int, data[2])
        end_price = cast(int, data[3])
        duration = cast(int, data[4])
        _create_sale_auction(t_from, t_amount, GAS_SCRIPT, cutie_id, start_price, end_price, duration)
        return
    if p_operation == 'cutie_check_witness':
        cutie_check_witness()
        return
    if p_operation == 'core_check_witness':
        core_check_witness()
        return
    if p_operation == 'call_delegated_approve_test':
        assert p_len == 5, 'incorrect arguments to createStream'
        cutie_id = cast(int, data[1])
        start_price = cast(int, data[2])
        end_price = cast(int, data[3])
        duration = cast(int, data[4])
        call_delegated_approve_test()
        return
    abort()

@public
def onNEP11Payment(from_address: UInt160, amount: int, tokenId: bytes, data: Any):
    abort()

def _create_sale_auction(address_from: UInt160, amount: int, token_address: UInt160, cutie_id: int, start_price: int, end_price: int, duration: int) -> None:
    call_contract(UInt160(get(TOKEN_ADDRESS)), 'delegated_approve', [address_from, UInt160(get(TOKEN_ADDRESS)), cutie_id])

@public
def test_simple() -> None:
    UInt160(get(gaziki))

@public
def test_simple_Two() -> None:
    get(gaziki)

@public
def call_delegated_approve_test() -> None:
    call_contract(UInt160(get(TOKEN_ADDRESS)), 'delegated_approve_test', [b'testegg'])

@public
def cutie_check_witness() -> Any:
    return call_contract(UInt160(get(TOKEN_ADDRESS)), 'cutie_witness', [1])

@public
def cutie_check_witness_com(address_from: UInt160, amount: int, token_address: UInt160, cutie_id: int, start_price: int, end_price: int, duration: int) -> Any:
    return call_contract(UInt160(get(TOKEN_ADDRESS)), 'cutie_witness', [address_from, UInt160(get(TOKEN_ADDRESS)), cutie_id])


@public
def core_check_witness() -> bool:
    owner: UInt160 = call_contract(UInt160(get(TOKEN_ADDRESS)), 'ownerOf', [1])
    return check_witness(owner)
