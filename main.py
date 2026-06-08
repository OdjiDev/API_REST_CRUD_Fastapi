from fastapi import FastAPI
from routers import auth # Import du routeur d'authentification
from database.session import init_db  
from users import routes
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Mon api avec FastAPI pour la gestion d'une université",
    description="Cette API permet de gérer les cours, les étudiants, les enseignants et les départements d'une université.",
    version="0.0.1",
)



# 1. Définir les origines autorisées (ton frontend Angular)
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

# 2. Ajouter le middleware à l'application FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Autorise les requêtes provenant d'Angular
    allow_credentials=True,
    allow_methods=["*"],         # Autorise toutes les méthodes (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],         # Autorise tous les en-têtes (Content-Type, Authorization, etc.)
)
# On inclut le routeur d'authentification dans notre application principale
app.include_router(auth.router) 
@app.on_event("startup")
def on_startup():
    init_db()

# On inclut le module utilisateurs
app.include_router(routes.router)
@app.get("/")
async def home():
    return {"message": "Bienvenue sur l'API de gestion d'une université!"} 
