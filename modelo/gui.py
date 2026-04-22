import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading

from model_logic import Model

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Enfermedades en Caña de Azúcar")
        self.root.geometry("1000x600") 
        self.root.resizable(True, True)
        
        self.ai_model = Model()
        
        self.image_path = None
        self.current_photo = None
        
        self.setup_styles()
        self.create_widgets()
        self.load_model_on_startup()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        bg_color = "#f0f0f0"
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color)
        style.configure('Header.TLabel', background=bg_color, font=('Arial', 14, 'bold'))
        style.configure('Info.TLabel', background=bg_color, font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header_frame, text="🌾 Detector de Enfermedades en Caña de Azúcar", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Carga una imagen de una hoja para identificar enfermedades", style='Info.TLabel').pack(anchor=tk.W)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_column = ttk.Frame(content_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        image_frame = ttk.LabelFrame(left_column, text="Imagen de la Hoja", padding=10)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        self.image_canvas = tk.Canvas(image_frame, bg='white', height=350, cursor="hand2")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        self.image_canvas.create_text(200, 175, text="Haz clic o arrastra una imagen aquí", fill="gray", font=("Arial", 12))
        self.image_canvas.bind("<Button-1>", self.on_canvas_click)
        
        button_frame = ttk.Frame(image_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.browse_button = ttk.Button(button_frame, text="📁 Seleccionar", command=self.browse_image)
        self.browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.analyze_button = ttk.Button(button_frame, text="🔍 Analizar", command=self.analyze_image)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Limpiar", command=self.clear_image)
        self.clear_button.pack(side=tk.LEFT)
        
        status_frame = ttk.LabelFrame(right_column, text="Estado del Modelo", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        self.status_label = ttk.Label(status_frame, text="⏳ Cargando modelo...", style='Info.TLabel')
        self.status_label.pack(anchor=tk.W)
        self.status_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
        
        results_frame = ttk.LabelFrame(right_column, text="Resultados del Análisis", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        diagnosis_frame = ttk.Frame(results_frame)
        diagnosis_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(diagnosis_frame, text="Diagnóstico Principal:", style='Info.TLabel').pack(anchor=tk.W)
        self.diagnosis_label = ttk.Label(diagnosis_frame, text="Sin analizar", font=('Arial', 14, 'bold'), foreground="#2ecc71")
        self.diagnosis_label.pack(anchor=tk.W, padx=(10, 0), pady=(5, 0))
        
        confidence_frame = ttk.Frame(results_frame)
        confidence_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(confidence_frame, text="Confianza de la IA:", style='Info.TLabel').pack(anchor=tk.W)
        self.confidence_bar = ttk.Progressbar(confidence_frame, mode='determinate', maximum=100)
        self.confidence_bar.pack(fill=tk.X, padx=(10, 0), pady=(5, 0))
        self.confidence_label = ttk.Label(confidence_frame, text="0%", style='Info.TLabel')
        self.confidence_label.pack(anchor=tk.W, padx=(10, 0))
        
        table_frame = ttk.Frame(results_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(table_frame, text="Desglose de Probabilidades:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.tree = ttk.Treeview(table_frame, columns=('Clase', 'Probabilidad'), show='headings')
        self.tree.column('Clase', width=150)
        self.tree.column('Probabilidad', width=100)
        self.tree.heading('Clase', text='Clase')
        self.tree.heading('Probabilidad', text='Probabilidad')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def load_model_on_startup(self):
        thread = threading.Thread(target=self._load_model_thread, daemon=True)
        thread.start()
    
    def _load_model_thread(self):
        try:
            self.status_bar.start()
            self.status_label.config(text="⏳ Cargando modelo keras_model.h5...")
            self.root.update()
            
            self.ai_model.load()
            
            self.status_bar.stop()
            self.status_label.config(text="✅ Modelo cargado y listo")
            self.browse_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.status_bar.stop()
            self.status_label.config(text="❌ Error al cargar el modelo")
            messagebox.showerror("Error", f"No se pudo cargar el modelo:\n{str(e)}")
    
    def on_canvas_click(self, event):
        self.browse_image()
    
    def browse_image(self):
        if not self.ai_model.is_loaded:
            messagebox.showwarning("Espera", "El modelo aún se está cargando...")
            return
        
        file_path = filedialog.askopenfilename(
            title="Selecciona una imagen de hoja de caña",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.analyze_image()
    
    def display_image(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")
            image.thumbnail((500, 400), Image.Resampling.LANCZOS)
            self.current_photo = ImageTk.PhotoImage(image)
            
            self.image_canvas.delete("all")
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1: canvas_width = 450
            if canvas_height <= 1: canvas_height = 350
                
            self.image_canvas.create_image(canvas_width//2, canvas_height//2, image=self.current_photo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
    
    def clear_image(self):
        self.image_canvas.delete("all")
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        self.image_canvas.create_text(canvas_width//2, canvas_height//2, text="Haz clic o arrastra una imagen aquí", fill="gray", font=("Arial", 12))
        self.image_path = None
        self.diagnosis_label.config(text="Sin analizar")
        self.confidence_bar.config(value=0)
        self.confidence_label.config(text="0%")
        self.tree.delete(*self.tree.get_children())
    
    def analyze_image(self):
        if not self.ai_model.is_loaded:
            messagebox.showwarning("Espera", "El modelo aún se está cargando...")
            return
        if not self.image_path:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una imagen primero")
            return
            
        thread = threading.Thread(target=self._analyze_image_thread, daemon=True)
        thread.start()
    
    def _analyze_image_thread(self):
        try:
            self.analyze_button.config(state=tk.DISABLED)
            self.browse_button.config(state=tk.DISABLED)
            
            class_name, confidence_score, predictions_list = self.ai_model.predict(self.image_path)
            
            self.diagnosis_label.config(text=class_name)
            self.confidence_bar.config(value=confidence_score * 100)
            self.confidence_label.config(text=f"{confidence_score * 100:.2f}%")
            
            self.tree.delete(*self.tree.get_children())
            for class_display, prob in predictions_list:
                self.tree.insert('', tk.END, values=(class_display, f"{prob * 100:.2f}%"))
            
            self.browse_button.config(state=tk.NORMAL)
            self.analyze_button.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis:\n{str(e)}")
            self.browse_button.config(state=tk.NORMAL)
            self.analyze_button.config(state=tk.NORMAL)