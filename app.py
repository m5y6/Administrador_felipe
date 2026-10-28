import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime

# Los datos se guardan junto al ejecutable (o junto a este script en desarrollo).
BASE_DIR = os.path.dirname(
    os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)
)

# Archivos de base de datos
INV_FILE = os.path.join(BASE_DIR, "inventario.json")
SALES_FILE = os.path.join(BASE_DIR, "ventas.json")
CAT_FILE = os.path.join(BASE_DIR, "categorias.json")
PROV_FILE = os.path.join(BASE_DIR, "proveedores.json")
EXPENSES_FILE = os.path.join(BASE_DIR, "gastos.json")
MOVEMENTS_FILE = os.path.join(BASE_DIR, "movimientos.json")
MIN_PREDICTION_DAYS = 7
DEFAULT_MIN_STOCK = 5

# Crear archivos si no existen
for f in [INV_FILE, SALES_FILE, CAT_FILE, PROV_FILE, EXPENSES_FILE, MOVEMENTS_FILE]:
    if not os.path.exists(f):
        if f == CAT_FILE:
            with open(f, "w") as file: json.dump({"Sin Categoría": "GEN"}, file)
        elif f == PROV_FILE:
            with open(f, "w") as file: json.dump(["Sin Proveedor"], file)
        else:
            with open(f, "w") as file: json.dump([], file)

def load_data(file):
    with open(file, "r") as f:
        data = json.load(f)

    if file == INV_FILE and isinstance(data, list):
        numeric_fields = ("precio_compra", "precio_venta", "stock", "hijo_unidades")
        for item in data:
            if isinstance(item, dict):
                for field in numeric_fields:
                    item[field] = entero_desde_dato(item.get(field), 0)
                item["stock_minimo"] = entero_desde_dato(
                    item.get("stock_minimo"), DEFAULT_MIN_STOCK
                )
    elif file == SALES_FILE and isinstance(data, list):
        numeric_fields = (
            "cantidad", "costo_unitario", "costo_total", "precio_unitario",
            "venta_total"
        )
        for item in data:
            if isinstance(item, dict):
                for field in numeric_fields:
                    item[field] = entero_desde_dato(item.get(field), 0)
    elif file == EXPENSES_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item["monto"] = entero_desde_dato(item.get("monto"), 0)
    elif file == MOVEMENTS_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item["cantidad"] = entero_desde_dato(item.get("cantidad"), 0)
                item["costo_unitario"] = entero_desde_dato(
                    item.get("costo_unitario"), 0
                )

    return data

def save_data(file, data):
    if file == INV_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for field in ("precio_compra", "precio_venta", "stock", "hijo_unidades"):
                    item[field] = entero_desde_dato(item.get(field), 0)
                item["stock_minimo"] = entero_desde_dato(
                    item.get("stock_minimo"), DEFAULT_MIN_STOCK
                )
    elif file == SALES_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for field in (
                    "cantidad", "costo_unitario", "costo_total", "precio_unitario",
                    "venta_total"
                ):
                    item[field] = entero_desde_dato(item.get(field), 0)
    elif file == EXPENSES_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item["monto"] = entero_desde_dato(item.get("monto"), 0)
    elif file == MOVEMENTS_FILE and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                item["cantidad"] = entero_desde_dato(item.get("cantidad"), 0)
                item["costo_unitario"] = entero_desde_dato(
                    item.get("costo_unitario"), 0
                )

    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def entero_desde_dato(valor, predeterminado=0):
    if valor is None or valor == "":
        return predeterminado
    try:
        return int(float(valor))
    except (TypeError, ValueError, OverflowError):
        return predeterminado

def obtener_entero(variable, nombre, minimo=0):
    try:
        valor = int(variable.get().strip())
    except (AttributeError, TypeError, ValueError, tk.TclError):
        messagebox.showerror("Dato inválido", f"{nombre} debe ser un número entero.")
        return None

    if valor < minimo:
        messagebox.showerror("Dato inválido", f"{nombre} debe ser mayor o igual a {minimo}.")
        return None
    return valor

def normalizar_texto(texto):
    if not texto: return ""
    return " ".join(palabra.capitalize() for palabra in texto.strip().split())

def costo_total_venta(venta):
    cantidad = entero_desde_dato(venta.get("cantidad"), 0)
    costo_unitario = entero_desde_dato(venta.get("costo_unitario"), 0)
    costo_total = entero_desde_dato(venta.get("costo_total"), 0)
    if costo_unitario > 0:
        return costo_unitario * cantidad
    return costo_total

def ingreso_total_venta(venta):
    cantidad = entero_desde_dato(venta.get("cantidad"), 0)
    precio_unitario = entero_desde_dato(venta.get("precio_unitario"), 0)
    venta_total = entero_desde_dato(venta.get("venta_total"), 0)
    if precio_unitario > 0:
        return precio_unitario * cantidad
    return venta_total

class AppAdministrador:
    def __init__(self, root):
        self.root = root
        self.root.title("FELIPE APP ADMINISTRADOR - Sistema Pro Automático")
        self.root.geometry("1100x750")
        
        self.dict_categorias = {}
        self.lista_proveedores = []
        
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(expand=True)
        
        tk.Label(self.login_frame, text="Contraseña:", font=("Arial", 14)).pack(pady=10)
        self.pass_entry = tk.Entry(self.login_frame, show="*")
        self.pass_entry.pack(pady=5)
        tk.Button(self.login_frame, text="Ingresar", command=self.check_login).pack(pady=10)

    def check_login(self):
        if self.pass_entry.get() == "Felipeweko":
            self.login_frame.destroy()
            self.build_main_app()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def build_main_app(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both')

        self.tab_inv = ttk.Frame(notebook)
        self.tab_ventas = ttk.Frame(notebook)
        self.tab_cat_prov = ttk.Frame(notebook)
        self.tab_dash = ttk.Frame(notebook)

        notebook.add(self.tab_inv, text="Inventario & Productos")
        notebook.add(self.tab_ventas, text="Ventas Rápidas")
        notebook.add(self.tab_cat_prov, text="Categorías & Proveedores")
        notebook.add(self.tab_dash, text="Contabilidad & Predicción")

        self.setup_cat_prov() 
        self.setup_inventario()
        self.setup_ventas()
        self.setup_dashboard()

    # --- PESTAÑA CATEGORÍAS Y PROVEEDORES ---
    def setup_cat_prov(self):
        frame_cat = tk.LabelFrame(self.tab_cat_prov, text="Gestión de Categorías", font=("Arial", 10, "bold"))
        frame_cat.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(frame_cat, text="Nueva Categoría (Ej: Papel Higiénico):").pack(pady=2)
        self.var_nueva_cat = tk.StringVar()
        tk.Entry(frame_cat, textvariable=self.var_nueva_cat, font=("Arial", 11)).pack(pady=2, padx=10, fill="x")
        
        tk.Label(frame_cat, text="Prefijo para Códigos (Ej: PAPE):").pack(pady=2)
        self.var_prefijo_cat = tk.StringVar()
        tk.Entry(frame_cat, textvariable=self.var_prefijo_cat, font=("Arial", 11)).pack(pady=2, padx=10, fill="x")
        
        tk.Button(frame_cat, text="Agregar Categoría", bg="#dff0d8", command=self.agregar_categoria).pack(pady=5)
        
        self.list_cat = tk.Listbox(frame_cat, font=("Arial", 11))
        self.list_cat.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_btn_cat = tk.Frame(frame_cat)
        frame_btn_cat.pack(fill="x", pady=5)
        tk.Button(frame_btn_cat, text="✏️ Editar", bg="#f0ad4e", fg="white", command=self.editar_categoria).pack(side="left", expand=True, padx=5)
        tk.Button(frame_btn_cat, text="🗑️ Eliminar", bg="#d9534f", fg="white", command=self.eliminar_categoria).pack(side="left", expand=True, padx=5)


        frame_prov = tk.LabelFrame(self.tab_cat_prov, text="Gestión de Proveedores", font=("Arial", 10, "bold"))
        frame_prov.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(frame_prov, text="Nuevo Proveedor:").pack(pady=5)
        self.var_nuevo_prov = tk.StringVar()
        tk.Entry(frame_prov, textvariable=self.var_nuevo_prov, font=("Arial", 11)).pack(pady=5, padx=10, fill="x")
        tk.Button(frame_prov, text="Agregar Proveedor", bg="#d9edf7", command=self.agregar_proveedor).pack(pady=5)
        
        self.list_prov = tk.Listbox(frame_prov, font=("Arial", 11))
        self.list_prov.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_btn_prov = tk.Frame(frame_prov)
        frame_btn_prov.pack(fill="x", pady=5)
        tk.Button(frame_btn_prov, text="✏️ Editar", bg="#f0ad4e", fg="white", command=self.editar_proveedor).pack(side="left", expand=True, padx=5)
        tk.Button(frame_btn_prov, text="🗑️ Eliminar", bg="#d9534f", fg="white", command=self.eliminar_proveedor).pack(side="left", expand=True, padx=5)

        self.actualizar_listas_cat_prov()

    def agregar_categoria(self):
        cat = normalizar_texto(self.var_nueva_cat.get())
        pref = self.var_prefijo_cat.get().strip().upper()
        if cat and pref:
            if cat not in self.dict_categorias:
                self.dict_categorias[cat] = pref
                save_data(CAT_FILE, self.dict_categorias)
                self.var_nueva_cat.set("")
                self.var_prefijo_cat.set("")
                self.actualizar_listas_cat_prov()
                messagebox.showinfo("Éxito", f"Categoría agregada con prefijo {pref}.")
            else:
                messagebox.showwarning("Aviso", "La categoría ya existe.")
        else:
            messagebox.showwarning("Aviso", "Debes ingresar Nombre y Prefijo.")

    def eliminar_categoria(self):
        seleccion = self.list_cat.curselection()
        if not seleccion: return
        cat_info = self.list_cat.get(seleccion[0])
        cat_name = cat_info.split(" (Prefijo:")[0]
        
        if cat_name == "Sin Categoría":
            messagebox.showwarning("Aviso", "No puedes eliminar la categoría predeterminada.")
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar '{cat_name}'? Sus productos pasarán a 'Sin Categoría', pero sus códigos se mantendrán."):
            del self.dict_categorias[cat_name]
            if "Sin Categoría" not in self.dict_categorias:
                self.dict_categorias["Sin Categoría"] = "GEN"
            save_data(CAT_FILE, self.dict_categorias)
            
            # Actualizar productos en inventario sin tocar el código
            inv = load_data(INV_FILE)
            for p in inv:
                if p.get("categoria") == cat_name:
                    p["categoria"] = "Sin Categoría"
            save_data(INV_FILE, inv)
            
            self.actualizar_listas_cat_prov()
            self.actualizar_tabla_inv()
            self.actualizar_tabla_ventas()
            messagebox.showinfo("Éxito", "Categoría eliminada.")

    def editar_categoria(self):
        seleccion = self.list_cat.curselection()
        if not seleccion: return
        cat_info = self.list_cat.get(seleccion[0])
        cat_name_old = cat_info.split(" (Prefijo:")[0]
        pref_old = self.dict_categorias[cat_name_old]

        top = tk.Toplevel(self.root)
        top.title("Editar Categoría")
        top.geometry("300x200")
        top.grab_set()

        tk.Label(top, text="Nombre Categoría (Editable):").pack(pady=5)
        var_nom = tk.StringVar(value=cat_name_old)
        tk.Entry(top, textvariable=var_nom).pack(pady=5)
        
        tk.Label(top, text="Prefijo (NO Editable, protege el historial):").pack(pady=5)
        var_pref = tk.StringVar(value=pref_old)
        # El entry se marca readonly para no perder datos históricos
        tk.Entry(top, textvariable=var_pref, state="readonly", fg="gray").pack(pady=5)

        def guardar():
            nuevo_nom = normalizar_texto(var_nom.get())
            if nuevo_nom:
                if nuevo_nom != cat_name_old:
                    del self.dict_categorias[cat_name_old]
                    self.dict_categorias[nuevo_nom] = pref_old
                    save_data(CAT_FILE, self.dict_categorias)
                    
                    inv = load_data(INV_FILE)
                    for p in inv:
                        if p.get("categoria") == cat_name_old:
                            p["categoria"] = nuevo_nom
                    save_data(INV_FILE, inv)
                    
                    self.actualizar_listas_cat_prov()
                    self.actualizar_tabla_inv()
                    self.actualizar_tabla_ventas()
                top.destroy()
                messagebox.showinfo("Éxito", "Categoría actualizada.")
        tk.Button(top, text="Guardar", bg="#5cb85c", fg="white", command=guardar).pack(pady=10)

    def agregar_proveedor(self):
        prov = normalizar_texto(self.var_nuevo_prov.get())
        if prov:
            if prov not in self.lista_proveedores:
                self.lista_proveedores.append(prov)
                self.lista_proveedores.sort()
                save_data(PROV_FILE, self.lista_proveedores)
                self.var_nuevo_prov.set("")
                self.actualizar_listas_cat_prov()
                messagebox.showinfo("Éxito", f"Proveedor '{prov}' agregado.")

    def eliminar_proveedor(self):
        seleccion = self.list_prov.curselection()
        if not seleccion: return
        prov_name = self.list_prov.get(seleccion[0])
        
        if prov_name == "Sin Proveedor":
            messagebox.showwarning("Aviso", "No puedes eliminar el proveedor predeterminado.")
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar '{prov_name}'? Sus productos pasarán a 'Sin Proveedor'."):
            self.lista_proveedores.remove(prov_name)
            if "Sin Proveedor" not in self.lista_proveedores:
                self.lista_proveedores.append("Sin Proveedor")
            save_data(PROV_FILE, self.lista_proveedores)
            
            inv = load_data(INV_FILE)
            for p in inv:
                if p.get("proveedor") == prov_name:
                    p["proveedor"] = "Sin Proveedor"
            save_data(INV_FILE, inv)
            
            self.actualizar_listas_cat_prov()
            self.actualizar_tabla_inv()
            messagebox.showinfo("Éxito", "Proveedor eliminado.")

    def editar_proveedor(self):
        seleccion = self.list_prov.curselection()
        if not seleccion: return
        prov_old = self.list_prov.get(seleccion[0])

        top = tk.Toplevel(self.root)
        top.title("Editar Proveedor")
        top.geometry("300x150")
        top.grab_set()

        tk.Label(top, text="Nombre Proveedor:").pack(pady=10)
        var_nom = tk.StringVar(value=prov_old)
        tk.Entry(top, textvariable=var_nom).pack(pady=5)
        
        def guardar():
            nuevo_nom = normalizar_texto(var_nom.get())
            if nuevo_nom:
                idx = self.lista_proveedores.index(prov_old)
                self.lista_proveedores[idx] = nuevo_nom
                save_data(PROV_FILE, self.lista_proveedores)
                
                inv = load_data(INV_FILE)
                for p in inv:
                    if p.get("proveedor") == prov_old:
                        p["proveedor"] = nuevo_nom
                save_data(INV_FILE, inv)
                
                self.actualizar_listas_cat_prov()
                self.actualizar_tabla_inv()
                top.destroy()
                messagebox.showinfo("Éxito", "Proveedor actualizado.")
        tk.Button(top, text="Guardar", bg="#5cb85c", fg="white", command=guardar).pack(pady=10)

    def actualizar_listas_cat_prov(self):
        self.dict_categorias = load_data(CAT_FILE)
        self.lista_proveedores = sorted(load_data(PROV_FILE))
        
        self.list_cat.delete(0, tk.END)
        for cat, pref in sorted(self.dict_categorias.items()): 
            self.list_cat.insert(tk.END, f"{cat} (Prefijo: {pref})")
            
        self.list_prov.delete(0, tk.END)
        for p in self.lista_proveedores: self.list_prov.insert(tk.END, p)

        lista_cat_nombres = sorted(list(self.dict_categorias.keys()))
        
        if hasattr(self, 'combo_cat'): self.combo_cat['values'] = lista_cat_nombres
        if hasattr(self, 'combo_prov'): self.combo_prov['values'] = self.lista_proveedores
        if hasattr(self, 'combo_filtro'): self.combo_filtro['values'] = [""] + lista_cat_nombres

    # --- PESTAÑA INVENTARIO ---
    def setup_inventario(self):
        frame_nuevo = tk.LabelFrame(self.tab_inv, text="Añadir Nuevo Producto")
        frame_nuevo.pack(fill="x", padx=10, pady=5)
        
        self.var_cod = tk.StringVar(value="(Selecciona Categoría)")
        self.var_nom = tk.StringVar()
        self.var_cat = tk.StringVar()
        self.var_prov = tk.StringVar()
        self.var_costo = tk.StringVar(value="0")
        self.var_venta = tk.StringVar(value="0")
        self.var_stock = tk.StringVar(value="0")
        self.var_stock_minimo = tk.StringVar(value=str(DEFAULT_MIN_STOCK))
        self.var_es_conjunto = tk.BooleanVar()
        self.var_uni_hijo = tk.StringVar(value="0")
        self.var_venta_hijo = tk.StringVar(value="0")

        tk.Label(frame_nuevo, text="Categoría:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.combo_cat = ttk.Combobox(frame_nuevo, textvariable=self.var_cat, state="readonly")
        self.combo_cat.grid(row=0, column=1, padx=5, pady=2)
        self.combo_cat.bind('<<ComboboxSelected>>', self.actualizar_preview_sku)

        tk.Label(frame_nuevo, text="Código (Automático):").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_cod, state="readonly", fg="blue", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5, pady=2)
        
        tk.Label(frame_nuevo, text="Nombre Producto:").grid(row=0, column=4, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_nom).grid(row=0, column=5, padx=5, pady=2)

        tk.Label(frame_nuevo, text="Proveedor:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.combo_prov = ttk.Combobox(frame_nuevo, textvariable=self.var_prov)
        self.combo_prov.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_nuevo, text="Costo de compra:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_costo).grid(row=1, column=3, padx=5, pady=2)

        tk.Label(frame_nuevo, text="Precio Venta:").grid(row=1, column=4, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_venta).grid(row=1, column=5, padx=5, pady=2)

        tk.Label(frame_nuevo, text="Stock Inicial:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_stock).grid(row=2, column=1, padx=5, pady=2)
        tk.Label(frame_nuevo, text="Stock Mínimo:").grid(row=2, column=2, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_stock_minimo).grid(row=2, column=3, padx=5, pady=2)

        frame_conjunto = tk.Frame(frame_nuevo)
        frame_conjunto.grid(row=3, column=0, columnspan=6, pady=5)
        tk.Checkbutton(frame_conjunto, text="Este producto es una Manga/Conjunto (Genera unidad suelta)", variable=self.var_es_conjunto, command=self.toggle_conjunto, font=("Arial", 9, "bold")).pack(side="top", pady=2)
        
        self.panel_hijo = tk.Frame(frame_conjunto)
        self.panel_hijo.pack(side="top", pady=2)
        
        tk.Label(self.panel_hijo, text="Cod. Suelto: (Se asignará auto)").grid(row=0, column=0, padx=5)
        tk.Label(self.panel_hijo, text="¿Cuántas unidades trae?:").grid(row=0, column=2, padx=5)
        self.entry_uni_hijo = tk.Entry(self.panel_hijo, textvariable=self.var_uni_hijo, state="disabled")
        self.entry_uni_hijo.grid(row=0, column=3, padx=5)
        tk.Label(self.panel_hijo, text="Precio Venta (Suelto):").grid(row=0, column=4, padx=5)
        self.entry_venta_hijo = tk.Entry(self.panel_hijo, textvariable=self.var_venta_hijo, state="disabled")
        self.entry_venta_hijo.grid(row=0, column=5, padx=5)

        tk.Button(frame_nuevo, text="Guardar Producto(s)", bg="#d9edf7", command=self.guardar_producto).grid(row=4, column=0, columnspan=6, pady=10)

        frame_compra = tk.LabelFrame(self.tab_inv, text="Registrar compra / entrada de stock")
        frame_compra.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_compra, text="Código:").pack(side="left", padx=5)
        self.var_compra_codigo = tk.StringVar()
        self.combo_compra_codigo = ttk.Combobox(
            frame_compra, textvariable=self.var_compra_codigo, width=12
        )
        self.combo_compra_codigo.pack(side="left", padx=5)
        tk.Label(frame_compra, text="Cantidad:").pack(side="left", padx=5)
        self.var_compra_cantidad = tk.StringVar(value="1")
        tk.Entry(frame_compra, textvariable=self.var_compra_cantidad, width=8).pack(side="left", padx=5)
        tk.Label(frame_compra, text="Nuevo costo unitario:").pack(side="left", padx=5)
        self.var_compra_costo = tk.StringVar(value="0")
        tk.Entry(frame_compra, textvariable=self.var_compra_costo, width=10).pack(side="left", padx=5)
        tk.Button(frame_compra, text="Registrar compra", bg="#d9edf7", command=self.registrar_compra).pack(side="left", padx=10)

        frame_desarmar = tk.LabelFrame(self.tab_inv, text="Romper Empaque Rápido")
        frame_desarmar.pack(fill="x", padx=10, pady=5)
        tk.Label(frame_desarmar, text="Código de la Manga (Ej: PAPE-01):").pack(side="left", padx=10)
        self.cod_desarmar = tk.StringVar()
        tk.Entry(frame_desarmar, textvariable=self.cod_desarmar).pack(side="left", padx=10)
        tk.Button(frame_desarmar, text="Desarmar 1 Unidad", bg="#fcf8e3", command=self.desarmar_empaque).pack(side="left", padx=10)

        frame_tabla = tk.Frame(self.tab_inv)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)
        
        frame_controles = tk.Frame(frame_tabla)
        frame_controles.pack(fill="x", pady=5)

        tk.Label(frame_controles, text="Filtrar por Categoría:").pack(side="left")
        self.var_filtro = tk.StringVar()
        self.combo_filtro = ttk.Combobox(frame_controles, textvariable=self.var_filtro, state="readonly")
        self.combo_filtro.pack(side="left", padx=5)
        tk.Button(frame_controles, text="Filtrar", command=self.actualizar_tabla_inv).pack(side="left")
        tk.Button(frame_controles, text="Ver Todos", command=lambda: [self.var_filtro.set(""), self.actualizar_tabla_inv()]).pack(side="left", padx=5)
        tk.Button(frame_controles, text="✏️ Editar Producto Seleccionado", bg="#f0ad4e", fg="white", font=("Arial", 9, "bold"), command=self.abrir_ventana_edicion).pack(side="right", padx=10)

        self.tree_inv = ttk.Treeview(frame_tabla, columns=("Cod", "Nombre", "Cat", "Costo", "Venta", "Stock", "Mínimo", "Prov"), show="headings")
        for col in self.tree_inv["columns"]:
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=90)
        self.tree_inv.pack(fill="both", expand=True, pady=10)
        
        self.actualizar_listas_cat_prov()
        self.actualizar_codigos_compra()
        self.actualizar_tabla_inv()

    def actualizar_codigos_compra(self):
        if hasattr(self, "combo_compra_codigo"):
            inventario = load_data(INV_FILE)
            self.combo_compra_codigo["values"] = [
                p.get("codigo", "") for p in inventario if p.get("codigo")
            ]

    def abrir_ventana_edicion(self):
        seleccion = self.tree_inv.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Por favor, selecciona un producto.")
            return
            
        valores = self.tree_inv.item(seleccion[0])['values']
        cod_prod = valores[0]
        
        inv = load_data(INV_FILE)
        producto = next((p for p in inv if p["codigo"] == cod_prod), None)
        if not producto: return

        top = tk.Toplevel(self.root)
        top.title(f"Editar Producto: {cod_prod}")
        top.geometry("400x350")
        top.grab_set() 
        
        tk.Label(top, text=f"Editando: {producto['nombre']}", font=("Arial", 11, "bold")).pack(pady=10)
        
        frame_form = tk.Frame(top)
        frame_form.pack(pady=10, padx=20, fill="x")

        # Categoria (El código NO cambia, pero la categoría visual sí)
        tk.Label(frame_form, text="Categoría:").grid(row=0, column=0, sticky="e", pady=5)
        var_cat_prod = tk.StringVar(value=producto.get("categoria", "Sin Categoría"))
        combo_cat_prod = ttk.Combobox(frame_form, textvariable=var_cat_prod, values=list(self.dict_categorias.keys()))
        combo_cat_prod.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Proveedor:").grid(row=1, column=0, sticky="e", pady=5)
        var_prov = tk.StringVar(value=producto.get("proveedor", ""))
        combo_prov = ttk.Combobox(frame_form, textvariable=var_prov, values=self.lista_proveedores)
        combo_prov.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Costo de compra:").grid(row=2, column=0, sticky="e", pady=5)
        var_costo = tk.StringVar(value=str(entero_desde_dato(producto.get("precio_compra"), 0)))
        tk.Entry(frame_form, textvariable=var_costo).grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Precio Venta:").grid(row=3, column=0, sticky="e", pady=5)
        var_venta = tk.StringVar(value=str(entero_desde_dato(producto.get("precio_venta"), 0)))
        tk.Entry(frame_form, textvariable=var_venta).grid(row=3, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Stock Total Actual:").grid(row=4, column=0, sticky="e", pady=5)
        var_stock = tk.StringVar(value=str(entero_desde_dato(producto.get("stock"), 0)))
        tk.Entry(frame_form, textvariable=var_stock).grid(row=4, column=1, pady=5, padx=5)
        tk.Label(frame_form, text="Stock mínimo:").grid(row=5, column=0, sticky="e", pady=5)
        var_stock_minimo = tk.StringVar(
            value=str(entero_desde_dato(producto.get("stock_minimo"), DEFAULT_MIN_STOCK))
        )
        tk.Entry(frame_form, textvariable=var_stock_minimo).grid(row=5, column=1, pady=5, padx=5)
        
        def guardar_cambios():
            costo = obtener_entero(var_costo, "El costo de compra")
            venta = obtener_entero(var_venta, "El precio de venta")
            stock = obtener_entero(var_stock, "El stock")
            stock_minimo = obtener_entero(var_stock_minimo, "El stock mínimo")
            if costo is None or venta is None or stock is None or stock_minimo is None:
                return

            # Actualizar Categoria
            cat_norm = normalizar_texto(var_cat_prod.get())
            if cat_norm and cat_norm not in self.dict_categorias:
                messagebox.showwarning("Aviso", "Categoría no existe. Guardando como 'Sin Categoría'.")
                cat_norm = "Sin Categoría"
            producto["categoria"] = cat_norm

            # Actualizar Proveedor
            prov_norm = normalizar_texto(var_prov.get())
            if prov_norm and prov_norm not in self.lista_proveedores:
                self.var_nuevo_prov.set(prov_norm)
                self.agregar_proveedor()

            cambios_costos = self.preparar_actualizacion_costos(inv, producto, costo)
            if cambios_costos is None:
                return
                
            producto["proveedor"] = prov_norm or "Sin Proveedor"
            producto["precio_venta"] = venta
            producto["stock"] = stock
            producto["stock_minimo"] = stock_minimo
            for producto_cambio, costo_cambio in cambios_costos:
                producto_cambio["precio_compra"] = costo_cambio
            
            save_data(INV_FILE, inv)
            self.actualizar_tabla_inv()
            self.actualizar_codigos_compra()
            self.actualizar_tabla_ventas()
            top.destroy()
            messagebox.showinfo("Éxito", f"Producto actualizado. El código {cod_prod} se mantiene intacto.")
            
        tk.Button(top, text="Guardar Cambios", bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), command=guardar_cambios).pack(pady=15)

    def generar_proximo_sku(self, categoria, sumador=1):
        if not categoria: return ""
        prefijo = self.dict_categorias.get(categoria, "GEN")
        inv = load_data(INV_FILE)
        
        max_num = 0
        for p in inv:
            cod = p.get("codigo", "")
            if cod.startswith(prefijo + "-"):
                try:
                    num = int(cod.split("-")[1])
                    if num > max_num: max_num = num
                except (IndexError, ValueError):
                    pass
        return f"{prefijo}-{max_num + sumador:02d}"

    def actualizar_preview_sku(self, event=None):
        cat = self.var_cat.get()
        if cat: self.var_cod.set(self.generar_proximo_sku(cat))

    def preparar_actualizacion_costos(self, inv, producto, nuevo_costo):
        cambios = [(producto, nuevo_costo)]
        advertencias = []
        precio_venta = entero_desde_dato(producto.get("precio_venta"), 0)
        if nuevo_costo > precio_venta:
            advertencias.append(
                f"{producto['codigo']}: costo ${nuevo_costo:,} > venta ${precio_venta:,}"
            )

        codigo_hijo = producto.get("hijo_codigo", "")
        unidades = entero_desde_dato(producto.get("hijo_unidades"), 0)
        if codigo_hijo and unidades > 0:
            hijo = next((p for p in inv if p.get("codigo") == codigo_hijo), None)
            if hijo is not None:
                costo_hijo = nuevo_costo // unidades
                cambios.append((hijo, costo_hijo))
                precio_venta_hijo = entero_desde_dato(hijo.get("precio_venta"), 0)
                if costo_hijo > precio_venta_hijo:
                    advertencias.append(
                        f"{hijo['codigo']}: costo ${costo_hijo:,} > venta "
                        f"${precio_venta_hijo:,}"
                    )

        if advertencias:
            detalle = "\n".join(advertencias)
            continuar = messagebox.askyesno(
                "Advertencia de pérdida",
                f"El cambio puede generar pérdidas:\n\n{detalle}\n\n"
                "¿Deseas continuar?"
            )
            if not continuar:
                return None
        return cambios

    def toggle_conjunto(self):
        estado = "normal" if self.var_es_conjunto.get() else "disabled"
        self.entry_uni_hijo.config(state=estado)
        self.entry_venta_hijo.config(state=estado)

    def guardar_producto(self):
        cat = self.var_cat.get()
        if not cat:
            messagebox.showerror("Error", "Debes seleccionar una Categoría.")
            return

        costo = obtener_entero(self.var_costo, "El costo de compra")
        venta = obtener_entero(self.var_venta, "El precio de venta")
        stock = obtener_entero(self.var_stock, "El stock")
        stock_minimo = obtener_entero(self.var_stock_minimo, "El stock mínimo")
        if costo is None or venta is None or stock is None or stock_minimo is None:
            return

        inv = load_data(INV_FILE)
        cod_padre = self.generar_proximo_sku(cat, sumador=1)
        cod_hijo = self.generar_proximo_sku(cat, sumador=2) if self.var_es_conjunto.get() else ""
        
        prov_norm = normalizar_texto(self.var_prov.get())
        if prov_norm and prov_norm not in self.lista_proveedores:
            self.var_nuevo_prov.set(prov_norm)
            self.agregar_proveedor()

        padre = {
            "codigo": cod_padre,
            "nombre": self.var_nom.get(),
            "categoria": cat,
            "proveedor": prov_norm or "Sin Proveedor",
            "precio_compra": costo,
            "precio_venta": venta,
            "stock": stock,
            "stock_minimo": stock_minimo,
            "hijo_codigo": cod_hijo,
            "hijo_unidades": 0
        }
        inv.append(padre)

        if self.var_es_conjunto.get():
            unidades = obtener_entero(self.var_uni_hijo, "Las unidades del conjunto", minimo=1)
            precio_hijo = obtener_entero(self.var_venta_hijo, "El precio de venta unitario")
            if unidades is None or precio_hijo is None:
                return

            padre["hijo_unidades"] = unidades
            if unidades > 0:
                costo_hijo = costo // unidades
                hijo = {
                    "codigo": cod_hijo,
                    "nombre": f"{self.var_nom.get()} (UNIDAD)",
                    "categoria": cat,
                    "proveedor": prov_norm or "Sin Proveedor",
                    "precio_compra": costo_hijo,
                    "precio_venta": precio_hijo,
                    "stock": 0,
                    "stock_minimo": stock_minimo,
                    "hijo_codigo": "",
                    "hijo_unidades": 0
                }
                inv.append(hijo)

        save_data(INV_FILE, inv)
        movimientos = load_data(MOVEMENTS_FILE)
        movimientos.append({
            "tipo": "entrada_inicial",
            "codigo": cod_padre,
            "cantidad": stock,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        save_data(MOVEMENTS_FILE, movimientos)
        self.actualizar_tabla_inv()
        self.actualizar_codigos_compra()
        self.actualizar_tabla_ventas()
        
        self.var_nom.set("")
        self.var_stock.set(0)
        self.var_stock_minimo.set(DEFAULT_MIN_STOCK)
        self.var_cod.set("(Selecciona Categoría)")
        self.var_cat.set("")
        messagebox.showinfo("Éxito", "Producto(s) guardado(s).")

    def registrar_compra(self):
        codigo = self.var_compra_codigo.get().strip().upper()
        cantidad = obtener_entero(self.var_compra_cantidad, "La cantidad comprada", minimo=1)
        costo_unitario = obtener_entero(
            self.var_compra_costo, "El nuevo costo unitario", minimo=0
        )
        if cantidad is None or costo_unitario is None:
            return

        inv = load_data(INV_FILE)
        producto = next((p for p in inv if p["codigo"] == codigo), None)
        if producto is None:
            messagebox.showerror("Error", "Selecciona un código de producto válido.")
            return

        cambios_costos = self.preparar_actualizacion_costos(
            inv, producto, costo_unitario
        )
        if cambios_costos is None:
            return

        producto["stock"] = entero_desde_dato(producto.get("stock"), 0) + cantidad
        for producto_cambio, costo_cambio in cambios_costos:
            producto_cambio["precio_compra"] = costo_cambio
        save_data(INV_FILE, inv)
        movimientos = load_data(MOVEMENTS_FILE)
        movimientos.append({
            "tipo": "compra",
            "codigo": codigo,
            "cantidad": cantidad,
            "costo_unitario": costo_unitario,
            "costo_total": costo_unitario * cantidad,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        for producto_cambio, costo_cambio in cambios_costos[1:]:
            movimientos.append({
                "tipo": "actualizacion_costo",
                "codigo": producto_cambio["codigo"],
                "cantidad": 0,
                "costo_unitario": costo_cambio,
                "fecha": datetime.now().strftime("%Y-%m-%d")
            })
        save_data(MOVEMENTS_FILE, movimientos)
        self.actualizar_tabla_inv()
        self.actualizar_codigos_compra()
        self.actualizar_tabla_ventas()
        messagebox.showinfo("Éxito", f"Se agregaron {cantidad} unidades a {codigo}.")

    def desarmar_empaque(self):
        inv = load_data(INV_FILE)
        cod_origen = self.cod_desarmar.get().strip().upper()
        idx_origen = next((i for i, p in enumerate(inv) if p["codigo"] == cod_origen), None)

        if idx_origen is not None:
            padre = inv[idx_origen]
            if padre.get("hijo_codigo") and padre.get("hijo_unidades", 0) > 0:
                idx_hijo = next((i for i, p in enumerate(inv) if p["codigo"] == padre["hijo_codigo"]), None)
                if idx_hijo is not None:
                    if padre["stock"] >= 1:
                        inv[idx_origen]["stock"] -= 1
                        inv[idx_hijo]["stock"] += padre["hijo_unidades"]
                        save_data(INV_FILE, inv)
                        movimientos = load_data(MOVEMENTS_FILE)
                        movimientos.append({
                            "tipo": "desarmado",
                            "codigo": cod_origen,
                            "cantidad": 1,
                            "fecha": datetime.now().strftime("%Y-%m-%d")
                        })
                        save_data(MOVEMENTS_FILE, movimientos)
                        self.actualizar_tabla_inv()
                        self.actualizar_tabla_ventas()
                        messagebox.showinfo("Éxito", f"1 Manga desarmada. Se sumaron {padre['hijo_unidades']} al stock.")
                    else:
                        messagebox.showerror("Error", "No queda stock.")
                else:
                    messagebox.showerror("Error", "No se encontró el producto suelto asociado.")
            else:
                messagebox.showerror("Error", "Este producto no está configurado como conjunto/manga.")
        else:
            messagebox.showerror("Error", "Código de manga no encontrado.")

    def actualizar_tabla_inv(self):
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        inv = load_data(INV_FILE)
        filtro = self.var_filtro.get()
        stock_bajo = []
        for p in inv:
            if not filtro or p.get("categoria") == filtro:
                item_id = self.tree_inv.insert("", "end", values=(
                    p["codigo"], p["nombre"], p.get("categoria", ""), 
                    f"${p['precio_compra']:,.0f}", f"${p['precio_venta']:,.0f}", 
                    p["stock"], p.get("stock_minimo", DEFAULT_MIN_STOCK),
                    p.get("proveedor", "")
                ))
                if p["stock"] <= p.get("stock_minimo", DEFAULT_MIN_STOCK):
                    self.tree_inv.item(item_id, tags=("stock_bajo",))
                    stock_bajo.append(p["nombre"])
        self.tree_inv.tag_configure("stock_bajo", background="#f7d9d9")
        if stock_bajo:
            self.tree_inv.heading("Mínimo", text="Mínimo ⚠")

    # --- PESTAÑA VENTAS RÁPIDAS ---
    def setup_ventas(self):
        frame_lista = tk.LabelFrame(self.tab_ventas, text="Selecciona un producto de la lista para vender", font=("Arial", 10, "bold"))
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)
        
        frame_busqueda = tk.Frame(frame_lista)
        frame_busqueda.pack(fill="x", pady=5, padx=10)
        tk.Label(frame_busqueda, text="🔍 Buscar por nombre o código:").pack(side="left")
        self.var_buscar_venta = tk.StringVar()
        entry_busqueda = tk.Entry(frame_busqueda, textvariable=self.var_buscar_venta, font=("Arial", 11), width=40)
        entry_busqueda.pack(side="left", padx=10)
        entry_busqueda.bind('<KeyRelease>', self.filtrar_tabla_ventas)

        self.tree_ventas = ttk.Treeview(frame_lista, columns=("Cod", "Nombre", "Precio Venta", "Stock"), show="headings", height=8)
        for col in self.tree_ventas["columns"]:
            self.tree_ventas.heading(col, text=col)
            self.tree_ventas.column(col, width=120)
        self.tree_ventas.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree_ventas.bind('<ButtonRelease-1>', self.seleccionar_producto_venta)

        frame_form = tk.Frame(self.tab_ventas)
        frame_form.pack(pady=10)
        
        tk.Label(frame_form, text="Código a Vender:", font=("Arial", 12)).grid(row=0, column=0, pady=10, padx=5)
        self.venta_cod_var = tk.StringVar()
        tk.Entry(frame_form, textvariable=self.venta_cod_var, font=("Arial", 12)).grid(row=0, column=1, pady=10)

        tk.Label(frame_form, text="Cantidad:", font=("Arial", 12)).grid(row=1, column=0, pady=10, padx=5)
        self.venta_cant_var = tk.StringVar(value="1")
        tk.Entry(frame_form, textvariable=self.venta_cant_var, font=("Arial", 12)).grid(row=1, column=1, pady=10)

        tk.Button(frame_form, text="🛒 Registrar Venta", font=("Arial", 13, "bold"), bg="#dff0d8", command=self.registrar_venta).grid(row=2, column=0, columnspan=2, pady=15)
        
        self.actualizar_tabla_ventas()

    def actualizar_tabla_ventas(self, event=None):
        for i in self.tree_ventas.get_children(): self.tree_ventas.delete(i)
        inv = load_data(INV_FILE)
        busqueda = self.var_buscar_venta.get().lower()
        for p in inv:
            if busqueda in p["nombre"].lower() or busqueda in p["codigo"].lower():
                self.tree_ventas.insert("", "end", values=(
                    p["codigo"], p["nombre"], f"${p['precio_venta']:,.0f}", p["stock"]
                ))

    def filtrar_tabla_ventas(self, event):
        self.actualizar_tabla_ventas()

    def seleccionar_producto_venta(self, event):
        seleccion = self.tree_ventas.selection()
        if seleccion:
            valores = self.tree_ventas.item(seleccion[0])['values']
            self.venta_cod_var.set(valores[0]) 
            self.venta_cant_var.set(1)

    def registrar_venta(self):
        inv = load_data(INV_FILE)
        cod_prod = self.venta_cod_var.get().strip().upper() 
        cant = obtener_entero(self.venta_cant_var, "La cantidad", minimo=1)
        if cant is None:
            return

        for p in inv:
            if p["codigo"] == cod_prod:
                if p["stock"] >= cant:
                    p["stock"] -= cant
                    save_data(INV_FILE, inv)
                    ventas = load_data(SALES_FILE)
                    ventas.append({
                        "codigo": cod_prod,
                        "nombre": p["nombre"],
                        "cantidad": cant,
                        "costo_unitario": int(p["precio_compra"]),
                        "costo_total": int(p["precio_compra"]) * cant,
                        "precio_unitario": int(p["precio_venta"]),
                        "venta_total": int(p["precio_venta"]) * cant,
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(SALES_FILE, ventas)
                    movimientos = load_data(MOVEMENTS_FILE)
                    movimientos.append({
                        "tipo": "venta",
                        "codigo": cod_prod,
                        "cantidad": cant,
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(MOVEMENTS_FILE, movimientos)
                    self.actualizar_tabla_inv()
                    self.actualizar_tabla_ventas()
                    self.actualizar_dashboard()
                    messagebox.showinfo("Éxito", f"Vendiste {cant} x {p['nombre']}.")
                    self.venta_cod_var.set("")
                    self.venta_cant_var.set(1)
                    return
                else:
                    messagebox.showerror("Error", f"Solo te quedan {p['stock']} unidades.")
                    return
        messagebox.showerror("Error", "Código no encontrado")

    # --- PESTAÑA DASHBOARD (REDISEÑADA) ---
    def setup_dashboard(self):
        marco_scroll = tk.Frame(self.tab_dash)
        marco_scroll.pack(fill="both", expand=True)

        canvas_scroll = tk.Canvas(marco_scroll, highlightthickness=0)
        barra_scroll = ttk.Scrollbar(
            marco_scroll, orient="vertical", command=canvas_scroll.yview
        )
        contenido_dashboard = tk.Frame(canvas_scroll)
        ventana_dashboard = canvas_scroll.create_window(
            (0, 0), window=contenido_dashboard, anchor="nw"
        )
        canvas_scroll.configure(yscrollcommand=barra_scroll.set)
        canvas_scroll.pack(side="left", fill="both", expand=True)
        barra_scroll.pack(side="right", fill="y")

        def actualizar_scroll(event=None):
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))

        def ajustar_ancho(event):
            canvas_scroll.itemconfigure(ventana_dashboard, width=event.width)

        contenido_dashboard.bind("<Configure>", actualizar_scroll)
        canvas_scroll.bind("<Configure>", ajustar_ancho)
        def desplazar_con_rueda(event):
            canvas_scroll.yview_scroll(int(-event.delta / 120), "units")

        canvas_scroll.bind("<Enter>", lambda event: canvas_scroll.bind_all(
            "<MouseWheel>", desplazar_con_rueda
        ))
        canvas_scroll.bind("<Leave>", lambda event: canvas_scroll.unbind_all(
            "<MouseWheel>"
        ))

        # Botón de refresco global
        frame_top = tk.Frame(contenido_dashboard)
        frame_top.pack(fill="x", padx=10, pady=5)
        tk.Button(frame_top, text="🔄 Refrescar Datos", font=("Arial", 11, "bold"), bg="#5bc0de", fg="white", command=self.actualizar_dashboard).pack(pady=5)

        frame_periodo = tk.LabelFrame(contenido_dashboard, text="Periodo de resultados", font=("Arial", 10, "bold"))
        frame_periodo.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_periodo, text="Desde (AAAA-MM-DD):").pack(side="left", padx=(10, 5), pady=8)
        self.var_fecha_inicio = tk.StringVar()
        tk.Entry(frame_periodo, textvariable=self.var_fecha_inicio, width=12).pack(side="left", padx=5)

        tk.Label(frame_periodo, text="Hasta (AAAA-MM-DD):").pack(side="left", padx=(15, 5), pady=8)
        self.var_fecha_fin = tk.StringVar()
        tk.Entry(frame_periodo, textvariable=self.var_fecha_fin, width=12).pack(side="left", padx=5)

        tk.Button(
            frame_periodo,
            text="Aplicar periodo",
            bg="#5cb85c",
            fg="white",
            command=self.actualizar_dashboard
        ).pack(side="left", padx=10)

        self.lbl_aviso_pred = tk.Label(
            frame_periodo,
            text="",
            font=("Arial", 9, "bold"),
            fg="#c46a00",
            wraplength=500,
            justify="left"
        )
        self.lbl_aviso_pred.pack(side="left", padx=10, pady=5)

        # 1. Módulo: Contabilidad Pura
        self.frame_conta = tk.LabelFrame(contenido_dashboard, text="📊 Contabilidad Pura", font=("Arial", 12, "bold"), fg="#333")
        self.frame_conta.pack(fill="x", padx=20, pady=10)

        # Labels gigantes para mejor visualización
        self.lbl_ingresos = tk.Label(self.frame_conta, text="Ingresos Totales (Ventas): $0", font=("Arial", 13, "bold"), fg="#4cae4c")
        self.lbl_ingresos.pack(pady=5)
        
        self.lbl_costos = tk.Label(self.frame_conta, text="Costos Totales (Mercadería): $0", font=("Arial", 11), fg="#d9534f")
        self.lbl_costos.pack(pady=5)
        
        self.lbl_ganancia = tk.Label(self.frame_conta, text="GANANCIA NETA REAL: $0", font=("Arial", 15, "bold"), fg="#0275d8")
        self.lbl_ganancia.pack(pady=10)

        # 2. Módulo: Inteligencia y Predicción
        self.frame_pred = tk.LabelFrame(contenido_dashboard, text="🤖 Predicción de Stock (basada en el periodo elegido)", font=("Arial", 12, "bold"), fg="#333")
        self.frame_pred.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla visual (Treeview) para los datos predictivos
        self.tree_pred = ttk.Treeview(self.frame_pred, columns=("Producto", "Total Vendido", "Promedio Diario", "Predicción Mes"), show="headings", height=8)
        
        # Configuración de columnas
        self.tree_pred.heading("Producto", text="Producto")
        self.tree_pred.column("Producto", width=200, anchor="w")
        
        self.tree_pred.heading("Total Vendido", text="Total Vendido (Histórico)")
        self.tree_pred.column("Total Vendido", width=150, anchor="center")
        
        self.tree_pred.heading("Promedio Diario", text="Velocidad (Promedio Diario)")
        self.tree_pred.column("Promedio Diario", width=150, anchor="center")
        
        self.tree_pred.heading("Predicción Mes", text="⚠️ Necesitas Comprar (30 Días)")
        self.tree_pred.column("Predicción Mes", width=200, anchor="center")
        
        self.tree_pred.pack(fill="both", expand=True, padx=10, pady=10)

        frame_historial = tk.LabelFrame(contenido_dashboard, text="Historial de ventas")
        frame_historial.pack(fill="both", expand=True, padx=20, pady=5)
        frame_hist_filtros = tk.Frame(frame_historial)
        frame_hist_filtros.pack(fill="x", padx=5, pady=3)
        tk.Label(frame_hist_filtros, text="Buscar:").pack(side="left")
        self.var_historial_busqueda = tk.StringVar()
        tk.Entry(frame_hist_filtros, textvariable=self.var_historial_busqueda, width=25).pack(side="left", padx=5)
        tk.Button(frame_hist_filtros, text="Filtrar", command=self.actualizar_historial).pack(side="left")
        tk.Button(frame_hist_filtros, text="Anular venta seleccionada", bg="#d9534f", fg="white",
                  command=self.anular_venta).pack(side="right", padx=5)
        self.tree_historial = ttk.Treeview(
            frame_historial,
            columns=("Fecha", "Producto", "Cantidad", "Total"),
            show="headings",
            height=5
        )
        for col in self.tree_historial["columns"]:
            self.tree_historial.heading(col, text=col)
            self.tree_historial.column(col, width=130)
        self.tree_historial.pack(fill="both", expand=True, padx=5, pady=3)

        frame_gastos = tk.LabelFrame(contenido_dashboard, text="Gastos adicionales")
        frame_gastos.pack(fill="x", padx=20, pady=5)
        self.var_gasto_concepto = tk.StringVar()
        self.var_gasto_monto = tk.StringVar(value="0")
        tk.Entry(frame_gastos, textvariable=self.var_gasto_concepto, width=22).pack(side="left", padx=5, pady=5)
        tk.Entry(frame_gastos, textvariable=self.var_gasto_monto, width=12).pack(side="left", padx=5)
        tk.Button(frame_gastos, text="Registrar gasto", command=self.registrar_gasto).pack(side="left", padx=5)
        self.lbl_gastos = tk.Label(frame_gastos, text="Gastos del periodo: $0")
        self.lbl_gastos.pack(side="left", padx=15)

        self.canvas_grafico = tk.Canvas(contenido_dashboard, height=225, bg="white", highlightthickness=1)
        self.canvas_grafico.pack(fill="x", padx=20, pady=5)

        self.establecer_periodo_inicial()
        self.actualizar_dashboard()
        self.actualizar_historial()

    def registrar_gasto(self):
        concepto = self.var_gasto_concepto.get().strip()
        monto = obtener_entero(self.var_gasto_monto, "El monto del gasto", minimo=1)
        if not concepto:
            messagebox.showerror("Dato inválido", "Ingresa el concepto del gasto.")
            return
        if monto is None:
            return
        gastos = load_data(EXPENSES_FILE)
        gastos.append({
            "concepto": concepto,
            "monto": monto,
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        save_data(EXPENSES_FILE, gastos)
        self.var_gasto_concepto.set("")
        self.var_gasto_monto.set("0")
        self.actualizar_dashboard()

    def actualizar_historial(self):
        if not hasattr(self, "tree_historial"):
            return
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        busqueda = self.var_historial_busqueda.get().strip().lower()
        try:
            fecha_inicio = datetime.strptime(self.var_fecha_inicio.get(), "%Y-%m-%d")
            fecha_fin = datetime.strptime(self.var_fecha_fin.get(), "%Y-%m-%d")
        except ValueError:
            fecha_inicio = fecha_fin = None
        for index, venta in enumerate(load_data(SALES_FILE)):
            texto = f"{venta.get('codigo', '')} {venta.get('nombre', '')}".lower()
            if busqueda and busqueda not in texto:
                continue
            try:
                fecha_venta = datetime.strptime(venta.get("fecha", ""), "%Y-%m-%d")
            except (TypeError, ValueError):
                continue
            if fecha_inicio and not (fecha_inicio <= fecha_venta <= fecha_fin):
                continue
            self.tree_historial.insert(
                "", "end", iid=str(index),
                values=(venta.get("fecha", ""), venta.get("nombre", ""),
                        entero_desde_dato(venta.get("cantidad"), 0),
                        f"${entero_desde_dato(venta.get('venta_total'), 0):,}")
            )

    def anular_venta(self):
        seleccion = self.tree_historial.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una venta del historial.")
            return
        indice = int(seleccion[0])
        ventas = load_data(SALES_FILE)
        if indice >= len(ventas):
            messagebox.showerror("Error", "La venta seleccionada ya no existe.")
            return
        venta = ventas.pop(indice)
        inv = load_data(INV_FILE)
        producto = next((p for p in inv if p["codigo"] == venta.get("codigo")), None)
        if producto is None:
            messagebox.showerror("Error", "No se encontró el producto para devolver el stock.")
            return
        producto["stock"] += entero_desde_dato(venta.get("cantidad"), 0)
        save_data(INV_FILE, inv)
        save_data(SALES_FILE, ventas)
        movimientos = load_data(MOVEMENTS_FILE)
        movimientos.append({
            "tipo": "anulacion",
            "codigo": venta.get("codigo", ""),
            "cantidad": entero_desde_dato(venta.get("cantidad"), 0),
            "fecha": datetime.now().strftime("%Y-%m-%d")
        })
        save_data(MOVEMENTS_FILE, movimientos)
        self.actualizar_historial()
        self.actualizar_tabla_inv()
        self.actualizar_tabla_ventas()
        self.actualizar_dashboard()
        messagebox.showinfo("Éxito", "Venta anulada y stock devuelto.")

    def establecer_periodo_inicial(self):
        ventas = load_data(SALES_FILE)
        fechas = []
        for venta in ventas:
            try:
                fechas.append(datetime.strptime(venta["fecha"], "%Y-%m-%d"))
            except (KeyError, TypeError, ValueError):
                continue

        hoy = datetime.now().strftime("%Y-%m-%d")
        self.var_fecha_inicio.set(min(fechas).strftime("%Y-%m-%d") if fechas else hoy)
        self.var_fecha_fin.set(hoy)

    def obtener_periodo_dashboard(self):
        try:
            fecha_inicio = datetime.strptime(self.var_fecha_inicio.get().strip(), "%Y-%m-%d")
            fecha_fin = datetime.strptime(self.var_fecha_fin.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Periodo inválido",
                "Usa fechas válidas con el formato AAAA-MM-DD."
            )
            return None

        if fecha_inicio > fecha_fin:
            messagebox.showerror(
                "Periodo inválido",
                "La fecha inicial no puede ser posterior a la fecha final."
            )
            return None

        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        return fecha_inicio, fecha_fin, dias_periodo

    def actualizar_dashboard(self):
        ventas = load_data(SALES_FILE)
        periodo = self.obtener_periodo_dashboard()
        if periodo is None:
            return

        fecha_inicio, fecha_fin, dias_periodo = periodo
        
        # Limpiar tabla de predicción
        for i in self.tree_pred.get_children(): self.tree_pred.delete(i)

        total_ingresos = total_costos = 0
        resumen = {}
        ventas_periodo = 0

        for v in ventas:
            try:
                fecha = datetime.strptime(v["fecha"], "%Y-%m-%d")
            except (KeyError, TypeError, ValueError):
                continue

            if not (fecha_inicio <= fecha <= fecha_fin):
                continue

            ventas_periodo += 1
            total_ingresos += ingreso_total_venta(v)
            total_costos += costo_total_venta(v)
            prod = f"{v['codigo']} - {v['nombre']}"
            
            if prod not in resumen:
                resumen[prod] = {"total_vendido": 0, "primera_venta": fecha, "ultima_venta": fecha}
            
            resumen[prod]["total_vendido"] += v["cantidad"]
            if fecha < resumen[prod]["primera_venta"]: resumen[prod]["primera_venta"] = fecha
            if fecha > resumen[prod]["ultima_venta"]: resumen[prod]["ultima_venta"] = fecha

        ganancia_neta = total_ingresos - total_costos
        total_gastos = 0
        for gasto in load_data(EXPENSES_FILE):
            try:
                fecha_gasto = datetime.strptime(gasto.get("fecha", ""), "%Y-%m-%d")
            except (TypeError, ValueError):
                continue
            if fecha_inicio <= fecha_gasto <= fecha_fin:
                total_gastos += entero_desde_dato(gasto.get("monto"), 0)
        ganancia_real = ganancia_neta - total_gastos

        # Actualizar Contabilidad Pura
        self.lbl_ingresos.config(text=f"Ingresos Totales (Ventas): ${total_ingresos:,.0f}")
        self.lbl_costos.config(text=f"Costos Totales (Mercadería): ${total_costos:,.0f}")
        self.lbl_ganancia.config(text=f"GANANCIA REAL: ${ganancia_real:,.0f}")
        self.lbl_gastos.config(text=f"Gastos del periodo: ${total_gastos:,.0f}")
        self.actualizar_historial()

        avisos = []
        if dias_periodo < MIN_PREDICTION_DAYS:
            avisos.append(
                f"⚠️ Periodo de solo {dias_periodo} día(s): la predicción puede fallar "
                f"por poca data. Se recomiendan al menos {MIN_PREDICTION_DAYS} días."
            )
        if not ventas_periodo:
            avisos.append("No hay ventas dentro del periodo elegido; no hay data para predecir.")
        self.lbl_aviso_pred.config(text=" ".join(avisos))
        
        # Actualizar Predicción de Stock en la Tabla
        for prod, data in resumen.items():
            promedio_diario = data["total_vendido"] // dias_periodo
            proyeccion_mes = promedio_diario * 30
            
            self.tree_pred.insert("", "end", values=(
                prod, 
                f"{data['total_vendido']} unid.", 
                f"{promedio_diario} u/día", 
                f"{proyeccion_mes} unid."
            ))
        self.dibujar_grafico(resumen)

    def dibujar_grafico(self, resumen):
        self.canvas_grafico.delete("all")
        datos = sorted(
            ((nombre, valores["total_vendido"]) for nombre, valores in resumen.items()),
            key=lambda dato: dato[1], reverse=True
        )[:6]
        if not datos:
            self.canvas_grafico.create_text(400, 80, text="Sin ventas para graficar")
            return
        maximo = max(valor for _, valor in datos) or 1
        ancho = max(self.canvas_grafico.winfo_width(), len(datos) * 125)
        self.canvas_grafico.configure(width=ancho)
        margen = 25
        espacio = max(105, (ancho - margen * 2) // len(datos))
        barra = min(70, espacio - 25)
        for indice, (nombre, valor) in enumerate(datos):
            x = margen + indice * espacio + (espacio - barra) // 2
            alto = int((valor / maximo) * 120)
            self.canvas_grafico.create_rectangle(x, 145 - alto, x + barra, 145, fill="#337ab7")
            codigo, separador, nombre_producto = nombre.partition(" - ")
            etiqueta = f"{codigo}\n{nombre_producto[:12]}" if separador else nombre[:14]
            self.canvas_grafico.create_text(
                x + barra // 2,
                157,
                text=etiqueta,
                font=("Arial", 8),
                justify="center",
                anchor="n"
            )
            self.canvas_grafico.create_text(x + barra // 2, 135 - alto, text=str(valor))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppAdministrador(root)
    root.mainloop()
