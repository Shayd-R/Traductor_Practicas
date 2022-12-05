from config.database import db
from datetime import date, datetime
from config import settings
from email.message import EmailMessage
from smtplib import SMTP
from os import remove

from flask import url_for

def correoExistente(email):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    cuenta = cursor.fetchone()
    cursor.close()
    return cuenta

def resgistrarUsuario(nombre, email, password, token):
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO usuarios(nombre, email, password, token) VALUES (%s, %s, %s, %s)",
        (
            nombre,
            email,
            password,
            token,
        ),
    )       
    cursor.close()
   
def nombreImagen(imagen):
    today = date.today()
    now = datetime.now()
    fecha= str(today)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
    nombreImagen = imagen.filename
    return str(fecha) + nombreImagen

def correoVerificacion(email, link):
    msg = EmailMessage()
    msg.set_content("Confirmar tu correo aqui: {} ".format(link))
    msg["Subject"] = "Registro en Foodrosif"
    msg["From"] = "shaydruano2020@itp.edu.co"
    msg["To"] = email
    username = "shaydruano2020@itp.edu.co"
    password = "1006663258"  
    server = SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()

def correoRestablecerPassword(email, link_password):
    msg = EmailMessage()
    msg.set_content("Para restablecer tu contraseña ingresa al siguiente link (Tiempo limite 2 min) : {} ".format(link_password))
    msg["Subject"] = "Recuperar contraseña"
    msg["From"] = "shaydruano2020@itp.edu.co"
    msg["To"] = email
    username = "shaydruano2020@itp.edu.co"
    password = "1006663258"  
    server = SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()

def cambioPassword(email, passwordencriptada):
    cursor = db.cursor(dictionary=True)
    cursor.execute("UPDATE usuarios SET contraseña=%s WHERE email=%s",
    (
        passwordencriptada,
        email,
    ))
    cursor.close()

def editarFrase(id, frase, traduccion, imagenn):
    imagen_sql=''
    if imagenn:
        imagen_sql=", imagen= '"+imagenn+"'"
        sql = " frase_español= '"+frase+"', traduccion = '"+traduccion+"'" + imagen_sql + " WHERE id_contribuccion = '"+id+"'"
    elif imagenn is None:
        sql = " frase_español= '"+frase+"', traduccion = '"+traduccion+"'" + imagen_sql + " WHERE id_contribuccion = '"+id+"'"
    cursor = db.cursor()    
    cursor.execute("UPDATE contribucciones SET " + sql)
    db.commit()

def eliminarFrase(id_frase):
    cursor = db.cursor()  
    cursor.execute("SELECT * FROM contribucciones WHERE id_contribuccion="+id_frase)
    imagen = cursor.fetchone()
    remove('./static/img/frases_categoria/'+str(imagen[3]))
    cursor.execute("DELETE FROM contribucciones WHERE id_contribuccion="+id_frase)
    db.commit()

def verificarFrase(id_frase):
    cursor = db.cursor()  
    cursor.execute("UPDATE contribucciones SET confirmacion='si' WHERE id_contribuccion= "+str(id_frase))
    db.commit()

def editarCategoria(idcategoria, categoria, imagenn):
    imagen_sql=''
    if imagenn:
        imagen_sql=", imagen_categoria= '"+imagenn+"'"
        sql = " nombre_categoria= '"+categoria+"'" + imagen_sql + " WHERE id_categoria = '"+idcategoria+"'"
    elif imagenn is None:
        sql = " nombre_categoria= '"+categoria+"'" + imagen_sql + " WHERE id_categoria = '"+idcategoria+"'"
    cursor = db.cursor()   
    cursor.execute("UPDATE categorias SET " + sql)
    db.commit()

def eliminarCategoria(id_categoria):
    cursor = db.cursor()  
    cursor.execute("SELECT * FROM categorias WHERE id_categoria="+id_categoria)
    imagen = cursor.fetchone()
    remove('./static/img/categorias/'+str(imagen[2]))
    cursor.execute("DELETE FROM categorias WHERE id_categoria="+id_categoria)
    db.commit()

