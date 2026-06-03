from fastapi import FastAPI
 
app = FastAPI()
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