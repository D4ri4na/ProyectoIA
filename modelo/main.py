import tkinter as tk
from gui import GUI

def main():
    """
    Punto de entrada de la aplicación.
    Inicializa la ventana principal y arranca el programa.
    """
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()