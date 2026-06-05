from fastapi import FastAPI
from routers import auth # Import du routeur d'authentification
from database.session import init_db  
from users import routes
app = FastAPI(
    title="Mon api avec FastAPI pour la gestion d'une université",
    description="Cette API permet de gérer les cours, les étudiants, les enseignants et les départements d'une université.",
    version="0.0.1",
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
