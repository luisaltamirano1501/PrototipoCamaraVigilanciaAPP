#librerias flask
from flask import Flask, render_template, request, url_for, redirect, session, flash, Response
from markupsafe import escape
from datetime import timedelta # libreria que crea lapsos de tiempo

## librerias de pymongoDB
from pymongo import MongoClient, InsertOne, UpdateOne, DeleteOne
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
import pandas as pd
from bson.son import SON
from pandas import ExcelWriter
from bson import json_util

#librerias para la funcion de la camara
import cv2
import time
import datetime
import json



#dirección
MOMGO_URI= "mongodb+srv://luis_rayh:jji3YFzkcQO2zyKh@pruebamongo.epav23g.mongodb.net/?retryWrites=true&w=majority"

# creación del cliente en MongoDB
client = MongoClient(MOMGO_URI)

#base de datos
db = client["proyecto_pagina"]

#coleccion
collection1 = db["camara"]
collection2 = db["cuentas"]

# Inicializar el clasificador de cascada de Haar
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#función dectector de rostro  
def detect_faces(frame):
    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar los rostros en la imagen
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Dibujar un rectángulo alrededor de cada rostro detectado
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    cantidadPersonas = len(faces)
    fecha = datetime.date.today()
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    
    return frame,cantidadPersonas,fecha,hora

def generate_video():
    # Iniciar la cámara
    cap = cv2.VideoCapture(0)

    tiempo_previo = time.time()
    while True:
        # Leer un frame de la cámara
        ret, frame = cap.read()

        # Detectar los rostros en el frame
        frame,cantidadPersonas,fecha,hora = detect_faces(frame)

        # Codificar el frame como JPEG
        ret, buffer = cv2.imencode('.jpg', frame)

        # Convertir el buffer codificado a bytes
        frame_bytes = buffer.tobytes()

        # Generar un frame de video
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

         # cada 5 segundos verifica los datos necesarios para la base da datos
        tiempo_actual = time.time()
        if tiempo_actual - tiempo_previo >= 5:
            tiempo_previo = tiempo_previo + 5  # Actualiza el tiempo previo para el siguiente intervalo de 5 segundos
            collection1.insert_one({"fecha":str(fecha),"hora":str(hora),"CantidadPersonas":cantidadPersonas})
    
def get_info():
    while True:
        registros = list(collection1.find().sort('_id', -1).limit(9))
        sesiones = list(collection2.find({},{"_id": 0, "sesiones": 1, "email" : 1}).sort('sesiones', -1).limit(10))

        return registros,sesiones
    

app = Flask(__name__, static_url_path='/static')# se define la aplicación
app.secret_key = "holamundo"
app.permanent_session_lifetime = timedelta(minutes = 5) # define el tiempo que dura una sesion de usuario 

#funcion para obtener camara 
@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/',methods=["GET","POST"]) # ruta por defecto de la app web
def index():
    if request.method == "POST":
        email = request.form["email"] # se obtiene el dato del formulario de la sesion en la pagina de html
        password = request.form["password"] # se obtiene el dato del formulario de la sesion en la pagina de html

        if (collection2.find({"email":email}) and email != "" and password != ""): # se ve si se relleno el formulario de la pagina html
            consulta = collection2.find_one({"email":email})
            
            if (collection2.find_one({"$and":[{"email":email},{"password":password}]})): # verifica si la contraseña y email existen
                session.permanent = True # valida el tiempo  que dura un sesion                                                 
                session["email"] = consulta["email"] # se crea la sesion
                session["password"] = consulta["password"]

                n_sesiones =  consulta["sesiones"]
                collection2.update_one({"email":email}, {'$set': {'sesiones':n_sesiones+1}})

                return redirect(url_for("user")) # se redirecciona a la pagina html que corresponde a la sesion del usuario
        
            else:
                return redirect(url_for("index"))
        
        else:
            return render_template("index.html") # se redirecciona a la pagina html que corresponde a la sesion del usuario

    else:
        if "email" in session:
            return redirect(url_for("user")) # si la sesion ya esta iniciada, se direccionara a la sesion del usuario
        else:
            return render_template("index.html") # en caso de no estar iniciada la sesion, se mandara a la pagina principal del login



@app.route('/user') # ruta por defecto de la app web
def user():
    if "email" in session:  # si el parametro de la sesion existe, se accede a la pagina del usuario
        return render_template("principal.html")
    else:
        return redirect(url_for("index")) 
    
@app.route("/log-out") # ruta al cerrar sesion
def log_out():
    session.pop("email",None)
    return redirect(url_for("index"))

      

@app.route('/principal',methods=["GET","POST"]) # ruta por defecto de la app web
def principal():
    registros,sesiones = get_info()

    registrosJSON,sesionesJSON = get_info()
    registrosJSON,sesionesJSON = json_util.dumps(registrosJSON),json_util.dumps(sesionesJSON)

    return render_template("principal.html",registros = registros, sesiones = sesiones,registrosJSON=registrosJSON,sesionesJSON=sesionesJSON)

@app.route('/video',methods=["GET","POST"]) # ruta por defecto de la app web
def video():
    #registros = get_info()

    return render_template("video.html")

@app.route('/grafica',methods=["GET","POST"]) # ruta por defecto de la app web
def grafica():
    registros,sesiones = get_info()

    registrosJSON,sesionesJSON = get_info()
    registrosJSON,sesionesJSON = json_util.dumps(registrosJSON),json_util.dumps(sesionesJSON)

    return render_template("grafica.html",registros = registros, sesiones = sesiones, registrosJSON = registrosJSON, sesionesJSON = sesionesJSON )

@app.route('/sesiones',methods=["GET","POST"]) # ruta por defecto de la app web
def sesiones():
    registros,sesiones = get_info()

    registrosJSON,sesionesJSON = get_info()
    registrosJSON,sesionesJSON = json_util.dumps(registrosJSON),json_util.dumps(sesionesJSON)

    return render_template("sesiones.html",registros = registros, sesiones = sesiones,registrosJSON=registrosJSON,sesionesJSON=sesionesJSON)


if __name__=='__main__': # verifica si esta la aplicación
    app.run(port=3000, debug=True)
