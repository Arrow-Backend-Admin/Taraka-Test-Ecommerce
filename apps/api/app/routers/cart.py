from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import CartItemAdd, CartItemUpdate, CartOut
from ..services.cart import (
    CartNotFound,
    CartRuleError,
    add_item,
    cart_payload,
    create_cart,
    remove_item,
    require_cart,
    update_item,
)
from ..services.inventory import InventoryNotFound, OutOfStock

router = APIRouter(prefix="/cart", tags=["cart"])


def _respond(cart) -> dict:
    return cart_payload(cart)


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, CartNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (OutOfStock, InventoryNotFound)):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, CartRuleError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="Cart error")


@router.post("", response_model=CartOut, status_code=201)
def new_cart(db: Session = Depends(get_db)) -> dict:
    return _respond(create_cart(db))


@router.get("", response_model=CartOut)
def read_cart(
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        cart = require_cart(db, x_cart_token)
    except CartNotFound as exc:
        raise _handle(exc) from exc
    return _respond(cart)


@router.post("/items", response_model=CartOut)
def add_cart_item(
    payload: CartItemAdd,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        cart = require_cart(db, x_cart_token)
        cart = add_item(db, cart, payload.sku, payload.quantity)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    return _respond(cart)


@router.patch("/items/{item_id}", response_model=CartOut)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        cart = require_cart(db, x_cart_token)
        cart = update_item(db, cart, item_id, payload.quantity)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    return _respond(cart)


@router.delete("/items/{item_id}", response_model=CartOut)
def delete_cart_item(
    item_id: int,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    try:
        cart = require_cart(db, x_cart_token)
        cart = remove_item(db, cart, item_id)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    return _respond(cart)
