from fastapi import FastAPI
 
app = FastAPI(
    title="Mon api avec FastAPI pour la gestion d'une université",
    description="Cette API permet de gérer les cours, les étudiants, les enseignants et les départements d'une université.",
    version="0.0.1",
)
@app.get("/")
def home():
    return {"Hello": "World"}
@app.get("/cours")
def cours():
    return {"cours": "FastAPI"}
@app.get("/etudiants")
def etudiants():
    return {"Noombre d'etudiants": "100"}
@app.get("/enseignants")
def enseignants():
    return {"enseignants": "DJIRE OUZAIROU"}
@app.get("/departements")
def departements():
    return {"departements": "Informatique"}
@app.get("/api/v1/utilisateurs")    
def utilisateurs():
    return {"utilisateurs": "1000"}