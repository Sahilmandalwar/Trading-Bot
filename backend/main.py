from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request  # notice how FastAPI written
from routes import price, signal, history, backtest, home

app = FastAPI()

app.include_router(home.router)
app.include_router(price.router)
app.include_router(signal.router)
app.include_router(history.router)
app.include_router(backtest.router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "message": "Route not found",
            "path": str(request.url)
        }
    )

