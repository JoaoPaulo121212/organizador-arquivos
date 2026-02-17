import os
import shutil
import time
import threading
import sys
from pathlib import Path
import customtkinter as ctk #type: ignore
from watchdog.observers import Observer #type: ignore
from watchdog.events import FileSystemEventHandler #type: ignore
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AutoStartHandler:
    def __init__(self):
        self.launch_agents_dir = Path.home() / "Library/LaunchAgents"
        self.plist_name = "com.usuario.macorganizer.plist"
        self.plist_path = self.launch_agents_dir / self.plist_name
        self.python_exe = sys.executable
        self.script_path = str(Path(__file__).resolve())

    def is_enabled(self):
        return self.plist_path.exists()

    def enable(self):
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.usuario.macorganizer</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.python_exe}</string>
        <string>{self.script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/macorganizer.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/macorganizer.out</string>
</dict>
</plist>
"""
        try:
            self.launch_agents_dir.mkdir(parents=True, exist_ok=True)
            with open(self.plist_path, "w") as f:
                f.write(plist_content)
            return True, "Inicialização automática ativada!"
        except Exception as e:
            return False, f"Erro ao ativar: {e}"

    def disable(self):
        try:
            if self.plist_path.exists():
                self.plist_path.unlink()
            return True, "Inicialização automática desativada."
        except Exception as e:
            return False, f"Erro ao desativar: {e}"

# --- LÓGICA DO ORGANIZADOR ---
class OrganizadorHandler(FileSystemEventHandler):
    def __init__(self, callback_log, callback_sucesso):
        self.callback_log = callback_log
        self.callback_sucesso = callback_sucesso 
        
        self.regras = {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".heic"],
            "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv", ".epub"],
            "Instaladores": [".dmg", ".pkg", ".zip", ".rar", ".iso"],
            "Codigos": [".py", ".js", ".html", ".css", ".json", ".java", ".c"]
        }

    def on_created(self, event):
        if event.is_directory or ".crdownload" in event.src_path or ".DS_Store" in event.src_path:
            return
        self.organizar_arquivo(event.src_path)

    def organizar_arquivo(self, caminho_arquivo):
        time.sleep(1)
        path = Path(caminho_arquivo)
        if not path.exists(): return 

        extensao = path.suffix.lower()
        nome_arquivo = path.name
        pasta_downloads = path.parent
        moved = False
        
        for pasta, extensoes in self.regras.items():
            if extensao in extensoes:
                destino = pasta_downloads / pasta
                destino.mkdir(exist_ok=True)
                destino_final = destino / nome_arquivo
                
                # Tratamento de colisão de nomes
                if destino_final.exists():
                    timestamp = int(time.time())
                    destino_final = destino / f"{path.stem}_{timestamp}{path.suffix}"

                try:
                    shutil.move(caminho_arquivo, destino_final)
                    self.callback_log(f"Movido: {nome_arquivo} -> 📂 {pasta}")
                    
                    self.callback_sucesso(str(caminho_arquivo), str(destino_final))
                    
                    moved = True
                except Exception as e:
                    self.callback_log(f"Erro ao mover {nome_arquivo}: {e}")
                break
        
        if not moved:
            self.callback_log(f"Ignorado: {nome_arquivo}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mac Organizer AI")
        self.geometry("700x550") # Um pouco mais largo para caber o histórico
        
        self.download_folder = str(Path.home() / "Downloads")
        self.observer = None
        self.running = False
        self.autostart = AutoStartHandler()

        self.criar_interface()

    def criar_interface(self):
        # Título Principal
        self.label_titulo = ctk.CTkLabel(self, text="Organizador de Downloads", font=("Arial", 22, "bold"))
        self.label_titulo.pack(pady=10)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_painel = self.tabview.add("Painel de Controle")
        self.tab_historico = self.tabview.add("Histórico & Desfazer")

        # === ABA 1 ===     
        self.label_status = ctk.CTkLabel(self.tab_painel, text="Status: Parado", text_color="red", font=("Arial", 14))
        self.label_status.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(self.tab_painel, text="INICIAR MONITORAMENTO", command=self.toggle_monitoramento, 
                                      height=40, fg_color="green", hover_color="darkgreen")
        self.btn_toggle.pack(pady=10, padx=50, fill="x")

        self.switch_autostart = ctk.CTkSwitch(self.tab_painel, text="Iniciar junto com o macOS", command=self.toggle_autostart)
        self.switch_autostart.pack(pady=10)
        
        if self.autostart.is_enabled():
            self.switch_autostart.select()

        # Logs
        self.label_logs = ctk.CTkLabel(self.tab_painel, text="Logs de Atividade:", anchor="w")
        self.label_logs.pack(pady=(10,0), padx=20, fill="x")
        
        self.textbox_log = ctk.CTkTextbox(self.tab_painel, height=150)
        self.textbox_log.pack(pady=10, padx=20, fill="both", expand=True)
        self.textbox_log.insert("0.0", "--- Logs do Sistema ---\n")
        self.textbox_log.configure(state="disabled")

        # ===  ABA 2 ===
        
        self.label_hist = ctk.CTkLabel(self.tab_historico, text="Arquivos movidos recentemente:", anchor="w")
        self.label_hist.pack(pady=5, padx=10, fill="x")

        self.scroll_history = ctk.CTkScrollableFrame(self.tab_historico, label_text="Lista de Ações")
        self.scroll_history.pack(pady=5, padx=10, fill="both", expand=True)

        self.label_footer = ctk.CTkLabel(self, text=f"Monitorando: {self.download_folder}", text_color="gray")
        self.label_footer.pack(side="bottom", pady=5)

    def log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    def adicionar_ao_historico(self, path_origem, path_destino):
        self.after(0, lambda: self._criar_item_historico(path_origem, path_destino))

    def _criar_item_historico(self, origem, destino):
        path_dest = Path(destino)
        nome_arquivo = path_dest.name
        hora = datetime.now().strftime("%H:%M:%S")

        row_frame = ctk.CTkFrame(self.scroll_history)
        row_frame.pack(fill="x", pady=2, padx=5)

        label_info = ctk.CTkLabel(row_frame, text=f"[{hora}] {nome_arquivo}", anchor="w", width=300)
        label_info.pack(side="left", padx=10, pady=5)

        #Botão desfazer
        btn_undo = ctk.CTkButton(row_frame, text="Desfazer", width=80, fg_color="orange", hover_color="#d97706",
                                 command=lambda f=row_frame, o=origem, d=destino: self.desfazer_acao(f, o, d))
        btn_undo.pack(side="right", padx=10, pady=5)

    def desfazer_acao(self, frame_widget, origem, destino):
        try:
            if not os.path.exists(destino):
                self.log(f"⚠️ Erro ao desfazer: Arquivo não existe mais em {destino}")
                frame_widget.destroy()
                return

            # Move de volta
            shutil.move(destino, origem)
            self.log(f"Desfeito: {Path(destino).name} voltou para Downloads.")
            
            # Remove a linha do histórico visualmente
            frame_widget.destroy()

        except Exception as e:
            self.log(f"Erro crítico ao desfazer: {e}")

    # --- CONTROLES DO SISTEMA ---
    def toggle_autostart(self):
        if self.switch_autostart.get() == 1:
            sucesso, msg = self.autostart.enable()
        else:
            sucesso, msg = self.autostart.disable()
        self.log(msg)

    def start_monitoring(self):
        # Passamos self.adicionar_ao_historico como callback
        event_handler = OrganizadorHandler(self.log, self.adicionar_ao_historico)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.download_folder, recursive=False)
        self.observer.start()
        self.log(f"Monitoramento iniciado.")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.log("Monitoramento paralisado.")

    def toggle_monitoramento(self):
        if not self.running:
            self.running = True
            self.btn_toggle.configure(text="PARAR MONITORAMENTO", fg_color="red", hover_color="darkred")
            self.label_status.configure(text="Status: Rodando ", text_color="#00FF00")
            threading.Thread(target=self.start_monitoring, daemon=True).start()
        else:
            self.running = False
            self.btn_toggle.configure(text="INICIAR MONITORAMENTO", fg_color="green", hover_color="darkgreen")
            self.label_status.configure(text="Status: Parado", text_color="red")
            self.stop_monitoring()

if __name__ == "__main__":
    app = App()
    app.mainloop()