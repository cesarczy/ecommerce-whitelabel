from uuid import UUID

from fastapi import APIRouter, Depends, Header

from app.api.deps import get_add_to_cart, get_cart, get_checkout, get_current_user_id, get_optional_user_id
from app.application.commands.cart import AddToCartUseCase, CheckoutUseCase, GetCartUseCase
from app.application.dto.schemas import AddToCartInput, CartOutput, CheckoutInput, OrderOutput

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/cart/items", response_model=CartOutput)
async def add_to_cart(
    data: AddToCartInput,
    user_id: UUID | None = Depends(get_optional_user_id),
    use_case: AddToCartUseCase = Depends(get_add_to_cart),
):
    return await use_case.execute(data, customer_id=user_id)


@router.get("/cart/{cart_id}", response_model=CartOutput)
async def get_cart(cart_id: UUID, use_case: GetCartUseCase = Depends(get_cart)):
    return await use_case.execute(cart_id=cart_id)


@router.post("/checkout", response_model=OrderOutput, status_code=201)
async def checkout(
    data: CheckoutInput,
    user_id: UUID = Depends(get_current_user_id),
    use_case: CheckoutUseCase = Depends(get_checkout),
):
    return await use_case.execute(user_id, data)
