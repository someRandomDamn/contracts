from typing import Any, Dict, Union, cast, List

from boa3.builtin import CreateNewEvent, NeoMetadata, metadata, public
from boa3.builtin.contract import Nep11TransferEvent, abort
from boa3.builtin.interop.blockchain import get_contract, Transaction
from boa3.builtin.interop.contract import call_contract, destroy_contract, update_contract
from boa3.builtin.interop.iterator import Iterator
from boa3.builtin.interop.runtime import check_witness, script_container, calling_script_hash
from boa3.builtin.interop.stdlib import serialize, deserialize
from boa3.builtin.interop.storage import delete, get, put, find, get_context
from boa3.builtin.interop.storage.findoptions import FindOptions
from boa3.builtin.type import UInt160, ByteString,ECPoint


# -------------------------------------------
# METADATA
# -------------------------------------------
@metadata
def gm_manifest() -> NeoMetadata:
    """
    Defines this smart contract's metadata information
    """
    meta = NeoMetadata()
    meta.author = "Template Author"  # TODO_TEMPLATE
    meta.description = "Some Description"  # TODO_TEMPLATE
    meta.email = "hello@example.com"  # TODO_TEMPLATE
    # meta.add_permission(contract='*', methods='*')
    return meta

# -------------------------------------------
# TOKEN SETTINGS
# -------------------------------------------

# Symbol of the Token
TOKEN_SYMBOL = 'EXMP'  # TODO_TEMPLATE

# Number of decimal places
TOKEN_DECIMALS = 0

DEPLOYED = b'deployed'
PAUSED = b'paused'

ADDRESS_OWNER = b'owner_address'
ADDRESS_GAME = b'game_address'


# -------------------------------------------
# Prefixes
# -------------------------------------------

APPROVALS_PREFIX = b'approvals_'
OPERATOR_APPROVALS_PREFIX = b'op_approvals_'

ACCOUNT_PREFIX = b'ACC'
TOKEN_PREFIX = b'TPF'
BALANCE_PREFIX = b'BLP'
SUPPLY_PREFIX = b'SPP'
META_PREFIX = b'MDP'

# -------------------------------------------
# Keys
# -------------------------------------------

TOKEN_COUNT = b'TOKEN_COUNT'

# -------------------------------------------
# Events
# -------------------------------------------

OnTransfer = Nep11TransferEvent
Approval = CreateNewEvent([('owner', UInt160), ('approved', UInt160), ('tokenId', int)], 'Approval')
ApprovalForAll = CreateNewEvent([('owner', UInt160), ('operator', UInt160), ('approved', bool)], 'ApprovalForAll')

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
# System Methods
# -------------------------------------------

@public
def verify() -> bool:
    return check_witness(cast(UInt160, get(ADDRESS_OWNER)))

@public
def _deploy(data: Any, update: bool):

    if get(DEPLOYED).to_bool():
        abort()

    if not update:
        tx = cast(Transaction, script_container)
        put(ADDRESS_OWNER, cast(UInt160, tx.sender))
        put(DEPLOYED, True)
        put(TOKEN_COUNT, 0)

@public
def update(script: bytes, manifest: bytes):
    assert _is_contract_owner() and verify(), '`acccount` is not allowed for update'
    update_contract(script, manifest)

@public
def destroy():
    assert _is_contract_owner() and verify(), '`acccount` is not allowed for destroy'
    destroy_contract()

# -------------------------------------------
# NEP-11 Methods
# -------------------------------------------

@public(safe=True)
def symbol() -> str:
    return TOKEN_SYMBOL

@public(safe=True)
def decimals() -> int:
    return TOKEN_DECIMALS

@public(safe=True)
def totalSupply() -> int:
    return get(SUPPLY_PREFIX).to_int()

@public(safe=True)
def balanceOf(owner: UInt160) -> int:
    assert len(owner) == 20, "Incorrect `owner` length"
    assert owner != UInt160(), "Balance query for the zero address"
    return get(mk_balance_key(owner)).to_int()

@public(safe=True)
def tokensOf(owner: UInt160) -> Iterator:
    assert len(owner) == 20, "Incorrect `owner` length"
    flags = FindOptions.REMOVE_PREFIX | FindOptions.KEYS_ONLY
    context = get_context()
    return find(mk_account_key(owner), context, flags)

@public(safe=False)
def transfer(to: UInt160, tokenId: ByteString, data: Any) -> bool:
    token_id: int = tokenId.to_int()
    assert len(to) == 20, "Incorrect `to` length"
    assert to != UInt160(), "Transfer to the zero address"

    cutie_owner = get_owner_of(token_id)
    _transfer(cutie_owner, to, token_id)
    post_transfer(cutie_owner, to, token_id, data)
    return True

@public(safe=False)
def transfer_from(_from: UInt160, to: UInt160, tokenId: ByteString, data: Any) -> bool:
    token_id: int = tokenId.to_int()
    assert len(to) == 20, "Incorrect `to` length"
    assert to != UInt160(), "Transfer to the zero address"

    _transfer(_from, to, token_id)
    post_transfer(_from, to, token_id, data)
    return True

def post_transfer(token_owner: Union[UInt160, None], to: Union[UInt160, None], tokenId: int, data: Any):
    OnTransfer(token_owner, to, 1, cast(bytes, tokenId))
    if not isinstance(to, None):    # TODO: change to 'is not None' when `is` semantic is implemented
        contract = get_contract(to)
        if not isinstance(contract, None):      # TODO: change to 'is not None' when `is` semantic is implemented
            call_contract(to, 'onNEP11Payment', [token_owner, 1, tokenId, data])

@public()
def delegated_approve(address_from: UInt160, address_to: UInt160, token_id: int) -> None:
    put(b'testeggtwo', 'someone')
    assert _is_cutie_owner(token_id), 'Wrong cutie owner'
    put(b'testeggtwo', 'somevalue')
    put(APPROVALS_PREFIX + cast(bytes, token_id), address_to)

@public()
def cutie_witness(token_id: int) -> bool:
    return _is_cutie_owner(token_id)

@public()
def delegated_approve_test(text: bytes) -> None:
    put(b'testeggxxxx', 'someone')

@public
def onNEP11Payment(from_address: UInt160, amount: int, tokenId: bytes, data: Any):
    abort()

@public
def onNEP17Payment(from_address: UInt160, amount: int, data: Any):
    abort()

# -------------------------------------------
# Methods
# -------------------------------------------

@public
def create_cutie(
        owner: UInt160,
        mom_id: int,
        dad_id: int,
        generation: int,
        cooldown_index: int,
        genes: int,
        birth_time: int
) -> int:
    assert owner != UInt160(), 'Mint to the zero address'
    assert isGame() or isOwner(), "Access denied"

    return _mint(owner, mom_id, dad_id, generation, cooldown_index, genes, birth_time)

@public
def get_cutie(
        token_id: int,
) -> Dict[str, int]:
    assert _exists(token_id), 'Cutie not exists'

    metaBytes = get_meta(token_id)
    metaObject: Cutie = deserialize(metaBytes)

    cutie: Cutie = {
        'genes': metaObject['genes'],
        'birth_time': metaObject['birth_time'],
        'mom_id': metaObject['mom_id'],
        'dad_id': metaObject['dad_id'],
        'cooldown_end_time': metaObject['cooldown_end_time'],
        'cooldown_index': metaObject['cooldown_index'],
        'generation': metaObject['generation'],
    }

    return cutie

@public
def setGame(gameAddr: UInt160) -> None:
    put(ADDRESS_GAME, gameAddr)

@public
def setOwner(owner: UInt160) -> None:
    assert isOwner(), "Access denied"
    assert owner != UInt160(), 'Owner is null address'
    put(ADDRESS_OWNER, owner)

@public
def isOwner() -> bool:
    return _is_contract_owner()

@public
def isGame() -> bool:
    address: UInt160 = get(ADDRESS_GAME)
    if address == '':
        return False
    if calling_script_hash == address:
        return True
    return False


def _mint(
        owner: UInt160,
        mom_id: int,
        dad_id: int,
        generation: int,
        cooldown_index: int,
        genes: int,
        birth_time: int
) -> int:

    cutie = Cutie(genes, birth_time, 0, mom_id, dad_id, cooldown_index, generation, 0)
    tokenId = get(TOKEN_COUNT).to_int() + 1

    # Check if id can fit into 40 bits TODO: is that needed here? (taken from solidity logic)
    # require(id <= 0xFFFFFFFFFF, "Cutie population overflow");

    put(TOKEN_COUNT, tokenId)

    set_owner_of(tokenId, owner)
    set_balance(owner, 1)
    add_to_supply(1)
    add_meta(tokenId, cutie)
    add_token_account(owner, tokenId)
    post_transfer(None, owner, tokenId, None) # TODO: not sure what it does

    return tokenId

def _transfer(address_from: UInt160, address_to: UInt160, cutie_id: int):
    assert _is_cutie_owner(cutie_id), "Transfer of token that is not own"
    if (address_from != address_to):
        set_balance(address_from, -1)
        remove_token_account(address_from, cutie_id)
        _approve(cutie_id, UInt160())

        set_balance(address_to, 1)

        set_owner_of(cutie_id, address_to)
        add_token_account(address_to, cutie_id)

def _approved_for(spender: UInt160, cutie_id: int) -> bool:
    approved_address: UInt160 = get(APPROVALS_PREFIX + cast(bytes, cutie_id))
    return spender == approved_address

def _approve(cutie_id: int, approved: UInt160):
    put(APPROVALS_PREFIX + cast(bytes, cutie_id), approved)
    Approval(ownerOf(cutie_id), approved, cutie_id)

@public(safe=True)
def ownerOf(tokenId: int) -> UInt160:
    owner = get_owner_of(tokenId)
    assert owner != UInt160(), 'Owner query for nonexistent token'
    return owner

# def _contract_is_cutie_owner(token_id: int) -> bool:
#     owner: UInt160 = get_owner_of(token_id)
#     return owner == calling_script_hash
#
# def _sender_is_cutie_owner(token_id: int) -> bool:
#     tx = cast(Transaction, script_container)
#     owner: UInt160 = get_owner_of(token_id)
#     return owner == UInt160(tx.sender)

def _is_cutie_owner(token_id: int) -> bool:
    return check_witness(get_owner_of(token_id))

def remove_token_account(holder: UInt160, tokenId: int):
    key = mk_account_key(holder) + cast(bytes, tokenId)
    delete(key)

def add_token_account(holder: UInt160, tokenId: int):
    key = mk_account_key(holder) + cast(bytes, tokenId)
    put(key, tokenId)

def get_owner_of(tokenId: int) -> UInt160:
    key = mk_token_key(tokenId)
    owner = get(key)
    return UInt160(owner)

def set_owner_of(tokenId: int, owner: UInt160):
    key = mk_token_key(tokenId)
    put(key, owner)

def add_to_supply(amount: int):
    total = totalSupply() + (amount)
    put(SUPPLY_PREFIX, total)

def set_balance(owner: UInt160, amount: int):
    old = balanceOf(owner)
    new = old + (amount)

    key = mk_balance_key(owner)
    if (new > 0):
        put(key, new)
    else:
        delete(key)

def get_meta(tokenId: int) -> bytes:
    key = mk_meta_key(tokenId)
    return get(key)

def _exists(token_id: int) -> bool:
    metaBytes = get_meta(token_id)
    return len(metaBytes) != 0

def add_meta(tokenId: int, meta: Cutie):
    key = mk_meta_key(tokenId)
    put(key, serialize(meta))

## helpers

def get_operator_approval_key(owner: UInt160, spender: UInt160) -> bytes:
    return OPERATOR_APPROVALS_PREFIX + owner + b'_' + spender

def mk_account_key(address: UInt160) -> bytes:
    return ACCOUNT_PREFIX + address

def mk_balance_key(address: UInt160) -> bytes:
    return BALANCE_PREFIX + address

def mk_token_key(tokenId: int) -> bytes:
    return TOKEN_PREFIX + cast(bytes, tokenId)

def mk_meta_key(tokenId: int) -> bytes:
    return META_PREFIX + cast(bytes, tokenId)

def _is_contract_owner() -> bool:
    tx = cast(Transaction, script_container)
    address: UInt160 = get(ADDRESS_OWNER)
    if address == '':
        return False
    if tx.sender == address:
        return True
    return False