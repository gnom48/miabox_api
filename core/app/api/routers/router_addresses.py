from fastapi import APIRouter, Depends, HTTPException, status
from app.database.repositories import AddressesRepository
from app.api.models import Address, UserCredentials
from app.api.middlewares import get_user_from_request
from app.utils.osm import reverse_geocoding_by_coords

router_addresses = APIRouter(prefix="/addresses", tags=["Адреса"])

# GOOD: полностью исправно
# GOOD: соответствует потребностям приложения


@router_addresses.post("/", status_code=status.HTTP_201_CREATED)
async def add_address(
    address_info: Address,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    addresses_repository: AddressesRepository = Depends(
        AddressesRepository.repository_factory)
):
    if address_info.user_id != user_credentials.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not self account in address info")
    async with addresses_repository:
        if not address_info.address or address_info.address == "":
            try:
                address_info.address = await reverse_geocoding_by_coords()[
                    "display_name"]
            except Exception as e:
                address_info.address = "Не удалось получить адрес"
        address_id = await addresses_repository.add_address_info(address_info)
        if not address_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to add address info")
        return address_id


@router_addresses.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_addresses(
    user_id: str,
    date_start: int | None = None,
    date_end: int | None = None,
    user_credentials: UserCredentials = Depends(get_user_from_request),
    addresses_repository: AddressesRepository = Depends(
        AddressesRepository.repository_factory)
):
    async with addresses_repository:
        addresses = await addresses_repository.get_address_info_by_user_id(user_id, date_start, date_end)
        if addresses is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Addresses not found")
        return addresses
