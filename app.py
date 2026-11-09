import os
import uuid
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

app = Flask(__name__)


# Token de autenticación de DataStax Astra
ASTRA_TOKEN = os.environ.get('ASTRA_APPLICATION_TOKEN')

BUNDLE_PATH = os.path.join(
    os.path.dirname(__file__),
    'secure-connect-bundle.zip'
)

# Conexión al cluster
cloud_config = {
    'secure_connect_bundle': BUNDLE_PATH
}

auth_provider = PlainTextAuthProvider(
    'token',
    ASTRA_TOKEN
)

cluster = Cluster(
    cloud=cloud_config,
    auth_provider=auth_provider
)

session = cluster.connect()
session.set_keyspace('practica_cassandra')

# Sentencia preparada para optimizar escrituras concurrentes
stmt = session.prepare("INSERT INTO usuarios (id, nombre, fecha) VALUES (?, ?, ?)")

@app.route('/', methods=['GET'])
def index():
    mensaje = request.args.get('mensaje')
    return render_template('index.html', mensaje=mensaje)

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form.get('nombre')
    if nombre:
        nuevo_id = uuid.uuid4()
        fecha_actual = datetime.utcnow()
        session.execute(stmt, (nuevo_id, nombre, fecha_actual))
    return redirect(url_for('index', mensaje="¡Registro guardado exitosamente!"))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)