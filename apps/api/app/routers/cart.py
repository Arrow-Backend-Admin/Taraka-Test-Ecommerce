from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..schemas import CartItemAdd, CartItemUpdate, CartOut
from ..services.cart import (
    CART_COOKIE_MAX_AGE,
    CART_COOKIE_NAME,
    CART_COOKIE_PATH,
    CartNotFound,
    CartRuleError,
    add_item,
    cart_payload,
    create_cart,
    hash_client_ip,
    remove_item,
    require_cart,
    update_item,
)
from ..services.inventory import InventoryNotFound, OutOfStock
from ..services.publish import is_production

router = APIRouter(prefix="/cart", tags=["cart"])


def _respond(db: Session, cart) -> dict:
    return cart_payload(db, cart)


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, CartNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (OutOfStock, InventoryNotFound)):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, CartRuleError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="Cart error")


def _client_ip_hash(request: Request, settings: Settings) -> str | None:
    client = request.client.host if request.client else None
    return hash_client_ip(client, settings.cart_ip_hash_secret)


def _token(request: Request, header_token: str | None) -> str | None:
    """Prefer the httpOnly cookie; keep the header as a legacy/test fallback."""

    return request.cookies.get(CART_COOKIE_NAME) or header_token


def _set_cart_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        CART_COOKIE_NAME,
        raw_token,
        max_age=CART_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=is_production(),
        path=CART_COOKIE_PATH,
    )


@router.post("", response_model=CartOut, status_code=201)
def new_cart(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    cart, raw_token = create_cart(db, ip_hash=_client_ip_hash(request, settings))
    _set_cart_cookie(response, raw_token)
    return _respond(db, cart)


@router.get("", response_model=CartOut)
def read_cart(
    request: Request,
    response: Response,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _token(request, x_cart_token)
    try:
        cart = require_cart(db, token)
    except CartNotFound as exc:
        raise _handle(exc) from exc
    if token:
        _set_cart_cookie(response, token)
    return _respond(db, cart)


@router.delete("", status_code=204)
def delete_cart(response: Response) -> None:
    response.delete_cookie(CART_COOKIE_NAME, path=CART_COOKIE_PATH)


@router.post("/items", response_model=CartOut)
def add_cart_item(
    payload: CartItemAdd,
    request: Request,
    response: Response,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _token(request, x_cart_token)
    try:
        cart = require_cart(db, token)
        cart = add_item(db, cart, payload.sku, payload.quantity)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    if token:
        _set_cart_cookie(response, token)
    return _respond(db, cart)


@router.patch("/items/{item_id}", response_model=CartOut)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    request: Request,
    response: Response,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _token(request, x_cart_token)
    try:
        cart = require_cart(db, token)
        cart = update_item(db, cart, item_id, payload.quantity)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    if token:
        _set_cart_cookie(response, token)
    return _respond(db, cart)


@router.delete("/items/{item_id}", response_model=CartOut)
def delete_cart_item(
    item_id: int,
    request: Request,
    response: Response,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    token = _token(request, x_cart_token)
    try:
        cart = require_cart(db, token)
        cart = remove_item(db, cart, item_id)
    except (CartNotFound, CartRuleError, OutOfStock, InventoryNotFound) as exc:
        raise _handle(exc) from exc
    if token:
        _set_cart_cookie(response, token)
    return _respond(db, cart)
