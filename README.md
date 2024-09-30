
# FastAPI Odoo Inventory Management API

This project is a FastAPI-based API that allows interaction with the Odoo inventory module to manage products. It supports basic CRUD operations (Create, Read, Update) for products in the Odoo inventory.

## Features

- **Get all products** with optional filtering by category.
- **Get a product by SKU** to view detailed information.
- **Create a new product** in Odoo without variants.
- **Update an existing product** partially, updating only the provided fields.
- Utilizes XML-RPC to communicate with Odoo's backend.

## Prerequisites

- Python 3.7 or higher
- Odoo instance with an active inventory module
- Access to the Odoo instance's URL, database name, username, and password
- `pip` for installing Python dependencies

## Installation

1. Clone the repository and navigate to the project directory:

    ```bash
    git clone https://github.com/sebas-masia/Odoo-RESTAPI.git
    cd odoo_inventory_api
    ```

2. Create a virtual environment and activate it:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```bash
    pip install fastapi uvicorn python-dotenv
    ```

4. Create a `.env` file in the root directory of the project to store your Odoo credentials:

    ```env
    ODOO_URL=<your_odoo_instance_url>
    DB_NAME=<your_database_name>
    ODOO_USERNAME=<your_odoo_username>
    ODOO_PASSWORD=<your_odoo_password>
    ```

## Running the Application

1. Start the FastAPI application using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

2. The application will be accessible at `http://127.0.0.1:8000`.

3. Visit `http://127.0.0.1:8000/docs` to see the automatically generated API documentation.

## API Endpoints

### 1. Get All Products
- **Endpoint:** `/products`
- **Method:** `GET`
- **Query Parameters:**
  - `category` (optional): Filter products by category name.
- **Response:** List of products.

### 2. Get a Product by SKU
- **Endpoint:** `/products/{sku}`
- **Method:** `GET`
- **Path Parameter:** `sku` (string) - The SKU of the product to retrieve.
- **Response:** Product details.

### 3. Create a Product
- **Endpoint:** `/products/`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
      "name": "Product Name",
      "sku": "SKU123",
      "price": 100.0,
      "qty_available": 50,
      "category": "Category Name"
    }
    ```
- **Response:** Message confirming product creation.

### 4. Update a Product
- **Endpoint:** `/products/{sku}`
- **Method:** `PUT`
- **Path Parameter:** `sku` (string) - The SKU of the product to update.
- **Request Body:** (Partial update, only include fields to be updated)
    ```json
    {
      "name": "Updated Product Name",
      "price": 120.0,
      "qty_available": 60,
      "category": "New Category Name"
    }
    ```
- **Response:** Message confirming product update.

## Notes

- The application uses the Odoo XML-RPC API to interact with the Odoo instance.
- Fields for update operations are optional, allowing partial updates.
- Ensure the Odoo instance has the necessary modules installed and proper access rights for the user.

## Error Handling

- Returns a `400 Bad Request` error if no valid fields are provided for update.
- Returns a `404 Not Found` error if a specified product, category, or SKU does not exist.
- Returns a `500 Internal Server Error` for server-related issues.

## License

This project is licensed under the MIT License.
