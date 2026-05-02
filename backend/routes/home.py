from fastapi import APIRouter

router = APIRouter()

@router.get("/")    # home route
def home():
    return {"message": "Trading bot API running..."}
    