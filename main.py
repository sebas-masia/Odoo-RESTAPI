from fastapi import FastAPI, HTTPException, Query
import xmlrpc.client
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

load_dotenv()

app = FastAPI()

ODOO_URL = os.getenv('ODOO_URL')
DB_NAME = os.getenv('DB_NAME')
ODOO_USERNAME = os.getenv('ODOO_USERNAME')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(DB_NAME, ODOO_USERNAME, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

if not uid:
    raise HTTPException(status_code=401, detail="Authentication failed")


class Product(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    qty_available: Optional[int] = None
    category: Optional[str] = None


@app.get("/")
async def read_root():
    return {"Navigate to localhost:8000/docs to see the API documentation"}


@app.get("/products")
async def get_products(category: str = Query(None), variant: str = Query(None)):
    try:
        domain = []
        if category:
            domain.append(['categ_id.name', '=', category])
        if variant:
            domain.append(
                ['product_variant_ids.attribute_value_ids.name', '=', variant])

        products = models.execute_kw(
            DB_NAME, uid, ODOO_PASSWORD,
            'product.product', 'search_read',
            [domain],
            {'fields': ['name', 'default_code', 'list_price',
                        'qty_available', 'categ_id', 'product_variant_ids']}
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching products: {str(e)}")


@app.get("/products/{sku}")
async def get_product_by_sku(sku: str):
    try:
        product = models.execute_kw(
            DB_NAME, uid, ODOO_PASSWORD,
            'product.product', 'search_read',
            [[['default_code', '=', sku]]],
            {'fields': ['name', 'default_code', 'list_price', 'qty_available']}
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product[0]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching product: {str(e)}")


@app.post("/products/")
async def create_product(product: Product):
    try:
        # Fetch the category ID from the category name
        category_id = None
        if product.category:
            category = models.execute_kw(
                DB_NAME, uid, ODOO_PASSWORD,
                'product.category', 'search_read',
                [[('name', '=', product.category)]],
                {'fields': ['id'], 'limit': 1}
            )
            if category:
                category_id = category[0]['id']
            else:
                raise HTTPException(status_code=404, detail=f"Category '{
                                    product.category}' not found")

        # Create the new product template in Odoo (without variant logic)
        product_id = models.execute_kw(
            DB_NAME, uid, ODOO_PASSWORD,
            # Use 'product.template' for creating the product template
            'product.template', 'create',
            [{
                'name': product.name,
                'default_code': product.sku,  # Set the SKU
                'list_price': product.price,
                'categ_id': category_id,  # Use the category ID
                'qty_available': product.qty_available  # Set the available quantity
            }]
        )
        return {"message": "Product created", "product_id": product_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating product: {e}")


@app.put("/products/{sku}")
async def update_product(sku: str, product: Product):
    try:
        # Find the product template ID to update using the SKU
        product_template_ids = models.execute_kw(
            DB_NAME, uid, ODOO_PASSWORD,
            'product.template', 'search',
            [[('default_code', '=', sku)]]
        )
        if not product_template_ids:
            raise HTTPException(status_code=404, detail="Product not found")

        # Prepare the values to update
        update_values = {}

        # Only include fields in update_values if they are provided
        if product.name:
            update_values['name'] = product.name
        if product.price:
            update_values['list_price'] = product.price
        if product.qty_available is not None:
            update_values['qty_available'] = product.qty_available

        # Handle category update if provided
        if product.category:
            category = models.execute_kw(
                DB_NAME, uid, ODOO_PASSWORD,
                'product.category', 'search_read',
                [[('name', '=', product.category)]],
                {'fields': ['id'], 'limit': 1}
            )
            if category:
                update_values['categ_id'] = category[0]['id']
            else:
                raise HTTPException(status_code=404, detail=f"Category '{
                                    product.category}' not found")

        # Check if there are fields to update
        if not update_values:
            raise HTTPException(
                status_code=400, detail="No valid fields provided for update.")

        # Update the product template in Odoo
        models.execute_kw(
            DB_NAME, uid, ODOO_PASSWORD,
            'product.template', 'write',
            [product_template_ids, update_values]
        )
        return {"message": "Product updated"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating product: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
