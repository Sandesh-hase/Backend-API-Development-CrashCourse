# FastAPI Project

This is a FastAPI-based project that provides a simple API for managing posts. The API allows you to create, read, update, and delete posts, as well as perform batch insertions.

## Features
- **Create Post**: Add a new post to the database.
- **Get All Posts**: Retrieve all posts from the database.
- **Get Latest Post**: Retrieve the most recent post.
- **Get Post by ID**: Retrieve a specific post by its ID.
- **Update Post**: Update an existing post by its ID.
- **Delete Post**: Remove a post by its ID.
- **Insert Many Posts**: Add multiple posts at once.

## Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**:
   Make sure you have Python installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the API**:
   Open your browser and go to `http://127.0.0.1:8000/docs` to view the interactive API documentation.

## Usage
- Use the interactive API documentation to test the endpoints.
- Integrate the API with your frontend or other services as needed.

## Note
- Ensure your database is running and accessible by the application.
- Adjust the database connection settings in the `app/database.py` file if necessary. 