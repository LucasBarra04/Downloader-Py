import tkinter as tk
from tkinter import messagebox, filedialog
import threading
from pytubefix import YouTube

def iniciar_download():
    url = entrada_url.get()
    
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira uma URL válida.")
        return

    pasta_destino = filedialog.askdirectory(title="Escolha onde salvar o vídeo")
    
    if not pasta_destino:
        return 
    
    label_status.config(text="Buscando informações do vídeo...", fg="blue")
    botao_baixar.config(state=tk.DISABLED)

    thread = threading.Thread(target=baixar_video, args=(url, pasta_destino))
    thread.start()

def baixar_video(url, pasta_destino):
    try:
        yt = YouTube(url)
        info = f"Título: {yt.title}\nAutor: {yt.author}"
        label_status.config(text=f"{info}\n\nBaixando vídeo... Aguarde.", fg="orange")
        
        ys = yt.streams.get_highest_resolution()
        
        ys.download(output_path=pasta_destino) 
        
        label_status.config(text=f"{info}\n\n✅ Salvo em:\n{pasta_destino}", fg="green")
        
    except Exception as e:
        label_status.config(text="❌ Erro durante o download.", fg="red")
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")
        
    finally:
        botao_baixar.config(state=tk.NORMAL)

janela = tk.Tk()
janela.title("Baixador de Vídeos do YouTube")
janela.geometry("450x250")
janela.eval('tk::PlaceWindow . center')

label_titulo = tk.Label(janela, text="Cole o link do YouTube abaixo:", font=("Arial", 12))
label_titulo.pack(pady=(20, 5))

entrada_url = tk.Entry(janela, width=50, font=("Arial", 10))
entrada_url.pack(pady=5)

botao_baixar = tk.Button(janela, text="Baixar Vídeo", command=iniciar_download, font=("Arial", 10, "bold"), bg="#ff0000", fg="white")
botao_baixar.pack(pady=10)

label_status = tk.Label(janela, text="", font=("Arial", 10), justify="center")
label_status.pack(pady=10)

janela.mainloop()