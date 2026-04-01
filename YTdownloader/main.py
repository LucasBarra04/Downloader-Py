import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import requests
from io import BytesIO
from PIL import Image
from pytubefix import YouTube
import os
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Youtube Downloader")
        self.geometry("750x450")
        self.resizable(False, False)
        
        self.yt = None
        self.imagem_tk = None

        self.construir_interface()

    def construir_interface(self):
        self.frame_busca = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busca.pack(pady=(30, 20), padx=20, fill="x")

        self.entrada_url = ctk.CTkEntry(
            self.frame_busca, 
            placeholder_text="Cole o link do vídeo aqui...", 
            width=500, 
            height=45, 
            font=("Segoe UI", 14)
        )
        self.entrada_url.pack(side="left", padx=(0, 10))

        self.botao_buscar = ctk.CTkButton(
            self.frame_busca, 
            text="Buscar", 
            command=self.iniciar_busca, 
            width=120, 
            height=45, 
            font=("Segoe UI", 14, "bold")
        )
        self.botao_buscar.pack(side="left")

        self.frame_card = ctk.CTkFrame(self, corner_radius=15)
        
        self.frame_card.grid_columnconfigure(0, weight=0)
        self.frame_card.grid_columnconfigure(1, weight=1)
        
        self.label_thumb = ctk.CTkLabel(self.frame_card, text="", corner_radius=10)
        self.label_thumb.grid(row=0, column=0, rowspan=6, padx=20, pady=20)

        self.label_titulo = ctk.CTkLabel(
            self.frame_card, 
            text="", 
            font=("Segoe UI", 16, "bold"), 
            wraplength=300, 
            justify="left",
            anchor="w"
        )
        self.label_titulo.grid(row=0, column=1, sticky="nw", pady=(20, 0), padx=(0, 20))

        self.label_autor = ctk.CTkLabel(
            self.frame_card, 
            text="", 
            font=("Segoe UI", 13), 
            text_color="gray70",
            anchor="w"
        )
        self.label_autor.grid(row=1, column=1, sticky="nw", pady=(0, 15), padx=(0, 20))

        self.frame_progresso = ctk.CTkFrame(self.frame_card, fg_color="transparent")
        
        self.barra_progresso = ctk.CTkProgressBar(self.frame_progresso, width=250, height=10)
        self.barra_progresso.set(0)
        self.barra_progresso.pack(side="left", pady=5)
        
        self.label_porcentagem = ctk.CTkLabel(self.frame_progresso, text="0%", font=("Segoe UI", 12))
        self.label_porcentagem.pack(side="left", padx=10)

        self.label_status = ctk.CTkLabel(self.frame_card, text="", font=("Segoe UI", 12))
        self.label_status.grid(row=3, column=1, sticky="sw", padx=(0, 20))

        self.frame_controles = ctk.CTkFrame(self.frame_card, fg_color="transparent")
        self.frame_controles.grid(row=4, column=1, sticky="sw", pady=(0, 20), padx=(0, 20))

        self.combo_resolucao = ctk.CTkOptionMenu(
            self.frame_controles,
            values=["Buscando..."],
            width=100,
            height=40,
            font=("Segoe UI", 13)
        )
        self.combo_resolucao.pack(side="left", padx=(0, 10))

        self.botao_baixar = ctk.CTkButton(
            self.frame_controles, 
            text="Baixar Vídeo", 
            command=self.iniciar_download, 
            fg_color="#E50914",
            hover_color="#B80710",
            height=40,
            font=("Segoe UI", 14, "bold")
        )
        self.botao_baixar.pack(side="left")

    def iniciar_busca(self):
        url = self.entrada_url.get()
        if not url:
            return

        self.botao_buscar.configure(state="disabled")
        self.frame_card.pack_forget()
        
        threading.Thread(target=self.processar_busca, args=(url,)).start()

    def processar_busca(self, url):
        try:
            self.yt = YouTube(url, on_progress_callback=self.atualizar_progresso)
            
            resposta = requests.get(self.yt.thumbnail_url)
            img_data = Image.open(BytesIO(resposta.content))
            
            img_data = img_data.resize((280, 157), Image.Resampling.LANCZOS)
            self.imagem_tk = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(280, 157))
            
            self.label_thumb.configure(image=self.imagem_tk)
            self.label_titulo.configure(text=self.yt.title)
            self.label_autor.configure(text=self.yt.author)
            
            streams = self.yt.streams.filter(type="video")
            resolucoes = list(set([s.resolution for s in streams if s.resolution]))
            resolucoes.sort(key=lambda x: int(x.replace("p", "")), reverse=True)
            
            if not resolucoes:
                resolucoes = ["Padrão"]

            self.combo_resolucao.configure(values=resolucoes)
            self.combo_resolucao.set(resolucoes[0])
            
            self.barra_progresso.set(0)
            self.label_porcentagem.configure(text="0%")
            self.frame_progresso.grid_forget()
            
            self.label_status.configure(text="Pronto para baixar.", text_color="gray70")
            self.botao_baixar.configure(state="normal", text="Baixar Vídeo", fg_color="#E50914")

            self.frame_card.pack(pady=10, padx=20, fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Erro", "Não foi possível carregar o vídeo. Verifique o link.")
        finally:
            self.botao_buscar.configure(state="normal")

    def iniciar_download(self):
        pasta = filedialog.askdirectory()
        if not pasta:
            return

        self.botao_baixar.configure(state="disabled")
        self.combo_resolucao.configure(state="disabled")
        self.frame_progresso.grid(row=2, column=1, sticky="w", pady=(10, 5), padx=(0, 20))
        self.label_status.configure(text="Baixando...", text_color="#E50914")

        threading.Thread(target=self.processar_download, args=(pasta,)).start()

    def processar_download(self, pasta):
        try:
            res_escolhida = self.combo_resolucao.get()
            
            if res_escolhida == "Padrão":
                stream = self.yt.streams.get_highest_resolution()
                stream.download(output_path=pasta)
            else:
                stream_video = self.yt.streams.filter(res=res_escolhida, type="video").first()
                
                if stream_video.is_progressive:
                    stream_video.download(output_path=pasta)
                else:
                    self.label_status.configure(text="Baixando vídeo e áudio...", text_color="#E50914")
                    stream_audio = self.yt.streams.get_audio_only()
                    
                    video_path = stream_video.download(output_path=pasta, filename="temp_video.mp4")
                    audio_path = stream_audio.download(output_path=pasta, filename="temp_audio.mp4")
                    
                    self.label_status.configure(text="Processando 1080p (Pode demorar)...", text_color="orange")
                    
                    nome_seguro = "".join([c for c in self.yt.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    caminho_final = os.path.join(pasta, f"{nome_seguro}.mp4")
                    
                    comando = f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{caminho_final}"'
                    subprocess.run(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    if os.path.exists(caminho_final):
                        os.remove(video_path)
                        os.remove(audio_path)
                    else:
                        raise Exception("FFmpeg não encontrado. Instale o FFmpeg para baixar em 1080p.")

            self.label_status.configure(text="✅ Download Completo!", text_color="#28a745")
            self.botao_baixar.configure(text="Sucesso!", fg_color="#28a745")
            
        except Exception as e:
            self.label_status.configure(text="❌ Erro no download.", text_color="red")
            messagebox.showerror("Erro", str(e))
        finally:
            self.botao_baixar.configure(state="normal")
            self.combo_resolucao.configure(state="normal")

    def atualizar_progresso(self, stream, chunk, bytes_remaining):
        tamanho_total = stream.filesize
        bytes_baixados = tamanho_total - bytes_remaining
        porcentagem = bytes_baixados / tamanho_total
        
        self.barra_progresso.set(porcentagem)
        self.label_porcentagem.configure(text=f"{int(porcentagem * 100)}%")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()