from flask import Flask, render_template, request, redirect, url_for, flash
import werkzeug
from db import get_db, query_db, init_db, close_connection
import locale
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.teardown_appcontext
def close_connection_on_teardown(exception):
    close_connection(exception)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/informe_stock')
def informe_stock():
    return render_template('informe_stock.html')

@app.route('/actualizar_eliminar_consultar')
def actualizar_eliminar_consultar():
    return render_template('actualizar_eliminar_consultar.html')

# CONSULTAR PRODUCTO

@app.route('/consultar_producto', methods=['GET', 'POST'])
def consultar_producto():
    if request.method == 'POST':
        producto_nombre = request.form['producto_nombre']
        producto_info = query_producto_info(producto_nombre)
        if producto_info:
            return render_template('consultar_producto.html', producto_info=producto_info, productos=query_db('SELECT nombre FROM productos'))
        else:
            flash('Producto no encontrado. Opcion(Ha eliminado el nombre de categoria o proveedor o bodega. Tienes que actualizar)', 'danger')  # Mensaje flash si el producto no se encuentra
            return redirect (url_for('index'))
    productos = query_db('SELECT nombre FROM productos')
    return render_template('consultar_producto.html', productos=productos)


def query_producto_info(nombre_producto):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('SELECT nombre, descripcion, precio, stock, categoria_nombre, proveedor_nombre, bodega_nombre FROM productos WHERE nombre = ?', (nombre_producto,))
        producto_info = cursor.fetchone()
        if producto_info:
            categoria_nombre = producto_info['categoria_nombre']
            proveedor_nombre = producto_info['proveedor_nombre']
            bodega_nombre = producto_info['bodega_nombre']
            categoria = query_db('SELECT nombre FROM categorias WHERE nombre = ?', (categoria_nombre,), one=True)
            proveedor = query_db('SELECT nombre FROM proveedores WHERE nombre = ?', (proveedor_nombre,), one=True)
            bodega = query_db('SELECT nombre FROM bodegas WHERE nombre = ?', (bodega_nombre,), one=True)
            if categoria and proveedor and bodega:
                return {
                    'nombre': producto_info['nombre'],
                    'descripcion': producto_info['descripcion'],
                    'precio': producto_info['precio'],
                    'stock': producto_info['stock'],
                    'categoria': categoria[0],  
                    'proveedor': proveedor[0], 
                    'bodega': bodega[0]
                }
    except Exception as e:
        flash('Error al consultar el producto: {}'.format(str(e)), 'danger')  
    return None

# CONSULTAR CATEGORÍA

@app.route('/consultar_categoria', methods=['GET', 'POST'])
def consultar_categoria():
    if request.method == 'POST':
        categoria_nombre = request.form['categoria_nombre']
        categoria_info = query_categoria_info(categoria_nombre)
        if categoria_info:
            return render_template('consultar_categoria.html', categoria_info=categoria_info, categorias=query_db('SELECT nombre FROM categorias'))
        else:
            flash('Categoría no encontrada.', 'danger')  
    categorias = query_db('SELECT nombre FROM categorias')
    return render_template('consultar_categoria.html', categorias=categorias)


def query_categoria_info(nombre_categoria):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('SELECT nombre, descripcion FROM categorias WHERE nombre = ?', (nombre_categoria,))
        categoria_info = cursor.fetchone()
        if categoria_info:
            productos = query_db('SELECT nombre, descripcion, precio, stock FROM productos WHERE categoria_nombre = ?', (nombre_categoria,))
            return {
                'nombre': categoria_info['nombre'],
                'descripcion': categoria_info['descripcion'],
                'productos': productos
            }
    except Exception as e:
        flash('Error al consultar la categoría: {}'.format(str(e)), 'danger')  
    return None

# CONSULTAR PROVEEDOR

@app.route('/consultar_proveedor', methods=['GET', 'POST'])
def consultar_proveedor():
    if request.method == 'POST':
        proveedor_nombre = request.form['proveedor_nombre']
        proveedor_info = query_proveedor_info(proveedor_nombre)
        if proveedor_info:
            return render_template('consultar_proveedor.html', proveedor_info=proveedor_info, proveedores=query_db('SELECT nombre FROM proveedores'))
        else:
            flash('Proveedor no encontrada.', 'danger')  
    proveedores = query_db('SELECT nombre FROM proveedores')
    return render_template('consultar_proveedor.html', proveedores=proveedores)


def query_proveedor_info(nombre_proveedor):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('SELECT nombre, direccion, telefono FROM proveedores WHERE nombre = ?', (nombre_proveedor,))
        proveedor_info = cursor.fetchone()
        if proveedor_info:
            productos = query_db('SELECT nombre, descripcion, precio, stock FROM productos WHERE proveedor_nombre = ?', (nombre_proveedor,))
            return {
                'nombre': proveedor_info['nombre'],
                'direccion': proveedor_info['direccion'],
                'telefono': proveedor_info['telefono'],
                'productos': productos
            }
    except Exception as e:
        flash('Error al consultar la producto: {}'.format(str(e)), 'danger')  # Mensaje flash si hay un error en la consulta
    return None

# CONSULTAR BODEGA

@app.route('/consultar_bodega', methods=['GET', 'POST'])
def consultar_bodega():
    if request.method == 'POST':
        bodega_nombre = request.form['bodega_nombre']
        bodega_info = query_bodega_info(bodega_nombre)
        if bodega_info:
            return render_template('consultar_bodega.html', bodega_info=bodega_info, bodegas=query_db('SELECT nombre FROM bodegas'))
        else:
            flash('Bodega no encontrada.', 'danger')  
    bodegas = query_db('SELECT nombre FROM bodegas')
    return render_template('consultar_bodega.html', bodegas=bodegas)


def query_bodega_info(nombre_bodega):
    try:
        db = get_db()
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute('SELECT nombre, ubicacion, capacidad_maxima FROM bodegas WHERE nombre = ?', (nombre_bodega,))
        bodega_info = cursor.fetchone()
        if bodega_info:
            productos = query_db('SELECT nombre, descripcion, precio, stock FROM productos WHERE bodega_nombre = ?', (nombre_bodega,))
            return {
                'nombre': bodega_info['nombre'],
                'ubicacion': bodega_info['ubicacion'],
                'capacidad_maxima': bodega_info['capacidad_maxima'],
                'productos': productos
            }
    except Exception as e:
        flash('Error al consultar la bodega: {}'.format(str(e)), 'danger')  
    return None

# AGREGAR CATEGORIA

@app.route('/agregar_categoria', methods=['GET', 'POST'])
def agregar_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        db = get_db()
        db.execute('INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)', (nombre, descripcion))
        db.commit()
        flash('Categoría agregada exitosamente.', 'success_message')
        return redirect(url_for('index'))
    return render_template('agregar_categoria.html')


# AGREGAR PROVEEDOR

@app.route('/agregar_proveedor', methods=['GET', 'POST'])
def agregar_proveedor():
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        db = get_db()
        db.execute('INSERT INTO proveedores (nombre, direccion, telefono) VALUES (?, ?, ?)', (nombre, direccion, telefono))
        db.commit()
        flash('Proveedor agregado exitosamente.', 'success_message')
        return redirect(url_for('index'))
    return render_template('agregar_proveedor.html')

# AGREGAR BODEGA

@app.route('/agregar_bodega', methods=['GET', 'POST'])
def agregar_bodega():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form['ubicacion']
        capacidad_maxima = int(request.form['capacidad_maxima'])
        db = get_db()
        db.execute('INSERT INTO bodegas (nombre, ubicacion, capacidad_maxima) VALUES (?, ?, ?)', (nombre, ubicacion, capacidad_maxima))
        db.commit()
        flash('Bodega agregada exitosamente.', 'success_message')
        return redirect(url_for('index'))
    return render_template('agregar_bodega.html')

# AGREGAR PRODUCTO

@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        categoria_nombre = request.form['categoria_nombre']
        proveedor_nombre = request.form['proveedor_nombre']
        bodega_nombre = request.form['bodega_nombre']
        
        db = get_db()
        
        categoria_result = query_db('SELECT nombre FROM categorias WHERE nombre = ?', [categoria_nombre], one=True)
        if categoria_result:
            categoria_nombre = categoria_result[0]
        else:
            flash('Categoría no encontrada.', 'danger')
            return redirect(url_for('agregar_producto'))

        proveedor_result = query_db('SELECT nombre FROM proveedores WHERE nombre = ?', [proveedor_nombre], one=True)
        if proveedor_result:
            proveedor_nombre = proveedor_result[0]
        else:
            flash('Proveedor no encontrado.', 'danger')
            return redirect(url_for('agregar_producto'))

        bodega_result = query_db('SELECT nombre FROM bodegas WHERE nombre = ?', [bodega_nombre], one=True)
        if bodega_result:
            bodega_nombre = bodega_result[0]
        else:
            flash('Bodega no encontrada.', 'danger')
            return redirect(url_for('agregar_producto'))
        
        db.execute('INSERT INTO productos (nombre, descripcion, precio, stock, categoria_nombre, proveedor_nombre, bodega_nombre) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (nombre, descripcion, precio, stock, categoria_nombre, proveedor_nombre, bodega_nombre))
        db.commit()
        flash('Producto agregado exitosamente.', 'success')
        return redirect(url_for('index'))

    categorias = query_db('SELECT nombre FROM categorias')
    proveedores = query_db('SELECT nombre FROM proveedores')
    bodegas = query_db('SELECT nombre FROM bodegas')
    productos = query_db('SELECT nombre FROM productos')
    return render_template('agregar_producto.html', categorias=categorias, proveedores=proveedores, bodegas=bodegas, productos=productos)


# AGREGAR STOCK

def agregar_stock(nombre_productos_cantidades):
    try:
        db = get_db()
        unidades_agregadas = False

        for nombre_producto, cantidad in nombre_productos_cantidades.items():
            espacio_necesario = cantidad
            bodegas = query_db('SELECT nombre, capacidad_maxima FROM bodegas')

            for bodega in bodegas:
                bodega_nombre = bodega[0]  # Acceder al nombre de la bodega por índice
                capacidad_maxima = bodega[1]  # Acceder a la capacidad máxima por índice

                stock_actual = query_db('SELECT SUM(stock) FROM productos WHERE bodega_nombre = ? AND nombre = ?', (bodega_nombre, nombre_producto))[0][0] or 0
                espacio_disponible = capacidad_maxima - stock_actual

                if espacio_disponible >= espacio_necesario:
                    db.execute("UPDATE productos SET stock = stock + ? WHERE nombre = ? AND bodega_nombre = ?", (espacio_necesario, nombre_producto, bodega_nombre))
                    db.commit()
                    espacio_necesario = 0  # Todo el espacio necesario se ha satisfecho
                    unidades_agregadas = True
                    break
                elif espacio_disponible > 0:
                    db.execute("UPDATE productos SET stock = stock + ? WHERE nombre = ? AND bodega_nombre = ?", (espacio_disponible, nombre_producto, bodega_nombre))
                    db.commit()
                    espacio_necesario -= espacio_disponible
                    unidades_agregadas =  True

            if espacio_necesario > 0:  # Producto no pudo ser agregado completamente
                flash(f'No hay suficiente espacio en las bodegas para {cantidad - espacio_necesario} unidades de {nombre_producto}. capacidad maxima es ({capacidad_maxima}) y la bodega es {bodega_nombre}', 'danger')
                return redirect(url_for('gestionar_stock'))

        if unidades_agregadas:
            flash('Stock agregado con éxito.', 'success')
            return redirect(url_for('gestionar_stock'))
    except Exception as e:
        flash(f'Error al agregar stock: {str(e)}', 'danger')
        return redirect(url_for('gestionar_stock'))



# RETIRAR STOCK 

def retirar_stock(nombre_productos_cantidades):
    try:
        db = get_db()
        for nombre_producto, cantidad in nombre_productos_cantidades.items():
            producto = query_db('SELECT stock FROM productos WHERE nombre = ?', [nombre_producto], one=True)
            if producto:
                stock_actual = producto[0]
                if cantidad <= stock_actual:
                    db.execute("UPDATE productos SET stock = stock - ? WHERE nombre = ?", (cantidad, nombre_producto))
                else:
                    flash(f'No hay suficientes unidades disponibles del producto {nombre_producto} en la bodega.', 'danger')
                    return redirect (url_for('gestionar_stock'))
            else:
                flash(f'El producto {nombre_producto} no se encontró en la base de datos.', 'danger')
                return redirect (url_for('gestionar_stock'))
        db.commit()
        flash(f'Se retiraron las unidades del stock correctamente.', 'success')
        return redirect (url_for('gestionar_stock'))
    except Exception as e:
        flash(f'Error al retirar stock: {str(e)}', 'danger')
        return redirect(url_for('gestionar_stock'))
    
#GESTIONAR STOCK

@app.route('/gestionar_stock', methods=['GET', 'POST'])
def gestionar_stock():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'agregar_stock':
            nombre_producto = request.form['nombre_producto']
            cantidad = int(request.form['cantidad'])
            agregar_stock({nombre_producto: cantidad})
            #flash(f'Se agregaron {cantidad} unidades al stock del producto {nombre_producto}.', 'success')
        elif action == 'retirar_stock':
            nombre_producto = request.form['nombre_producto']
            cantidad = int(request.form['cantidad'])
            retirar_stock({nombre_producto: cantidad})
            #flash(f'Se retiraron {cantidad} unidades del stock del producto {nombre_producto}.', 'success') 
        else:
            flash('Acción no válida.', 'danger')
        return redirect(url_for('gestionar_stock'))
    productos = query_db('SELECT nombre FROM productos')
    return render_template('gestionar_stock.html', productos=productos)

# INFORME STOCK

@app.route('/informe_stock_total')
def informe_stock_total():
    try:
        db = get_db()
        stock_info = db.execute('SELECT SUM(stock), SUM(stock * precio) FROM productos').fetchone()
        total_stock = stock_info[0] if stock_info[0] is not None else 0  # Total quantity of products in stock
        total_value = stock_info[1] if stock_info[1] is not None else 0  # Total value of the stock

        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

        formatted_total_value = locale.currency(total_value, grouping=True)

        return render_template('informe_stock_total.html', stock_total=total_stock, total_value=formatted_total_value)
    except Exception as e:
        flash(f'Error al generar el informe de stock total: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
# Informe de Stock por Producto
@app.route('/informe_stock_por_producto')
def informe_stock_por_producto():
    try:
        db = get_db()
        productos = query_db('SELECT nombre FROM productos')
        stock_por_producto = {}
        for producto in productos:
            nombre_producto = producto[0]  # Acceder al primer elemento de la tupla
            stock = db.execute('SELECT SUM(stock) FROM productos WHERE nombre = ?', (nombre_producto,)).fetchone()[0]
            stock_por_producto[nombre_producto] = stock if stock is not None else 0  
        return render_template('informe_stock_por_producto.html', stock_por_producto=stock_por_producto)
    except Exception as e:
        flash(f'Error al generar el informe de stock por producto: {str(e)}', 'danger')
        return redirect(url_for('index'))

# Informe de Stock por Categoria
@app.route('/informe_stock_por_categoria')
def informe_stock_por_categoria():
    try:
        db = get_db()
        categorias = query_db('SELECT nombre FROM categorias')
        stock_por_categoria = {}
        for categoria in categorias:
            nombre_categoria = categoria[0]  # Access the first element of the tuple
            stock = db.execute('SELECT SUM(stock) FROM productos WHERE categoria_nombre = ?', (nombre_categoria,)).fetchone()[0]
            stock_por_categoria[nombre_categoria] = stock if stock is not None else 0  # Replace None with 0
        return render_template('informe_stock_por_categoria.html', stock_por_categoria=stock_por_categoria)
    except Exception as e:
        flash(f'Error al generar el informe de stock por categoría: {str(e)}', 'danger')
        return redirect(url_for('index'))



# Informe de Stock por Proveedor
@app.route('/informe_stock_por_proveedor')
def informe_stock_por_proveedor():
    try:
        db = get_db()
        proveedores = query_db('SELECT nombre FROM proveedores')
        stock_por_proveedor = {}
        for proveedor in proveedores:
            nombre_proveedor = proveedor[0]  
            stock = db.execute('SELECT SUM(stock) FROM productos WHERE proveedor_nombre = ?', (nombre_proveedor,)).fetchone()[0]
            stock_por_proveedor[nombre_proveedor] = stock if stock is not None else 0  
        return render_template('informe_stock_por_proveedor.html', stock_por_proveedor=stock_por_proveedor)
    except Exception as e:
        flash(f'Error al generar el informe de stock por proveedor: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
# Informe de Stock por Bodega
@app.route('/informe_stock_por_bodega')
def informe_stock_por_bodega():
    try:
        db = get_db()
        bodegas = query_db('SELECT nombre FROM bodegas')
        stock_por_bodega = {}
        for bodega in bodegas:
            nombre_bodega = bodega[0]  # Acceder al primer elemento de la tupla
            stock = db.execute('SELECT SUM(stock) FROM productos WHERE bodega_nombre = ?', (nombre_bodega,)).fetchone()[0]
            stock_por_bodega[nombre_bodega] = stock if stock is not None else 0  
        return render_template('informe_stock_por_bodega.html', stock_por_bodega=stock_por_bodega)
    except Exception as e:
        flash(f'Error al generar el informe de stock por bodega: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
# AGREGAR PRODUCTO A CATEGORIA    

@app.route('/agregar_producto_categoria', methods=['GET', 'POST'])
def agregar_producto_categoria():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        categoria_nombre = request.form['categoria_nombre']
        
        categoria_result = query_db('SELECT nombre FROM categorias WHERE nombre = ?', [categoria_nombre], one=True)
        if categoria_result:
            categoria_nombre = categoria_result[0]  
            db = get_db()
            db.execute('UPDATE productos SET categoria_nombre = ? WHERE nombre = ?', (categoria_nombre, nombre_producto))
            db.commit()
            flash(f'Producto {nombre_producto} agregado a la categoría {categoria_nombre}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Categoría no encontrada.', 'danger')
            return redirect (url_for('index'))
    categorias = query_db('SELECT nombre FROM categorias')
    productos = query_db('SELECT nombre FROM productos')
    return render_template('agregar_producto_categoria.html', categorias=categorias, productos=productos)

# ELIMINAR PRODUCTO A CATEGORIA    

@app.route('/eliminar_producto_categoria', methods=['GET', 'POST'])
def eliminar_producto_categoria():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        
        db = get_db()
        categoria_result = query_db('SELECT categoria_nombre FROM productos WHERE nombre = ?', (nombre_producto,), one=True)
        categoria_nombre = categoria_result[0] if categoria_result and len(categoria_result) > 0 else None
        
        if categoria_nombre:
            db.execute('UPDATE productos SET categoria_nombre = NULL WHERE nombre = ?', (nombre_producto,))
            db.commit()
            flash(f'Producto {nombre_producto} eliminado de la categoría {categoria_nombre}.', 'success')
        else:
            flash(f'El producto {nombre_producto} no está asignado a ninguna categoría.', 'warning')
        return redirect(url_for('index'))
    
    productos = query_db('SELECT nombre FROM productos WHERE categoria_nombre IS NOT NULL')
    return render_template('eliminar_producto_categoria.html', productos=productos)

# AGREGAR PRODUCTO A PROVEEDOR    

@app.route('/agregar_producto_proveedor', methods=['GET', 'POST'])
def agregar_producto_proveedor():
    if request.method == 'POST':

        nombre_producto = request.form['nombre_producto']
        proveedor_nombre = request.form['proveedor_nombre']

        proveedor_result = query_db('SELECT nombre FROM proveedores WHERE nombre = ?', [proveedor_nombre], one=True)
        if proveedor_result:
            proveedor_nombre = proveedor_result[0]  

            db = get_db()
            db.execute('UPDATE productos SET proveedor_nombre = ? WHERE nombre = ?', (proveedor_nombre, nombre_producto))
            db.commit()
            flash(f'Producto {nombre_producto} agregado a la proveedor {proveedor_nombre}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Proveedor no encontrada.', 'danger')
    
    proveedores = query_db('SELECT nombre FROM proveedores')
    productos = query_db('SELECT nombre FROM productos')
    return render_template('agregar_producto_proveedor.html', proveedores=proveedores, productos=productos)

# ELIMINAR PRODUCTO A PROVEEDOR

@app.route('/eliminar_producto_proveedor', methods=['GET', 'POST'])
def eliminar_producto_proveedor():
    if request.method == 'POST':
        try:
            nombre_producto = request.form['nombre_producto']
        except KeyError:
            flash('Nombre del producto no encontrado en la solicitud. Tienes que seleccionar el producto', 'danger')
            return redirect(url_for('eliminar_producto_proveedor'))
        
        db = get_db()
        proveedor_result = query_db('SELECT proveedor_nombre FROM productos WHERE nombre= ?', (nombre_producto,), one=True)
        proveedor_nombre = proveedor_result[0] if proveedor_result and len(proveedor_result) > 0 else None

        if proveedor_nombre:
            db.execute('UPDATE productos SET proveedor_nombre = NULL WHERE nombre = ?', (nombre_producto,))
            db.commit()
            flash(f'Producto {nombre_producto} eliminado de la proveedor {proveedor_nombre}.', 'success')
        else:
            flash(f'El producto {nombre_producto} no está asignado a ninguna proveedor.', 'warning')
        return redirect(url_for('index'))
    
    productos = query_db('SELECT nombre FROM productos WHERE proveedor_nombre IS NOT NULL')
    return render_template('eliminar_producto_proveedor.html', productos=productos)

# ACTUALIZAR PRODUCTO A BODEGA    

@app.route('/agregar_producto_bodega', methods=['GET', 'POST'])
def agregar_producto_bodega():
    if request.method == 'POST':
        try:
            nombre_producto = request.form['nombre_producto']
            bodega_nombre = request.form['bodega_nombre']

            # Check if the bodega exists
            bodega_result = query_db('SELECT nombre FROM bodegas WHERE nombre = ?', [bodega_nombre], one=True)
            if bodega_result:
                db = get_db()
                db.execute('UPDATE productos SET bodega_nombre = ? WHERE nombre = ?', (bodega_nombre, nombre_producto))
                db.commit()
                flash(f'Producto {nombre_producto} agregado a la bodega {bodega_nombre}.', 'success')
                return redirect(url_for('agregar_producto_bodega'))
            else:
                flash('Bodega no encontrada.', 'danger')
                return redirect(url_for('agregar_producto_bodega'))
        except KeyError as e:
            flash(f'Error al enviar el formulario: campo faltante {str(e)}.', 'danger')
            return redirect(url_for('agregar_producto_bodega'))
        except Exception as e:
            flash(f'Error inesperado: {str(e)}', 'danger')
        return redirect(url_for('agregar_producto_bodega'))
    
    # Fetch bodegas and productos for the form
    bodegas = query_db('SELECT nombre FROM bodegas')
    productos = query_db('SELECT nombre FROM productos')
    return render_template('agregar_producto_bodega.html', bodegas=bodegas, productos=productos)


# ELIMINAR PRODUCTO A BODEGA

@app.route('/eliminar_producto_bodega', methods=['GET', 'POST'])
def eliminar_producto_bodega():
    if request.method == 'POST':
        try:
            nombre_producto = request.form['nombre_producto']
        except KeyError:
            flash('Nombre del producto no encontrado en la solicitud. Tienes que seleccionar el producto', 'danger')
            return redirect(url_for('eliminar_producto_bodega'))
        
        db = get_db()
        bodega_result = query_db('SELECT bodega_nombre FROM productos WHERE nombre = ?', (nombre_producto,), one=True)
        bodega_nombre = bodega_result[0] if bodega_result and len(bodega_result) > 0 else None

        if bodega_nombre:
            db.execute('UPDATE productos SET bodega_nombre = NULL WHERE nombre = ?', (nombre_producto,))
            db.commit()
            flash(f'Producto {nombre_producto} eliminado de la bodega {bodega_nombre}.', 'success')
        else:
            flash(f'El producto {nombre_producto} no está asignado a ninguna bodega.', 'warning')
        return redirect(url_for('index'))
        
    productos = query_db('SELECT nombre FROM productos WHERE bodega_nombre IS NOT NULL')
    return render_template('eliminar_producto_bodega.html', productos=productos)



# RETIRAR PRODUCTO A BODEGA    

@app.route('/retirar_producto_bodega', methods=['GET', 'POST'])
def retirar_producto_bodega():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        cantidad = int(request.form['cantidad'])
        retirar_producto(nombre_producto, cantidad)
        return redirect(url_for('index'))
    productos = query_db('SELECT nombre FROM productos WHERE stock > 0')

    return render_template('retirar_producto_bodega.html', productos=productos)

def retirar_producto(nombre_producto, cantidad):
    try:
        db = get_db()
        producto = query_db('SELECT stock FROM productos WHERE nombre = ?', [nombre_producto], one=True)
        if producto:
            stock_actual = producto[0]  
            if cantidad <= stock_actual:
                db.execute("UPDATE productos SET stock = stock - ? WHERE nombre = ?", (cantidad, nombre_producto))
                db.commit()
                flash(f'Se retiraron {cantidad} unidades del producto {nombre_producto} de la bodega correctamente.', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'No hay suficientes unidades disponibles del producto {nombre_producto} en la bodega.', 'danger')
                return redirect(url_for('index'))
        else:
            flash(f'El producto {nombre_producto} no se encontró en la base de datos.', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error al retirar el producto de la bodega: {str(e)}', 'danger')
        return redirect(url_for('index'))
    
# CONSULTAR DISPONIBILIDAD        

@app.route('/consultar_disponibilidad_producto', methods=['GET', 'POST'])
def consultar_disponibilidad_producto():
    if request.method == 'POST':
        try:
            print(request.form)  # Print the form data to check if it is being received
            producto_nombre = request.form['producto_nombre']
            disponibilidad = query_disponibilidad_producto(producto_nombre)
            if disponibilidad is not None:
                return render_template('consultar_disponibilidad_producto.html', productos=query_db('SELECT nombre FROM productos'), disponibilidad=disponibilidad, producto_nombre=producto_nombre)
            else:
                flash(f'El producto {producto_nombre} no está disponible.', 'danger')
                return redirect(url_for('consultar_disponibilidad_producto'))
        except werkzeug.exceptions.BadRequestKeyError as e:
            flash('Producto nombre no encontrado en la solicitud. Por favor, inténtalo de nuevo.', 'danger')
            #return redirect(url_for('consultar_disponibilidad_producto'))
            print(f'Error: {e}')  # Log the error for debugging

    productos = query_db('SELECT nombre FROM productos')
    return render_template('consultar_disponibilidad_producto.html', productos=productos)

def query_disponibilidad_producto(nombre_producto):
    try:
        db = get_db()
        producto_info = db.execute('SELECT stock, bodega_nombre FROM productos WHERE nombre = ?', (nombre_producto,)).fetchone()
        if producto_info:
            stock_disponible = producto_info[0]
            nombre_bodega = producto_info[1]
            return stock_disponible, nombre_bodega
        else:
            return None, None
    except Exception as e:
        flash(f'Error al consultar la disponibilidad del producto en la bodega: {str(e)}', 'danger')
        return None, None

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
