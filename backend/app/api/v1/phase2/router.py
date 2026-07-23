from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import (
    get_create_coupon,
    get_current_user_id,
    get_enroll_mfa,
    get_process_payment,
    get_update_inventory,
    get_upload_image,
    get_user_profile,
    get_verify_mfa,
    require_staff,
)
from app.application.commands.phase2 import (
    CreateCouponUseCase,
    EnrollMfaUseCase,
    ProcessPaymentUseCase,
    UpdateInventoryUseCase,
    UploadProductImageUseCase,
    VerifyMfaUseCase,
)
from app.application.commands.users import GetUserProfileUseCase
from app.application.dto.schemas import (
    CouponOutput,
    CreateCouponInput,
    CreatePaymentInput,
    MfaEnrollOutput,
    MfaVerifyInput,
    PaymentOutput,
    UpdateInventoryInput,
)

router = APIRouter(tags=["Phase 2"])


@router.post("/coupons", response_model=CouponOutput, status_code=201, dependencies=[Depends(require_staff)])
async def create_coupon(
    data: CreateCouponInput,
    use_case: CreateCouponUseCase = Depends(get_create_coupon),
):
    return await use_case.execute(data)


@router.put("/inventory", dependencies=[Depends(require_staff)])
async def update_inventory(
    data: UpdateInventoryInput,
    use_case: UpdateInventoryUseCase = Depends(get_update_inventory),
):
    return await use_case.execute(data)


@router.post("/payments", response_model=PaymentOutput, status_code=201)
async def create_payment(
    data: CreatePaymentInput,
    user_id: UUID = Depends(get_current_user_id),
    profile_uc: GetUserProfileUseCase = Depends(get_user_profile),
    use_case: ProcessPaymentUseCase = Depends(get_process_payment),
):
    profile = await profile_uc.execute(user_id)
    return await use_case.execute(data, customer_email=profile.email)


@router.post("/products/{product_id}/upload", dependencies=[Depends(require_staff)])
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    use_case: UploadProductImageUseCase = Depends(get_upload_image),
):
    data = await file.read()
    return await use_case.execute(
        product_id=str(product_id),
        filename=file.filename or "image.jpg",
        data=data,
        content_type=file.content_type or "image/jpeg",
    )


@router.post("/auth/mfa/enroll", response_model=MfaEnrollOutput)
async def enroll_mfa(
    user_id: UUID = Depends(get_current_user_id),
    use_case: EnrollMfaUseCase = Depends(get_enroll_mfa),
):
    return await use_case.execute(user_id)


@router.post("/auth/mfa/verify")
async def verify_mfa(
    data: MfaVerifyInput,
    user_id: UUID = Depends(get_current_user_id),
    use_case: VerifyMfaUseCase = Depends(get_verify_mfa),
):
    return await use_case.execute(user_id, data)
