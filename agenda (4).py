import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import pandas as pd

class Agenda:
    def __init__(self, archivo="eventos.json"):
        self.archivo = archivo
        self.eventos = self.cargar_eventos()
    
    def cargar_eventos(self):
        """Carga los eventos desde el archivo JSON"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def guardar_eventos(self):
        """Guarda los eventos en el archivo JSON"""
        with open(self.archivo, 'w', encoding='utf-8') as f:
            json.dump(self.eventos, f, indent=4, ensure_ascii=False)

    def exportar_eventos_csv(self, archivo_csv="eventos.csv"):
        """Exporta eventos guardados a CSV usando pandas"""
        if not self.eventos:
            return False, "No hay eventos para exportar."
        df = pd.DataFrame(self.eventos)
        df.to_csv(archivo_csv, index=False, encoding='utf-8')
        return True, f"Eventos exportados a {archivo_csv}."

    def importar_eventos_csv(self, archivo_csv="eventos.csv"):
        """Importa eventos desde CSV y los guarda en JSON"""
        if not os.path.exists(archivo_csv):
            return False, f"No se encontró el archivo {archivo_csv}."
        try:
            df = pd.read_csv(archivo_csv, encoding='utf-8')
            eventos_nuevos = []
            max_id = max([e["id"] for e in self.eventos], default=0)
            for idx, row in df.iterrows():
                max_id += 1
                evento = {
                    "id": int(row.get("id", max_id)),
                    "fecha": str(row.get("fecha", "")),
                    "titulo": str(row.get("titulo", "Evento")),
                    "descripcion": str(row.get("descripcion", "")),
                    "completado": bool(row.get("completado", False))
                }
                if not evento["fecha"]:
                    continue
                eventos_nuevos.append(evento)
            if eventos_nuevos:
                self.eventos.extend(eventos_nuevos)
                self.guardar_eventos()
                return True, f"Importados {len(eventos_nuevos)} eventos desde {archivo_csv}."
            return False, "No se importaron eventos desde el archivo CSV."
        except Exception as e:
            return False, f"Error al importar CSV: {e}"

    def agregar_evento(self, fecha, titulo, descripcion=""):
        """Agrega un nuevo evento"""
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            
            evento = {
                "id": max([e["id"] for e in self.eventos], default=0) + 1,
                "fecha": fecha,
                "titulo": titulo,
                "descripcion": descripcion,
                "completado": False
            }
            self.eventos.append(evento)
            self.guardar_eventos()
            return True, f"Evento '{titulo}' agregado para el {fecha}"
        except ValueError:
            return False, "Formato de fecha inválido. Use: YYYY-MM-DD"
    
    def obtener_todos_eventos(self):
        """Retorna todos los eventos ordenados por fecha"""
        return sorted(self.eventos, key=lambda x: x["fecha"])
    
    def eliminar_evento(self, evento_id):
        """Elimina un evento por su ID"""
        for evento in self.eventos:
            if evento["id"] == evento_id:
                titulo = evento["titulo"]
                self.eventos.remove(evento)
                self.guardar_eventos()
                return True, f"Evento '{titulo}' eliminado"
        return False, f"No se encontró un evento con ID {evento_id}"
    
    def marcar_completado(self, evento_id):
        """Marca un evento como completado"""
        for evento in self.eventos:
            if evento["id"] == evento_id:
                evento["completado"] = not evento["completado"]
                self.guardar_eventos()
                estado = "completado" if evento["completado"] else "pendiente"
                return True, f"Evento '{evento['titulo']}' marcado como {estado}"
        return False, f"No se encontró un evento con ID {evento_id}"
    
    def buscar_evento(self, palabra_clave):
        """Busca eventos por palabra clave"""
        return [e for e in self.eventos 
                if palabra_clave.lower() in e["titulo"].lower() 
                or palabra_clave.lower() in e["descripcion"].lower()]


class AgendaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Agenda")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.agenda = Agenda()
        
        self.crear_interfaz()
        self.actualizar_lista()
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        # Frame superior - Agregar evento
        frame_agregar = ttk.LabelFrame(self.root, text="Agregar Evento", padding=10)
        frame_agregar.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame_agregar, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5)
        self.entrada_fecha = ttk.Entry(frame_agregar, width=20)
        self.entrada_fecha.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_agregar, text="Título:").grid(row=0, column=2, sticky="w", padx=5)
        self.entrada_titulo = ttk.Entry(frame_agregar, width=25)
        self.entrada_titulo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(frame_agregar, text="➕ Agregar", command=self.agregar_evento).grid(row=0, column=4, padx=5)
        
        ttk.Label(frame_agregar, text="Descripción:").grid(row=1, column=0, sticky="w", padx=5)
        self.entrada_descripcion = ttk.Entry(frame_agregar, width=60)
        self.entrada_descripcion.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Frame búsqueda
        frame_busqueda = ttk.Frame(self.root)
        frame_busqueda.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_busqueda, text="Buscar:").pack(side="left", padx=5)
        self.entrada_busqueda = ttk.Entry(frame_busqueda, width=30)
        self.entrada_busqueda.pack(side="left", padx=5)
        self.entrada_busqueda.bind("<KeyRelease>", lambda e: self.buscar_eventos())
        
        ttk.Button(frame_busqueda, text="🔄 Actualizar", command=self.actualizar_lista).pack(side="left", padx=5)
        
        # Frame lista de eventos
        frame_lista = ttk.LabelFrame(self.root, text="Eventos", padding=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        self.tree = ttk.Treeview(frame_lista, columns=("ID", "Fecha", "Título", "Descripción", "Estado"), 
                                  yscrollcommand=scrollbar.set, height=15)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("#0", text="")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("ID", width=30)
        self.tree.column("Fecha", width=100)
        self.tree.column("Título", width=150)
        self.tree.column("Descripción", width=250)
        self.tree.column("Estado", width=100)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_evento_doble_click)
        
        # Frame botones
        frame_botones = ttk.Frame(self.root)
        frame_botones.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(frame_botones, text="✓ Completar", command=self.completar_evento).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="🗑️ Eliminar", command=self.eliminar_evento).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="📤 Exportar CSV", command=self.exportar_csv).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="📥 Importar CSV", command=self.importar_csv).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="❌ Salir", command=self.root.quit).pack(side="right", padx=5)
    
    def agregar_evento(self):
        """Agrega un nuevo evento"""
        fecha = self.entrada_fecha.get().strip()
        titulo = self.entrada_titulo.get().strip()
        descripcion = self.entrada_descripcion.get().strip()
        
        if not fecha or not titulo:
            messagebox.showwarning("Validación", "Por favor ingrese fecha y título")
            return
        
        exito, mensaje = self.agenda.agregar_evento(fecha, titulo, descripcion)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.entrada_fecha.delete(0, "end")
            self.entrada_titulo.delete(0, "end")
            self.entrada_descripcion.delete(0, "end")
            self.actualizar_lista()
        else:
            messagebox.showerror("Error", mensaje)
    
    def actualizar_lista(self):
        """Actualiza la lista de eventos"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar eventos
        eventos = self.agenda.obtener_todos_eventos()
        for evento in eventos:
            estado = "✓ Completado" if evento["completado"] else "⏳ Pendiente"
            self.tree.insert("", "end", 
                           values=(evento["id"], evento["fecha"], evento["titulo"], 
                                  evento["descripcion"], estado))
    
    def buscar_eventos(self):
        """Busca eventos por palabra clave"""
        palabra = self.entrada_busqueda.get().strip()
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if palabra:
            eventos = self.agenda.buscar_evento(palabra)
        else:
            eventos = self.agenda.obtener_todos_eventos()
        
        for evento in eventos:
            estado = "✓ Completado" if evento["completado"] else "⏳ Pendiente"
            self.tree.insert("", "end",
                           values=(evento["id"], evento["fecha"], evento["titulo"],
                                  evento["descripcion"], estado))
    
    def on_evento_doble_click(self, event):
        """Maneja el doble click en un evento"""
        selection = self.tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.tree.item(item, "values")
        evento_id = int(values[0])
        self.completar_evento(evento_id)
    
    def completar_evento(self, evento_id=None):
        """Marca un evento como completado"""
        if evento_id is None:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Validación", "Seleccione un evento")
                return
            values = self.tree.item(selection[0], "values")
            evento_id = int(values[0])
        
        exito, mensaje = self.agenda.marcar_completado(evento_id)
        
        if exito:
            self.actualizar_lista()
        else:
            messagebox.showerror("Error", mensaje)
    
    def eliminar_evento(self):
        """Elimina un evento"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Validación", "Seleccione un evento")
            return
        
        values = self.tree.item(selection[0], "values")
        evento_id = int(values[0])
        
        if messagebox.askyesno("Confirmación", "¿Está seguro de eliminar este evento?"):
            exito, mensaje = self.agenda.eliminar_evento(evento_id)
            
            if exito:
                self.actualizar_lista()
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)

    def exportar_csv(self):
        """Exporta eventos a CSV"""
        exito, mensaje = self.agenda.exportar_eventos_csv()
        if exito:
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showwarning("Aviso", mensaje)

    def importar_csv(self):
        """Importa eventos desde CSV"""
        exito, mensaje = self.agenda.importar_eventos_csv()
        if exito:
            self.actualizar_lista()
            messagebox.showinfo("Éxito", mensaje)
        else:
            messagebox.showerror("Error", mensaje)


if __name__ == "__main__":
    root = tk.Tk()
    app = AgendaGUI(root)
    root.mainloop()
