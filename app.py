from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from datetime import datetime
import logging
from pythonjsonlogger.json import JsonFormatter
import os


class OrderCreate(BaseModel):
    username: str
    product_name: str
    quantity: int

    @field_validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


### Структура контейнера для заказов (вместо отдельной БД)
# orders = [
#     {
#      "username": str,
#      "product_name: str,
#      "quantity": int,
#      "created_at": str
#     }
# ]
orders: list[dict[str, str | int]] = []

# Настройка логгера
logger = logging.getLogger("app")

formatter = JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.getenv("LOG_LEVEL", logging.INFO))
logger.propagate = False


app = FastAPI()
logger.info("The app has just started")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Hello this is test app!"
    }

@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy"
    }


@app.post("/orders")
async def post_order(order: OrderCreate) -> dict[str, int]:
    created_at: str = str(datetime.now())
    order_id: int = len(orders) + 1

    orders.append({
        "username": order.username,
        "product_name": order.product_name,
        "quantity": order.quantity,
        "created_at": created_at
    })

    logger.info(
        msg="Order successfully created",
        extra={
            "order_id": order_id,
            "username": order.username,
            "product_name": order.product_name,
            "quantity": order.quantity,
            "created_at": created_at
        }
    )

    return {
        "order_id": order_id
    }


@app.get("/order/{order_id}")
async def get_order(order_id: int):

    if 0 < order_id <= len(orders):
        logger.info(
            msg="Order successfully retrieved",
            extra={
                "order_id": order_id
            }
        )

        return {
            "id": order_id,
            "created_at": orders[order_id-1].get("created_at")
        }

    logger.warning(
        msg="Order not found",
        extra={
            "order_id": order_id
        }
    )

    raise HTTPException(
        status_code=404,
        detail="Not found"
    )
