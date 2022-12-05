
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, json, make_response
from hashlib import sha256
from models import voz_traductor, traduccion_texto, userModel, crearCategoria, existeCategoria, crearFrase
from controllers import loginController, registroController, confirmarToken, restablecerPassword, cambiarPassword, autenticacionController
from config.database import db

app = Flask(__name__)
app.secret_key = "##91!IasdyAjadfbdfan"


@app.route("/", methods=["GET", "POST"])
def inicio():
    return render_template("/inicio/inicio.html")


@app.route("/inicio_session", methods=["GET", "POST"])
def inicio_session():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if loginController.login(email, password) == True:
            return redirect(url_for('muro'))
        else:
            return render_template("/inicio_session/inicio_session.html")
    return render_template("/inicio_session/inicio_session.html")


@app.get("/exit")
def exit():
    if autenticacionController.vericarAutenticacion():
        session.clear()
    return redirect(url_for('inicio_session'))


@app.route("/muro", methods=["GET", "POST"])
def muro():
    if autenticacionController.vericarAutenticacion():
        nombre = session['name']
        rol = session['rol']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM categorias")
        categorias = cursor.fetchall()
        return render_template("menu/menu.html", nombre=nombre, rol=rol, categorias=categorias)
    else:
        return redirect(url_for('inicio'))


@app.route("/frasesCategoria/<string:id>/<string:nombre>", methods=["GET", "POST"])
def frases(id, nombre):
    cursor = db.cursor()
    if autenticacionController.vericarAutenticacion():
        name = session['name']
        rol = session['rol']
        cursor.execute("SELECT * FROM contribucciones WHERE id_categoria= "+id+" and confirmacion='si' ")
        frases_categorias = cursor.fetchall()
        print(frases_categorias)
        return render_template("menu/categorias.html", nombre_categoria=nombre, id=id, name=name, rol=rol, frases_categoria=frases_categorias)
    else:
        return redirect(url_for('inicio'))


@app.route("/registrarUsuario", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        if registroController.registro(nombre, email, password) == True:
            flash("Confirma tu correo")
        else:
            return render_template("/registro/registro.html", nombre=nombre, email=email)
    return render_template("/registro/registro.html")


@app.route("/crearCategoria", methods=["GET", "POST"])
def crear_categoria():
    if request.method == 'GET':
        return render_template('/menu/menu.html')

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        if nombre == "":
            flash("El campo nombre esta vacio", "error")
            return redirect(url_for('muro'))
        imagen = request.files.get('imagen')
        resultado = existeCategoria.existe(nombre)
        if resultado:
            flash("Ya existe esta categoria", "error")
            return redirect(url_for('muro'))
        img = userModel.nombreImagen(imagen)
        crearCategoria.crear(nombre=nombre, imagen=img)
        print(nombre)
        imagen.save('./static/img/categorias/'+str(img))
        flash("Se ha creado la categoria: "+nombre, 'bueno')
    return redirect(url_for('muro'))


@app.route("/restorePassword", methods=["GET", "POST"])
def restorePassword():
    if autenticacionController.vericarAutenticacion():
        if request.method == 'POST':
            email = request.form['email']
            if restablecerPassword.restablecer(email):
                return redirect(url_for('inicio'))
        return render_template("/correo_restablecer_contraseña/correoRestablecerPassword.html")
    else:
        return render_template("/correo_restablecer_contraseña/correoRestablecerPassword.html")


@app.get("/cambiarPass/<id>/<token>")
def cambiarPass(id, token):
    if confirmarToken.validateIdToken(id, token) == True:
        return render_template("/restablecer_contraseña/restablecer_password.html", id=id)
    else:
        return redirect(url_for('inicio_session'))


@app.post("/newPassword")
def newPassword():
    if request.method == 'POST':
        id = request.form.get("id")
        session['token'] = id
        password = request.form.get("password")
        password_verificacion = request.form.get("password_verificacion")
        if password == password_verificacion:
            if confirmarToken.validateToken(id):
                cambiarPassword.cambiar(id, password)
                return redirect(url_for('inicio_session'))
    return render_template("/restablecer_contraseña/restablecer_password.html")


@app.route("/confirmarToken/<token>", methods=["GET", "POST"])
def authToken(token):
    if confirmarToken.valToken(token) == True:
        return redirect(url_for('inicio_session'))
    else:
        return redirect(url_for('inicio_session'))


@app.route("/traductor", methods=["GET", "POST"])
def traductor():
    return render_template("/traductor/traductor.html")


@app.route("/traduccion", methods=["GET", "POST"])
def traduccion():
    if request.method == 'POST':
        texto_entrada = request.form['texto_entrada']
        texto = texto_entrada.split()
        traducido = []
        for palabra in texto:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM palabras_espanol WHERE palabra_espanol='" +palabra+"' OR palabra_espanol LIKE '%"+palabra+"%' ")
            a = cursor.fetchone()
            if a == None:
                a = palabra
            else:
                a = a['palabra a palabra']
            traducido.append(a)
            db.commit()
        texto_salida = traduccion_texto.concatenar_palabras(traducido, "  ")
        return render_template("/traductor/traductor.html", texto_salida=texto_salida, texto_entrada=texto_entrada)
    return render_template("/traductor/traductor.html")


@app.route("/voz", methods=["GET", "POST"])
def audio():
    texto_entrada = request.form['texto_entrada']
    texto = texto_entrada.split()
    traducido = []
    for palabra in texto:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM palabras_espanol WHERE palabra_espanol='" +palabra+"' OR palabra_espanol LIKE '%"+palabra+"%' ")
        a = cursor.fetchone()
        if a == None:
            a = palabra
        else:
            a = a['palabra a palabra']
        traducido.append(a)
        db.commit()
        texto_salida = traduccion_texto.concatenar_palabras(traducido, "  ")
    voz_traductor.voz_texto(texto_salida)
    return render_template("/traductor/traductor.html", texto_entrada=texto_entrada, texto_salida=texto_salida)


@app.route("/crearFrase/<string:id>/<string:nombre>", methods=["GET", "POST"])
def crear_frase(id, nombre):
    if request.method == 'GET':
        return render_template('/menu/categorias.html')

    if request.method == 'POST':
        frase = request.form.get('frase')
        if frase == "":
            flash("El campo frase esta vacio", "error")
            return redirect(url_for('frases', id=id, nombre=nombre))
        traduccion = request.form.get('traduccion')
        if traduccion == "":
            flash("El campo traduccion esta vacio", "error")
            return redirect(url_for('frases', id=id, nombre=nombre))
        id_usuario = session['id_usuario']
        imagen = request.files.get('imagen')
        resultado = existeCategoria.existe(frase)
        if resultado:
            flash("Ya existe esta frase", "error")
            return redirect(url_for('frases', id=id, nombre=nombre))
        img = userModel.nombreImagen(imagen)
        crearFrase.crear(id_categoria=id, frase=frase,traduccion=traduccion, imagen=img, id_usuario=id_usuario)
        imagen.save('./static/img/frases_categoria/'+str(img))
        flash("La frase '"+frase+"' estara en verificacion ", 'verificacion')
    return redirect(url_for('frases', id=id, nombre=nombre))

@app.route('/editarFrase/<string:id_frase>/<string:id>/<string:nombre>', methods=['GET', 'POST'])
def editar_frase(id_frase, id, nombre):
    if autenticacionController.vericarAutenticacion():
        frase = request.form['frase']
        traduccion = request.form['traduccion']
        imagen = request.files['imagen']
        if imagen:
            nombreImagen = userModel.nombreImagen(imagen)
            imagenn = nombreImagen
            imagen.save('./static/img/frases_categoria/'+nombreImagen)
        else:
            imagenn = None
        userModel.editarFrase(frase=frase, traduccion=traduccion, imagenn=imagenn, id=id_frase)
        flash('Se ha editado la frase correctamente','bueno')
        return redirect(url_for('frases', id=id, nombre=nombre))
    else:
        return redirect(url_for('inicio'))

@app.route('/eliminarFrase/<string:id_frase>/<string:id>/<string:nombre>', methods=['GET', 'POST'])
def eliminar_frase(id_frase, id, nombre):
    if autenticacionController.vericarAutenticacion(): 
        userModel.eliminarFrase(id_frase=id_frase)
        
        flash('Se ha eliminado la frase correctamente', 'error')
        return redirect(url_for('frases', id=id, nombre=nombre))
    else:
        return redirect(url_for('inicio'))    

@app.route("/ajaxfile", methods=["GET", "POST"])
def ajaxfile():
    cursor = db.cursor()
    if request.method=='POST':
        fraseid=request.form['fraseid']
        id=request.form['id']
        nombre=request.form['nombre']
        cursor.execute(
            "SELECT * FROM contribucciones WHERE id_contribuccion= "+fraseid)
        frase = cursor.fetchall()
        print(fraseid)
    return jsonify({'htmlresponse': render_template('menu/response.html', frase=frase, nombre=nombre, id=id)})

@app.route("/verificacionContribuyente", methods=["GET", "POST"])
def verificacionContribuyente():
    cursor = db.cursor()
    if autenticacionController.vericarAutenticacion():
        name = session['name']
        rol = session['rol']
        cursor.execute("""
            SELECT 
                `contribucciones`.`id_contribuccion`,
                `usuarios`.`nombre`,
                `contribucciones`.`frase_español`,
                `contribucciones`.`traduccion`,
                `categorias`.`nombre_categoria`,
                `contribucciones`.`imagen`,
                `contribucciones`.`confirmacion`
            FROM `traductor`.`contribucciones`
                INNER JOIN `traductor`.`categorias`
                    ON (   `contribucciones`.`id_categoria` = `categorias`.`id_categoria`
                    )
                INNER JOIN `traductor`.`usuarios`
                    ON (
                    `contribucciones`.`id_usuario` = `usuarios`.`id_usuario`
                    )
            WHERE contribucciones.`confirmacion`='No'
        """)
        frases_categorias = cursor.fetchall()
        print(frases_categorias)
        return render_template("menu/verificacionContribucciones.html", name=name, rol=rol, frases_categoria=frases_categorias)
    else:
        return redirect(url_for('inicio'))
    
app.run(debug=True)
