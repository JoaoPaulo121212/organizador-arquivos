import os
import shutil
import time
import threading
from pathlib import Path
import customtkinter as ctk # type: ignore
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore

ctk.set_appearance_mode("Dark")  # Modo escuro
ctk.set_default_color_theme("blue")

class OrganizadorHandler(FileSystemEventHandler):
    def __init__(self, callback_log):
        self.callback_log = callback_log
        
        # Mapeamento: Pasta -> Extensões
        self.regras = {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".heic"],
            "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
            "Instaladores": [".dmg", ".pkg", ".zip", ".rar", ".iso"],
            "Codigos": [".py", ".js", ".html", ".css", ".json", ".java"]
        }

    def on_created(self, event):
        # Ignora se for pasta ou arquivo temporário (.ds_store, .crdownload)
        if event.is_directory or ".crdownload" in event.src_path or ".DS_Store" in event.src_path:
            return

        self.organizar_arquivo(event.src_path)

    def organizar_arquivo(self, caminho_arquivo):
        time.sleep(1) # Espera para garantir que o download terminou
        
        path = Path(caminho_arquivo)
        extensao = path.suffix.lower()
        nome_arquivo = path.name
        pasta_downloads = path.parent

        moved = False
        
        for pasta, extensoes in self.regras.items():
            if extensao in extensoes:
                destino = pasta_downloads / pasta
                destino.mkdir(exist_ok=True) # Cria a pasta se não existir
                
                destino_final = destino / nome_arquivo
                
                # Evita sobrescrever arquivos com mesmo nome
                if destino_final.exists():
                    timestamp = int(time.time())
                    destino_final = destino / f"{path.stem}_{timestamp}{path.suffix}"

                try:
                    shutil.move(caminho_arquivo, destino_final)
                    self.callback_log(f"✅ Movido: {nome_arquivo} -> 📂 {pasta}")
                    moved = True
                except Exception as e:
                    self.callback_log(f"❌ Erro ao mover {nome_arquivo}: {e}")
                break
        
        if not moved:
            self.callback_log(f"ℹ️ Ignorado: {nome_arquivo} (Sem regra definida)")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mac Organizer AI")
        self.geometry("600x450")
        
        self.download_folder = str(Path.home() / "Downloads")
        self.observer = None
        self.running = False

        self.criar_interface()

    def criar_interface(self):
        # Título
        self.label_titulo = ctk.CTkLabel(self, text="Organizador de Downloads", font=("Arial", 20, "bold"))
        self.label_titulo.pack(pady=20)

        # Status
        self.label_status = ctk.CTkLabel(self, text="Status: Parado", text_color="red")
        self.label_status.pack(pady=5)

        # Botão Iniciar/Parar
        self.btn_toggle = ctk.CTkButton(self, text="INICIAR MONITORAMENTO", command=self.toggle_monitoramento, height=40, fg_color="green", hover_color="darkgreen")
        self.btn_toggle.pack(pady=20, padx=50, fill="x")

        # Área de Logs (Scrollable)
        self.textbox_log = ctk.CTkTextbox(self, width=500, height=200)
        self.textbox_log.pack(pady=10)
        self.textbox_log.insert("0.0", "--- Logs do Sistema ---\n")
        self.textbox_log.configure(state="disabled") # Bloqueia edição manual

        # Rodapé
        self.label_footer = ctk.CTkLabel(self, text=f"Monitorando: {self.download_folder}", text_color="gray")
        self.label_footer.pack(side="bottom", pady=10)

    def log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end") 
        self.textbox_log.configure(state="disabled")

    def start_monitoring(self):
        event_handler = OrganizadorHandler(self.log)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.download_folder, recursive=False)
        self.observer.start()
        self.log(f"Monitoramento iniciado em: {self.download_folder}")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.log("Monitoramento paralisado.")

    def toggle_monitoramento(self):
        if not self.running:
            # INICIAR
            self.running = True
            self.btn_toggle.configure(text="PARAR MONITORAMENTO", fg_color="red", hover_color="darkred")
            self.label_status.configure(text="Status: Rodando", text_color="#00FF00")
            
            threading.Thread(target=self.start_monitoring, daemon=True).start()
        else:
            # PARAR
            self.running = False
            self.btn_toggle.configure(text="INICIAR MONITORAMENTO", fg_color="green", hover_color="darkgreen")
            self.label_status.configure(text="Status: Parado", text_color="red")
            self.stop_monitoring()

if __name__ == "__main__":
    app = App()
    app.mainloop()