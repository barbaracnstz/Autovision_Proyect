import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from util import validar_login
from residentes import abrir_ventana_residentes
from inicio import abrir_ventana_administrador

def abrir_ventana_inicio():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Autovision - Inicio de Sesión")

    # Obtener el tamaño de la pantalla
    ancho_ventana = root.winfo_screenwidth()
    alto_ventana = root.winfo_screenheight()
    root.geometry(f"{ancho_ventana}x{alto_ventana}+0+0")

    # Salir de pantalla completa con la tecla Esc
    def salir_pantalla_completa(event):
        root.attributes('-fullscreen', False)
    root.bind("<Escape>", salir_pantalla_completa)

    # Frame izquierdo para la imagen de fondo
    left_frame = tk.Frame(root, bg='white')
    left_frame.pack(side='left', fill='both')
    
    try:
        fondo_img = Image.open("image.png") #modificar imagen
        fondo_img = fondo_img.resize((ancho_ventana // 2, alto_ventana), Image.LANCZOS)
        fondo_photo = ImageTk.PhotoImage(fondo_img)
        
        img_label = tk.Label(left_frame, image=fondo_photo)
        img_label.image = fondo_photo
        img_label.pack(fill='both', expand=True)
    except Exception as e:
        print(f"Error al cargar la imagen: {e}")

    # Frame derecho para el formulario de inicio de sesión
    right_frame = tk.Frame(root, bg='#2897cb')
    right_frame.pack(side='right', fill='both', expand=True)

    # Icono de usuario en la parte superior
    try:
        user_icon = Image.open("user_icon.png").resize((80, 80), Image.LANCZOS)  # Cambia "user_icon.png" por el archivo del icono que quieras
        user_icon = ImageTk.PhotoImage(user_icon)
        icon_label = tk.Label(right_frame, image=user_icon, bg='#2e11bf')
        icon_label.image = user_icon
        icon_label.place(relx=0.5, rely=0.2, anchor='center')
    except Exception as e:
        print(f"Error al cargar el icono: {e}")

    # Título de inicio de sesión
    inicio_label = tk.Label(right_frame, text="Inicio de Sesión", font=('Helvetica', 24, 'bold'), bg='#2897cb', fg='white')
    inicio_label.place(relx=0.5, rely=0.3, anchor='center')

    # Campo de entrada para usuario con icono
    usuario_frame = tk.Frame(right_frame, bg='#2897cb')
    usuario_frame.place(relx=0.5, rely=0.4, anchor='center')

    usuario_icon = tk.Label(usuario_frame, text="👤", bg='#2897cb', fg='white', font=('Arial', 14))
    usuario_icon.pack(side='left')
    
    usuario_entry = tk.Entry(usuario_frame, font=('Arial', 14), width=20, bd=0, fg='black', insertbackground='black', bg='white')
    usuario_entry.pack(side='left', fill='x')

    # Mensaje de error debajo del campo de usuario
    usuario_error = tk.Label(right_frame, text="", bg='#2897cb', fg='white', font=('Arial', 10))
    usuario_error.place(relx=0.5, rely=0.45, anchor='center')

    # Campo de entrada para contraseña con icono
    password_frame = tk.Frame(right_frame, bg='#2897cb')
    password_frame.place(relx=0.5, rely=0.5, anchor='center')

    password_icon = tk.Label(password_frame, text="🔒", bg='#2897cb', fg='white', font=('Arial', 14))
    password_icon.pack(side='left')

    password_entry = tk.Entry(password_frame, font=('Arial', 14), show='*', width=20, bd=0,  fg='black', insertbackground='black', bg='white')
    password_entry.pack(side='left', fill='x')

    # Mensaje de error debajo del campo de contraseña
    password_error = tk.Label(right_frame, text="", bg='#2897cb', fg='white', font=('Arial', 10))
    password_error.place(relx=0.5, rely=0.55, anchor='center')

    # Botón de inicio de sesión
    login_button = tk.Button(right_frame, text="Iniciar Sesión", font=('Arial', 14, 'bold'), bg='#097abd', fg='white', activebackground='black', activeforeground='white', padx=10, pady=5, bd=0, command=lambda: iniciar_sesion(usuario_entry, password_entry))
    login_button.place(relx=0.5, rely=0.6, anchor='center')

    # Enlace de "Forgot Password?"
    olvide_password_label = tk.Label(right_frame, text="Olvidaste tu contraseña?", bg='#2897cb', fg='white', font=('Arial', 10, 'underline'))
    olvide_password_label.place(relx=0.5, rely=0.7, anchor='center')

    # Validación de inicio de sesión
    def iniciar_sesion(usuario_entry, password_entry):
        usuario = usuario_entry.get().strip()
        contrasena = password_entry.get().strip()

        # Limpiar mensajes de error
        usuario_error.config(text="")
        password_error.config(text="")

        # Validaciones
        if not usuario and not contrasena:
            usuario_error.config(text="DEBE INGRESAR USUARIO")
            password_error.config(text="DEBE INGRESAR CONTRASEÑA")
        elif not usuario:
            usuario_error.config(text="DEBE INGRESAR USUARIO")
        elif not contrasena:
            password_error.config(text="DEBE INGRESAR CONTRASEÑA")
        else:
            if validar_login(usuario, contrasena):
                messagebox.showinfo("Éxito", "Inicio de sesión correcto")
                root.withdraw()
                abrir_ventana_administrador()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    # Ejecutar la aplicación solo si este archivo es el principal
    if __name__ == "__main__":
        root.mainloop()
