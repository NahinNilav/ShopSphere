from app.routers import products, categories, brands, carts, users, auth, accounts
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.cloudinary_config import initialize_cloudinary
from app.core.config import settings
from app.routers import wishlists 
from app.routers import feedback
from app.routers import orders
from app.routers import search

# Initialize Cloudinary
# initialize_cloudinary()



app = FastAPI(
    title="App API",
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "layout": "BaseLayout",
        "filter": True,
        "tryItOutEnabled": True,
        "onComplete": "Ok"
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.NGROK_URL], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount the uploads directory to serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.include_router(products.router)
app.include_router(categories.router)
app.include_router(brands.router)
app.include_router(carts.router)
app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(auth.router)
app.include_router(wishlists.router)


app.include_router(feedback.router)
app.include_router(orders.router)
app.include_router(search.router)