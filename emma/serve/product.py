from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from serve.db import Product, db
import redis
import dotenv
import os
from serve.model import ProductRequest, StandardResponse
from typing import List
from peewee import IntegrityError

dotenv.load_dotenv()

router = APIRouter()


@router.post("/ecommerce/product", response_model=StandardResponse)
async def create_update_new_products(products: List[ProductRequest]):
    try:
        with db.atomic():
            data = [product.model_dump() for product in products]
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                Product.insert_many(batch).on_conflict(
                    conflict_target=[Product.pid],
                    update={
                        Product.name: Product.name,
                        Product.brief: Product.brief,
                        Product.description: Product.description,
                        Product.price: Product.price,
                        Product.meta: Product.meta
                    }
                ).execute()

        return StandardResponse(
            status=200,
            resp={
                "message": f"Successfully created {len(products)} products",
                "data": {"created_count": len(products)}
            }
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating products: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


def init_app(app):
    app.include_router(router)
