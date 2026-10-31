import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta

# Archivos de base de datos
INV_FILE = "inventario.json"
SALES_FILE = "ventas.json"
CAT_FILE = "categorias.json"
PROV_FILE = "proveedores.json"

for f in [INV_FILE, SALES_FILE, CAT_FILE, PROV_FILE]:
    if not os.path.exists(f):
        if f == CAT_FILE:
            with open(f, "w") as file: json.dump({"Sin Categoría": "GEN"}, file)
        elif f == PROV_FILE:
            with open(f, "w") as file: json.dump(["Sin Proveedor"], file)
        else:
            with open(f, "w") as file: json.dump([], file)

def load_data(file):
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

def normalizar_texto(texto):
    if not texto: return ""
    return " ".join(palabra.capitalize() for palabra in texto.strip().split())

class AppAdministrador:
    def __init__(self, root):
        self.root = root
        self.root.title("APP ADMINISTRADOR - Sistema Pro Automático")
        self.root.geometry("1150x800")
        
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
        self.tab_historial = ttk.Frame(notebook)
        self.tab_cat_prov = ttk.Frame(notebook)
        self.tab_dash = ttk.Frame(notebook)
        self.tab_sync = ttk.Frame(notebook)

        notebook.add(self.tab_inv, text="📦 Inventario")
        notebook.add(self.tab_ventas, text="🛒 Ventas Rápidas")
        notebook.add(self.tab_historial, text="📜 Historial de Ventas")
        notebook.add(self.tab_cat_prov, text="🏷️ Categorías & Prov.")
        notebook.add(self.tab_dash, text="📊 Dash & Gráficos")
        notebook.add(self.tab_sync, text="📱 Sync Móvil")

        self.setup_cat_prov() 
        self.setup_inventario()
        self.setup_ventas()
        self.setup_historial()
        self.setup_dashboard()
        self.setup_sync() 

    # =========================================================================
    # FUNCIÓN GLOBAL DE FILTRADO POR PERÍODO Y RANGO DE FECHAS
    # =========================================================================
    def filtrar_ventas(self, ventas, periodo, busqueda="", desde="", hasta=""):
        hoy = datetime.now().date()
        filtradas = []
        b = busqueda.lower().strip()
        
        for v in ventas:
            # 1. Filtro por texto (Buscador)
            if b and b not in v.get("nombre", "").lower() and b not in v.get("codigo", "").lower():
                continue
                
            # 2. Filtro por periodo
            try:
                fecha_v = datetime.strptime(v.get("fecha", ""), "%Y-%m-%d").date()
            except ValueError:
                fecha_v = hoy # Fallback si no hay fecha válida
                
            if periodo == "Hoy" and fecha_v != hoy:
                continue
            elif periodo == "Últimos 7 días" and (hoy - fecha_v).days > 7:
                continue
            elif periodo == "Últimos 30 días" and (hoy - fecha_v).days > 30:
                continue
            elif periodo == "Este Mes" and (fecha_v.month != hoy.month or fecha_v.year != hoy.year):
                continue
            elif periodo == "Rango Personalizado":
                try:
                    d = datetime.strptime(desde, "%Y-%m-%d").date() if desde else None
                    h = datetime.strptime(hasta, "%Y-%m-%d").date() if hasta else None
                    if d and fecha_v < d:
                        continue
                    if h and fecha_v > h:
                        continue
                except ValueError:
                    pass # Si hay un error de tipeo en la fecha, ignoramos el filtro en ese momento
                
            filtradas.append(v)
            
        return filtradas

    # =========================================================================
    # HISTORIAL DE VENTAS CON RANGO PERSONALIZADO
    # =========================================================================
    def setup_historial(self):
        tk.Label(self.tab_historial, text="Registro Histórico de Ventas", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_filtros = tk.Frame(self.tab_historial)
        frame_filtros.pack(fill="x", padx=20, pady=5)
        
        tk.Label(frame_filtros, text="🔍 Buscar:").pack(side="left")
        self.var_buscar_hist = tk.StringVar()
        entry_b_hist = tk.Entry(frame_filtros, textvariable=self.var_buscar_hist, font=("Arial", 11), width=20)
        entry_b_hist.pack(side="left", padx=5)
        entry_b_hist.bind("<KeyRelease>", lambda e: self.actualizar_historial())

        tk.Label(frame_filtros, text="📅 Período:").pack(side="left", padx=(10, 5))
        self.var_periodo_hist = tk.StringVar(value="Todo el tiempo")
        cb_per_hist = ttk.Combobox(frame_filtros, textvariable=self.var_periodo_hist, state="readonly", width=17, font=("Arial", 10))
        cb_per_hist['values'] = ["Todo el tiempo", "Hoy", "Últimos 7 días", "Últimos 30 días", "Este Mes", "Rango Personalizado"]
        cb_per_hist.pack(side="left", padx=5)
        cb_per_hist.bind("<<ComboboxSelected>>", self.toggle_rango_fechas_hist)
        
        self.frame_fechas_hist = tk.Frame(frame_filtros)
        tk.Label(self.frame_fechas_hist, text="Desde:").pack(side="left")
        self.var_desde_hist = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
        tk.Entry(self.frame_fechas_hist, textvariable=self.var_desde_hist, width=11).pack(side="left", padx=2)
        tk.Label(self.frame_fechas_hist, text="Hasta:").pack(side="left")
        self.var_hasta_hist = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(self.frame_fechas_hist, textvariable=self.var_hasta_hist, width=11).pack(side="left", padx=2)
        
        tk.Button(frame_filtros, text="🔄 Refrescar", bg="#5bc0de", fg="white", font=("Arial", 9, "bold"), command=self.actualizar_historial).pack(side="left", padx=15)

        self.tree_hist = ttk.Treeview(self.tab_historial, columns=("Fecha", "Cod", "Nombre", "Cant", "Total"), show="headings")
        self.tree_hist.heading("Fecha", text="Fecha de Venta")
        self.tree_hist.heading("Cod", text="Código")
        self.tree_hist.heading("Nombre", text="Producto")
        self.tree_hist.heading("Cant", text="Cantidad")
        self.tree_hist.heading("Total", text="Ingreso Total")
        
        self.tree_hist.column("Fecha", width=120, anchor="center")
        self.tree_hist.column("Cod", width=100, anchor="center")
        self.tree_hist.column("Nombre", width=300, anchor="w")
        self.tree_hist.column("Cant", width=80, anchor="center")
        self.tree_hist.column("Total", width=100, anchor="e")
        
        self.tree_hist.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualizar_historial()

    def toggle_rango_fechas_hist(self, event=None):
        if self.var_periodo_hist.get() == "Rango Personalizado":
            self.frame_fechas_hist.pack(side="left", padx=5, before=self.frame_fechas_hist.master.winfo_children()[-1])
        else:
            self.frame_fechas_hist.pack_forget()
        self.actualizar_historial()

    def actualizar_historial(self):
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        
        ventas_crudas = load_data(SALES_FILE)
        periodo = self.var_periodo_hist.get()
        busqueda = self.var_buscar_hist.get()
        desde = self.var_desde_hist.get()
        hasta = self.var_hasta_hist.get()
        
        ventas_filtradas = self.filtrar_ventas(ventas_crudas, periodo, busqueda, desde, hasta)
        
        for v in reversed(ventas_filtradas):
            self.tree_hist.insert("", "end", values=(
                v.get("fecha", ""), 
                v.get("codigo", ""), 
                v.get("nombre", ""),
                f"{v.get('cantidad', 0)} u.", 
                f"${v.get('venta_total', 0):,.0f}"
            ))

    # =========================================================================
    # PESTAÑA DASHBOARD Y GRÁFICOS (CON RANGO PERSONALIZADO)
    # =========================================================================
    def setup_dashboard(self):
        frame_filtros = tk.Frame(self.tab_dash)
        frame_filtros.pack(fill="x", padx=20, pady=10)
        
        tk.Label(frame_filtros, text="📅 Analizar Período:", font=("Arial", 11, "bold")).pack(side="left")
        self.var_periodo_dash = tk.StringVar(value="Todo el tiempo")
        cb_per_dash = ttk.Combobox(frame_filtros, textvariable=self.var_periodo_dash, state="readonly", width=17, font=("Arial", 11))
        cb_per_dash['values'] = ["Todo el tiempo", "Hoy", "Últimos 7 días", "Últimos 30 días", "Este Mes", "Rango Personalizado"]
        cb_per_dash.pack(side="left", padx=10)
        cb_per_dash.bind("<<ComboboxSelected>>", self.toggle_rango_fechas_dash)

        self.frame_fechas_dash = tk.Frame(frame_filtros)
        tk.Label(self.frame_fechas_dash, text="Desde (AAAA-MM-DD):").pack(side="left")
        self.var_desde_dash = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
        tk.Entry(self.frame_fechas_dash, textvariable=self.var_desde_dash, width=11).pack(side="left", padx=2)
        tk.Label(self.frame_fechas_dash, text="Hasta:").pack(side="left")
        self.var_hasta_dash = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(self.frame_fechas_dash, textvariable=self.var_hasta_dash, width=11).pack(side="left", padx=2)

        tk.Button(frame_filtros, text="🔄 Actualizar Dash", font=("Arial", 10, "bold"), bg="#5bc0de", fg="white", command=self.actualizar_dashboard).pack(side="left", padx=10)
        
        # Módulo Contabilidad
        self.frame_conta = tk.LabelFrame(self.tab_dash, text="📊 Contabilidad Pura del Período", font=("Arial", 12, "bold"), fg="#333")
        self.frame_conta.pack(fill="x", padx=20, pady=5)
        
        frame_metrics = tk.Frame(self.frame_conta)
        frame_metrics.pack(pady=5)
        
        self.lbl_ingresos = tk.Label(frame_metrics, text="Ingresos (Ventas): $0", font=("Arial", 12, "bold"), fg="#4cae4c")
        self.lbl_ingresos.pack(side="left", padx=15)
        self.lbl_costos = tk.Label(frame_metrics, text="Costos (Mercadería): $0", font=("Arial", 11), fg="#d9534f")
        self.lbl_costos.pack(side="left", padx=15)
        self.lbl_ganancia = tk.Label(frame_metrics, text="GANANCIA NETA: $0", font=("Arial", 14, "bold"), fg="#0275d8")
        self.lbl_ganancia.pack(side="left", padx=15)

        # Módulo Gráfico
        self.frame_grafico = tk.LabelFrame(self.tab_dash, text="📈 Gráfico: Top 5 Productos Más Vendidos del Período", font=("Arial", 11, "bold"))
        self.frame_grafico.pack(fill="x", padx=20, pady=5)
        self.canvas = tk.Canvas(self.frame_grafico, bg="white", height=150)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=5)

        # Módulo Predicción
        self.frame_pred = tk.LabelFrame(self.tab_dash, text="🤖 Predicción de Stock (Inteligencia de Velocidad en el Período)", font=("Arial", 12, "bold"), fg="#333")
        self.frame_pred.pack(fill="both", expand=True, padx=20, pady=5)
        self.tree_pred = ttk.Treeview(self.frame_pred, columns=("Producto", "Total Vendido", "Promedio Diario", "Predicción Mes"), show="headings", height=5)
        self.tree_pred.heading("Producto", text="Producto"); self.tree_pred.column("Producto", width=200, anchor="w")
        self.tree_pred.heading("Total Vendido", text="Unid. Vendidas (Período)"); self.tree_pred.column("Total Vendido", width=150, anchor="center")
        self.tree_pred.heading("Promedio Diario", text="Velocidad Diaria"); self.tree_pred.column("Promedio Diario", width=150, anchor="center")
        self.tree_pred.heading("Predicción Mes", text="⚠️ Necesitas para 30 días"); self.tree_pred.column("Predicción Mes", width=200, anchor="center")
        self.tree_pred.pack(fill="both", expand=True, padx=10, pady=10)

    def toggle_rango_fechas_dash(self, event=None):
        if self.var_periodo_dash.get() == "Rango Personalizado":
            self.frame_fechas_dash.pack(side="left", padx=5, before=self.frame_fechas_dash.master.winfo_children()[-1])
        else:
            self.frame_fechas_dash.pack_forget()
        self.actualizar_dashboard()

    def actualizar_dashboard(self):
        ventas_crudas = load_data(SALES_FILE)
        periodo = self.var_periodo_dash.get()
        desde = self.var_desde_dash.get()
        hasta = self.var_hasta_dash.get()
        
        ventas = self.filtrar_ventas(ventas_crudas, periodo, desde=desde, hasta=hasta)
        
        for i in self.tree_pred.get_children(): self.tree_pred.delete(i)
        self.canvas.delete("all")
        
        if not ventas:
            self.lbl_ingresos.config(text="Ingresos (Ventas): $0")
            self.lbl_costos.config(text="Costos (Mercadería): $0")
            self.lbl_ganancia.config(text="GANANCIA NETA: $0")
            self.canvas.create_text(400, 75, text="No hay ventas en este período para graficar.", font=("Arial", 12), fill="gray")
            return
            
        total_ingresos = total_costos = 0
        resumen = {}
        
        for v in ventas:
            total_ingresos += v["venta_total"]
            total_costos += v["costo_total"]
            prod = f"{v['codigo']} - {v['nombre']}"
            fecha = datetime.strptime(v["fecha"], "%Y-%m-%d")
            
            if prod not in resumen: resumen[prod] = {"total_vendido": 0, "primera_venta": fecha, "ultima_venta": fecha}
            resumen[prod]["total_vendido"] += v["cantidad"]
            
            if fecha < resumen[prod]["primera_venta"]: resumen[prod]["primera_venta"] = fecha
            if fecha > resumen[prod]["ultima_venta"]: resumen[prod]["ultima_venta"] = fecha
            
        ganancia_neta = total_ingresos - total_costos
        self.lbl_ingresos.config(text=f"Ingresos (Ventas): ${total_ingresos:,.0f}")
        self.lbl_costos.config(text=f"Costos (Mercadería): ${total_costos:,.0f}")
        self.lbl_ganancia.config(text=f"GANANCIA NETA: ${ganancia_neta:,.0f}")
        
        hoy = datetime.now()
        for prod, data in resumen.items():
            if periodo == "Hoy":
                dias = 1
            elif periodo == "Rango Personalizado":
                try:
                    d = datetime.strptime(desde, "%Y-%m-%d").date()
                    h = datetime.strptime(hasta, "%Y-%m-%d").date()
                    dias = (h - d).days + 1
                except:
                    dias = (hoy - data["primera_venta"]).days
            else:
                dias = (hoy - data["primera_venta"]).days
                
            if dias <= 0: dias = 1 
                
            promedio = data["total_vendido"] / dias
            proyeccion = int(promedio * 30)
            self.tree_pred.insert("", "end", values=(prod, f"{data['total_vendido']} unid.", f"{promedio:.1f} u/día", f"{proyeccion} unid."))

        # DIBUJAR GRÁFICO
        top_prods = sorted(resumen.items(), key=lambda x: x[1]["total_vendido"], reverse=True)[:5]
        if top_prods:
            self.canvas.update_idletasks()
            c_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 10 else 800
            c_h = self.canvas.winfo_height() if self.canvas.winfo_height() > 10 else 150
            
            max_val = max(item[1]["total_vendido"] for item in top_prods)
            padding = 30
            bar_width = min(60, c_w / (len(top_prods) * 2))
            
            for i, (p_name, data) in enumerate(top_prods):
                val = data["total_vendido"]
                bar_h = (val / max_val) * (c_h - padding * 2) if max_val > 0 else 0
                
                x0 = padding + i * (bar_width * 1.5 + 20)
                y0 = c_h - padding - bar_h
                x1 = x0 + bar_width
                y1 = c_h - padding
                
                self.canvas.create_rectangle(x0, y0, x1, y1, fill="#5bc0de", outline="#31708f")
                self.canvas.create_text(x0 + bar_width/2, y0 - 10, text=f"{val} u.", font=("Arial", 10, "bold"), fill="#333")
                
                short_n = p_name.split(" - ")[-1][:12] + ".." if len(p_name.split(" - ")[-1]) > 12 else p_name.split(" - ")[-1]
                self.canvas.create_text(x0 + bar_width/2, y1 + 15, text=short_n, font=("Arial", 9))

    # =========================================================================
    # EL RESTO DEL CÓDIGO SE MANTIENE EXACTAMENTE IGUAL (Sync, Inv, Ventas, etc)
    # =========================================================================
    
    def setup_sync(self):
        tk.Label(self.tab_sync, text="Sincronización con Teléfono en Terreno", font=("Arial", 16, "bold")).pack(pady=20)
        frame_export = tk.LabelFrame(self.tab_sync, text="Paso 1: Antes de salir de casa", font=("Arial", 12, "bold"), fg="#0275d8")
        frame_export.pack(fill="x", padx=40, pady=10)
        tk.Label(frame_export, text="Exporta tu inventario actual para cargarlo en la App de tu celular.", font=("Arial", 11)).pack(pady=10)
        tk.Button(frame_export, text="📤 Exportar Inventario para Móvil (.json)", bg="#5bc0de", fg="white", font=("Arial", 12, "bold"), command=self.exportar_inventario_movil).pack(pady=15)
        frame_import = tk.LabelFrame(self.tab_sync, text="Paso 2: Al regresar a casa", font=("Arial", 12, "bold"), fg="#4cae4c")
        frame_import.pack(fill="x", padx=40, pady=10)
        tk.Label(frame_import, text="Importa el archivo de ventas que te generó el celular. Esto descontará el stock y calculará tus ganancias automáticamente.", font=("Arial", 11)).pack(pady=10)
        tk.Button(frame_import, text="📥 Importar Ventas del Móvil (.json)", bg="#5cb85c", fg="white", font=("Arial", 12, "bold"), command=self.importar_ventas_movil).pack(pady=15)

    def exportar_inventario_movil(self):
        inv = load_data(INV_FILE)
        if not inv: return messagebox.showwarning("Aviso", "El inventario está vacío.")
        file_path = filedialog.asksaveasfilename(title="Guardar Inventario para Celular", defaultextension=".json", initialfile="inventario_movil.json", filetypes=[("Archivos JSON", "*.json")])
        if not file_path: return
        try:
            with open(file_path, "w", encoding="utf-8") as f: json.dump(inv, f, indent=4)
            messagebox.showinfo("Éxito", f"Archivo guardado exitosamente.Envíate el archivo '{os.path.basename(file_path)}' al celular y cárgalo en tu App Móvil.")
        except Exception as e: messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def importar_ventas_movil(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo de ventas del celular", filetypes=[("Archivos JSON", "*.json")])
        if not file_path: return
        try:
            with open(file_path, "r", encoding="utf-8") as f: ventas_movil = json.load(f)
        except Exception as e: return messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
            
        inv = load_data(INV_FILE)
        ventas_pc = load_data(SALES_FILE)
        exito = errores = 0
        for v in ventas_movil:
            cod_prod = v.get("codigo")
            cant = v.get("cantidad", 0)
            fecha = v.get("fecha", datetime.now().strftime("%Y-%m-%d"))
            prod = next((p for p in inv if p["codigo"] == cod_prod), None)
            
            if prod:
                prod["stock"] -= cant 
                ventas_pc.append({
                    "codigo": cod_prod, "nombre": prod["nombre"], "cantidad": cant,
                    "costo_total": prod.get("precio_compra", 0) * cant,
                    "venta_total": prod.get("precio_venta", 0) * cant, "fecha": fecha
                })
                exito += 1
            else: errores += 1
                
        save_data(INV_FILE, inv)
        save_data(SALES_FILE, ventas_pc)
        self.actualizar_tabla_inv()
        self.actualizar_tabla_ventas()
        self.actualizar_dashboard()
        self.actualizar_historial()
        
        msg = f"Se importaron {exito} ventas provenientes del terreno."
        if errores > 0: msg += f"Hubo {errores} productos no encontrados (códigos modificados o eliminados)."
        messagebox.showinfo("Importación Finalizada", msg)

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
            else: messagebox.showwarning("Aviso", "La categoría ya existe.")
        else: messagebox.showwarning("Aviso", "Debes ingresar Nombre y Prefijo.")

    def eliminar_categoria(self):
        seleccion = self.list_cat.curselection()
        if not seleccion: return
        cat_info = self.list_cat.get(seleccion[0])
        cat_name = cat_info.split(" (Prefijo:")[0]
        if cat_name == "Sin Categoría": return messagebox.showwarning("Aviso", "No puedes eliminar la categoría predeterminada.")
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{cat_name}'? Sus productos pasarán a 'Sin Categoría', pero sus códigos se mantendrán."):
            del self.dict_categorias[cat_name]
            if "Sin Categoría" not in self.dict_categorias: self.dict_categorias["Sin Categoría"] = "GEN"
            save_data(CAT_FILE, self.dict_categorias)
            inv = load_data(INV_FILE)
            for p in inv:
                if p.get("categoria") == cat_name: p["categoria"] = "Sin Categoría"
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
        tk.Label(top, text="Prefijo (NO Editable):").pack(pady=5)
        var_pref = tk.StringVar(value=pref_old)
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
                        if p.get("categoria") == cat_name_old: p["categoria"] = nuevo_nom
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
        if prov_name == "Sin Proveedor": return messagebox.showwarning("Aviso", "No puedes eliminar el proveedor predeterminado.")
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{prov_name}'?"):
            self.lista_proveedores.remove(prov_name)
            if "Sin Proveedor" not in self.lista_proveedores: self.lista_proveedores.append("Sin Proveedor")
            save_data(PROV_FILE, self.lista_proveedores)
            inv = load_data(INV_FILE)
            for p in inv:
                if p.get("proveedor") == prov_name: p["proveedor"] = "Sin Proveedor"
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
                    if p.get("proveedor") == prov_old: p["proveedor"] = nuevo_nom
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
        for cat, pref in sorted(self.dict_categorias.items()): self.list_cat.insert(tk.END, f"{cat} (Prefijo: {pref})")
        self.list_prov.delete(0, tk.END)
        for p in self.lista_proveedores: self.list_prov.insert(tk.END, p)
        lista_cat_nombres = sorted(list(self.dict_categorias.keys()))
        if hasattr(self, 'combo_cat'): self.combo_cat['values'] = lista_cat_nombres
        if hasattr(self, 'combo_prov'): self.combo_prov['values'] = self.lista_proveedores
        if hasattr(self, 'combo_filtro'): self.combo_filtro['values'] = [""] + lista_cat_nombres

    def setup_inventario(self):
        frame_nuevo = tk.LabelFrame(self.tab_inv, text="Añadir Nuevo Producto")
        frame_nuevo.pack(fill="x", padx=10, pady=5)
        self.var_cod = tk.StringVar(value="(Selecciona Categoría)")
        self.var_nom = tk.StringVar()
        self.var_cat = tk.StringVar()
        self.var_prov = tk.StringVar()
        self.var_costo = tk.DoubleVar()
        self.var_venta = tk.DoubleVar()
        self.var_stock = tk.IntVar()
        self.var_es_conjunto = tk.BooleanVar()
        self.var_uni_hijo = tk.IntVar()
        self.var_venta_hijo = tk.DoubleVar()

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
        tk.Label(frame_nuevo, text="Costo Compra Total:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_costo).grid(row=1, column=3, padx=5, pady=2)
        tk.Label(frame_nuevo, text="Precio Venta:").grid(row=1, column=4, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_venta).grid(row=1, column=5, padx=5, pady=2)
        tk.Label(frame_nuevo, text="Stock Inicial:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        tk.Entry(frame_nuevo, textvariable=self.var_stock).grid(row=2, column=1, padx=5, pady=2)

        frame_conjunto = tk.Frame(frame_nuevo)
        frame_conjunto.grid(row=3, column=0, columnspan=6, pady=5)
        tk.Checkbutton(frame_conjunto, text="Este producto es una Manga/Conjunto (Genera unidad suelta)", variable=self.var_es_conjunto, command=self.toggle_conjunto, font=("Arial", 9, "bold")).pack(side="top", pady=2)
        
        self.panel_hijo = tk.Frame(frame_conjunto)
        self.panel_hijo.pack(side="top", pady=2)
        tk.Label(self.panel_hijo, text="Cod. Suelto: (Auto)").grid(row=0, column=0, padx=5)
        tk.Label(self.panel_hijo, text="¿Cuántas unidades trae?:").grid(row=0, column=2, padx=5)
        self.entry_uni_hijo = tk.Entry(self.panel_hijo, textvariable=self.var_uni_hijo, state="disabled")
        self.entry_uni_hijo.grid(row=0, column=3, padx=5)
        tk.Label(self.panel_hijo, text="Precio Venta (Suelto):").grid(row=0, column=4, padx=5)
        self.entry_venta_hijo = tk.Entry(self.panel_hijo, textvariable=self.var_venta_hijo, state="disabled")
        self.entry_venta_hijo.grid(row=0, column=5, padx=5)

        tk.Button(frame_nuevo, text="Guardar Producto(s)", bg="#d9edf7", command=self.guardar_producto).grid(row=4, column=0, columnspan=6, pady=10)

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

        self.tree_inv = ttk.Treeview(frame_tabla, columns=("Cod", "Nombre", "Cat", "Costo", "Venta", "Stock", "Prov"), show="headings")
        for col in self.tree_inv["columns"]:
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=90)
        self.tree_inv.pack(fill="both", expand=True, pady=10)
        
        self.actualizar_listas_cat_prov()
        self.actualizar_tabla_inv()

    def abrir_ventana_edicion(self):
        seleccion = self.tree_inv.selection()
        if not seleccion: return messagebox.showwarning("Aviso", "Por favor, selecciona un producto.")
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

        tk.Label(frame_form, text="Categoría:").grid(row=0, column=0, sticky="e", pady=5)
        var_cat_prod = tk.StringVar(value=producto.get("categoria", "Sin Categoría"))
        combo_cat_prod = ttk.Combobox(frame_form, textvariable=var_cat_prod, values=list(self.dict_categorias.keys()))
        combo_cat_prod.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Proveedor:").grid(row=1, column=0, sticky="e", pady=5)
        var_prov = tk.StringVar(value=producto.get("proveedor", ""))
        combo_prov = ttk.Combobox(frame_form, textvariable=var_prov, values=self.lista_proveedores)
        combo_prov.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Costo Compra Total:").grid(row=2, column=0, sticky="e", pady=5)
        var_costo = tk.DoubleVar(value=producto.get("precio_compra", 0))
        tk.Entry(frame_form, textvariable=var_costo).grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Precio Venta:").grid(row=3, column=0, sticky="e", pady=5)
        var_venta = tk.DoubleVar(value=producto.get("precio_venta", 0))
        tk.Entry(frame_form, textvariable=var_venta).grid(row=3, column=1, pady=5, padx=5)
        
        tk.Label(frame_form, text="Stock Total Actual:").grid(row=4, column=0, sticky="e", pady=5)
        var_stock = tk.IntVar(value=producto.get("stock", 0))
        tk.Entry(frame_form, textvariable=var_stock).grid(row=4, column=1, pady=5, padx=5)
        
        def guardar_cambios():
            cat_norm = normalizar_texto(var_cat_prod.get())
            if cat_norm and cat_norm not in self.dict_categorias: cat_norm = "Sin Categoría"
            producto["categoria"] = cat_norm
            prov_norm = normalizar_texto(var_prov.get())
            if prov_norm and prov_norm not in self.lista_proveedores:
                self.var_nuevo_prov.set(prov_norm)
                self.agregar_proveedor()
            producto["proveedor"] = prov_norm or "Sin Proveedor"
            producto["precio_compra"] = var_costo.get()
            producto["precio_venta"] = var_venta.get()
            producto["stock"] = var_stock.get()
            save_data(INV_FILE, inv)
            self.actualizar_tabla_inv()
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
                except: pass
        return f"{prefijo}-{max_num + sumador:02d}"

    def actualizar_preview_sku(self, event=None):
        cat = self.var_cat.get()
        if cat: self.var_cod.set(self.generar_proximo_sku(cat))

    def toggle_conjunto(self):
        estado = "normal" if self.var_es_conjunto.get() else "disabled"
        self.entry_uni_hijo.config(state=estado)
        self.entry_venta_hijo.config(state=estado)

    def guardar_producto(self):
        cat = self.var_cat.get()
        if not cat: return messagebox.showerror("Error", "Debes seleccionar una Categoría.")
        inv = load_data(INV_FILE)
        cod_padre = self.generar_proximo_sku(cat, sumador=1)
        cod_hijo = self.generar_proximo_sku(cat, sumador=2) if self.var_es_conjunto.get() else ""
        prov_norm = normalizar_texto(self.var_prov.get())
        if prov_norm and prov_norm not in self.lista_proveedores:
            self.var_nuevo_prov.set(prov_norm)
            self.agregar_proveedor()
        padre = {
            "codigo": cod_padre, "nombre": self.var_nom.get(), "categoria": cat, "proveedor": prov_norm or "Sin Proveedor",
            "precio_compra": self.var_costo.get(), "precio_venta": self.var_venta.get(), "stock": self.var_stock.get(),
            "hijo_codigo": cod_hijo, "hijo_unidades": self.var_uni_hijo.get() if self.var_es_conjunto.get() else 0
        }
        inv.append(padre)
        if self.var_es_conjunto.get():
            unidades = self.var_uni_hijo.get()
            if unidades > 0:
                costo_hijo = self.var_costo.get() / unidades
                hijo = {
                    "codigo": cod_hijo, "nombre": f"{self.var_nom.get()} (UNIDAD)", "categoria": cat, "proveedor": prov_norm or "Sin Proveedor",
                    "precio_compra": costo_hijo, "precio_venta": self.var_venta_hijo.get(), "stock": 0, "hijo_codigo": "", "hijo_unidades": 0
                }
                inv.append(hijo)
        save_data(INV_FILE, inv)
        self.actualizar_tabla_inv()
        self.actualizar_tabla_ventas()
        self.var_nom.set(""); self.var_stock.set(0); self.var_cod.set("(Selecciona Categoría)"); self.var_cat.set("")
        messagebox.showinfo("Éxito", "Producto(s) guardado(s).")

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
                        self.actualizar_tabla_inv()
                        self.actualizar_tabla_ventas()
                        messagebox.showinfo("Éxito", f"1 Manga desarmada. Se sumaron {padre['hijo_unidades']} al stock.")
                    else: messagebox.showerror("Error", "No queda stock.")
                else: messagebox.showerror("Error", "No se encontró el producto suelto asociado.")
            else: messagebox.showerror("Error", "Este producto no está configurado como conjunto/manga.")
        else: messagebox.showerror("Error", "Código de manga no encontrado.")

    def actualizar_tabla_inv(self):
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        inv = load_data(INV_FILE)
        filtro = self.var_filtro.get()
        for p in inv:
            if not filtro or p.get("categoria") == filtro:
                self.tree_inv.insert("", "end", values=(
                    p["codigo"], p["nombre"], p.get("categoria", ""), 
                    f"${p['precio_compra']:,.0f}", f"${p['precio_venta']:,.0f}", p["stock"], p.get("proveedor", "")
                ))

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
        self.venta_cant_var = tk.IntVar(value=1)
        tk.Entry(frame_form, textvariable=self.venta_cant_var, font=("Arial", 12)).grid(row=1, column=1, pady=10)
        tk.Button(frame_form, text="🛒 Registrar Venta", font=("Arial", 13, "bold"), bg="#dff0d8", command=self.registrar_venta).grid(row=2, column=0, columnspan=2, pady=15)
        self.actualizar_tabla_ventas()

    def actualizar_tabla_ventas(self, event=None):
        for i in self.tree_ventas.get_children(): self.tree_ventas.delete(i)
        inv = load_data(INV_FILE)
        busqueda = self.var_buscar_venta.get().lower()
        for p in inv:
            if busqueda in p["nombre"].lower() or busqueda in p["codigo"].lower():
                self.tree_ventas.insert("", "end", values=(p["codigo"], p["nombre"], f"${p['precio_venta']:,.0f}", p["stock"]))

    def filtrar_tabla_ventas(self, event): self.actualizar_tabla_ventas()

    def seleccionar_producto_venta(self, event):
        seleccion = self.tree_ventas.selection()
        if seleccion:
            valores = self.tree_ventas.item(seleccion[0])['values']
            self.venta_cod_var.set(valores[0]) 
            self.venta_cant_var.set(1)

    def registrar_venta(self):
        inv = load_data(INV_FILE)
        cod_prod = self.venta_cod_var.get().strip().upper() 
        cant = self.venta_cant_var.get()
        for p in inv:
            if p["codigo"] == cod_prod:
                if p["stock"] >= cant:
                    p["stock"] -= cant
                    save_data(INV_FILE, inv)
                    ventas = load_data(SALES_FILE)
                    ventas.append({
                        "codigo": cod_prod, "nombre": p["nombre"], "cantidad": cant,
                        "costo_total": p["precio_compra"] * cant, "venta_total": p["precio_venta"] * cant,
                        "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(SALES_FILE, ventas)
                    self.actualizar_tabla_inv()
                    self.actualizar_tabla_ventas()
                    self.actualizar_historial()
                    self.actualizar_dashboard()
                    messagebox.showinfo("Éxito", f"Vendiste {cant} x {p['nombre']}.")
                    self.venta_cod_var.set("")
                    self.venta_cant_var.set(1)
                    return
                else: return messagebox.showerror("Error", f"Solo te quedan {p['stock']} unidades.")
        messagebox.showerror("Error", "Código no encontrado")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppAdministrador(root)
    root.mainloop()
