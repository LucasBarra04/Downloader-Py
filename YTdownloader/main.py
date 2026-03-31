import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pytubefix import YouTube
from PIL import Image, ImageTk
import requests
from io import BytesIO

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue") 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Baixador de Vídeos Pro")
        self.geometry("800x650")
        self.grid_columnconfigure(0, weight=1)

        self.yt = None
        self.stream_download = None 
        self.thumbnail_tk = None

        self.label_titulo = ctk.CTkLabel(self, text="Cole o Link do YouTube", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=(30, 10))
        self.entrada_url = ctk.CTkEntry(self, width=600, height=40, placeholder_text="Ex: https://www.youtube.com/watch?v=...")
        self.entrada_url.pack(pady=10)

        self.botao_buscar = ctk.CTkButton(self, text="Buscar Informações", command=self.iniciar_busca, font=("Arial", 14, "bold"), height=40)
        self.botao_buscar.pack(pady=(10, 20))

        self.frame_info = ctk.CTkFrame(self, fg_color="transparent")
    
        self.label_thumbnail = ctk.CTkLabel(self.frame_info, text="")
        self.label_thumbnail.pack(pady=10)

        self.label_dados = ctk.CTkLabel(self.frame_info, text="", font=("Arial", 14), justify="center")
        self.label_dados.pack(pady=5)

        self.botao_baixar = ctk.CTkButton(self.frame_info, text="Escolher Pasta e Baixar", command=self.iniciar_download, font=("Arial", 14, "bold"), height=40, fg_color="#ff0000", hover_color="#cc0000")
        self.botao_baixar.pack(pady=(15, 10))
        
        self.label_status = ctk.CTkLabel(self.frame_info, text="", font=("Arial", 12))
        self.label_status.pack()

    def iniciar_busca(self):
        url = self.entrada_url.get()
        if not url:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL válida.")
            return

        self.label_dados.configure(text="")
        self.label_thumbnail.configure(image=None)
        self.label_status.configure(text="", fg_color="transparent")
        self.frame_info.pack(fill="x", padx=50)
        self.botao_baixar.configure(state="disabled")

        self.label_status.configure(text="Buscando thumbnail e informações...", text_color="cyan")
        
        thread_busca = threading.Thread(target=self.buscar_dados_video, args=(url,))
        thread_busca.start()

    def buscar_dados_video(self, url):
        try:
            self.yt = YouTube(url)
            
            resposta = requests.get(self.yt.thumbnail_url)
            imagem_data = BytesIO(resposta.content)
            imagem_pil = Image.open(imagem_data)
            
            proporcao = 480 / imagem_pil.width
            nova_altura = int(imagem_pil.height * proporcao)
            imagem_pil_redimensionada = imagem_pil.resize((480, nova_altura), Image.Resampling.LANCZOS)
            
            self.thumbnail_tk = ImageTk.PhotoImage(imagem_pil_redimensionada)

            self.label_thumbnail.configure(image=self.thumbnail_tk)
            dados_texto = f"Título: {self.yt.title}\nAutor: {self.yt.author}"
            self.label_dados.configure(text=dados_texto)
            self.label_status.configure(text="Pronto para baixar!", text_color="green")
            
            self.stream_download = self.yt.streams.get_highest_resolution()
            self.botao_baixar.configure(state="normal")

        except Exception as e:
            self.label_status.configure(text="❌ Erro ao buscar dados do vídeo.", text_color="red")
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o vídeo:\n{str(e)}")
            self.frame_info.pack_forget()

    def iniciar_download(self):
        pasta_destino = filedialog.askdirectory(title="Escolha onde salvar o vídeo")
        
        if not pasta_destino:
            return

        if self.stream_download:
            self.label_status.configure(text="Iniciando download... Aguarde.", text_color="orange")
            self.botao_baixar.configure(state="disabled")
            
            # Thread para o download pesado
            thread_download = threading.Thread(target=self.fazer_download, args=(pasta_destino,))
            thread_download.start()

    def fazer_download(self, pasta_destino):
        try:
            self.stream_download.download(output_path=pasta_destino)
            self.label_status.configure(text=f"✅ Download concluído com sucesso!", text_color="green")
            messagebox.showinfo("Sucesso", f"O vídeo foi salvo em:\n{pasta_destino}")
            
        except Exception as e:
            self.label_status.configure(text="❌ Erro durante o download.", text_color="red")
            messagebox.showerror("Erro", f"Ocorreu um erro durante o download:\n{str(e)}")
            
        finally:
            self.botao_baixar.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.eval('tk::PlaceWindow . center')
    app.mainloop()