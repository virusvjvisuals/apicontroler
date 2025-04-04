import gradio as gr
import json
import os
import requests
import traceback
from pathlib import Path

# Configuration des chemins
RECORDINGS_DIR = Path("./recordings")
RECORDINGS_DIR.mkdir(exist_ok=True)

# Classe pour gérer les APIs et leurs enregistrements
class APIController:
    def __init__(self):
        self.recordings = {}
        self.load_recordings()
    
    def load_recordings(self):
        """Charge tous les enregistrements depuis le répertoire"""
        self.recordings = {}
        for file in RECORDINGS_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    recording = json.load(f)
                    name = file.stem
                    self.recordings[name] = recording
            except Exception as e:
                print(f"Erreur lors du chargement de {file}: {e}")
    
    def save_recording(self, name, api_url, request_data):
        """Enregistre une nouvelle API"""
        recording = {
            "api_url": api_url,
            "request_data": request_data
        }
        
        filename = RECORDINGS_DIR / f"{name}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(recording, f, indent=2, ensure_ascii=False)
        
        self.recordings[name] = recording
        return True
    
    def execute_recording(self, name):
        """Exécute un enregistrement API"""
        if name not in self.recordings:
            return False, f"Enregistrement '{name}' introuvable", None
        
        recording = self.recordings[name]
        api_url = recording["api_url"]
        request_data = recording["request_data"]
        
        log = f"Exécution de l'enregistrement '{name}':\n"
        
        try:
            response = requests.post(api_url, json=request_data)
            response.raise_for_status()
            
            log += f"Requête envoyée à {api_url}\n"
            log += f"Statut: {response.status_code}\n"
            
            if response.text:
                try:
                    log += f"Réponse: {json.dumps(response.json(), indent=2)[:500]}\n"
                except:
                    log += f"Réponse: {response.text[:500]}\n"
            
            return True, log, "", ""
            
        except Exception as e:
            error_log = f"ERREUR: {str(e)}\n{traceback.format_exc()}"
            return False, log, True, error_log

# Initialisation du contrôleur
controller = APIController()

# Interface Gradio
with gr.Blocks(title="API Controller") as app:
    gr.Markdown("# API Controller")
    
    with gr.Tab("Exécuter API"):
        with gr.Row():
            recording_dropdown = gr.Dropdown(
                label="Sélectionner un enregistrement",
                choices=list(controller.recordings.keys()),
                interactive=True
            )
            refresh_btn = gr.Button("Actualiser")
        
        execute_btn = gr.Button("Exécuter l'API")
        
        with gr.Row():
            status_label = gr.Label(label="Statut")
            execution_log = gr.TextArea(label="Log d'exécution", lines=10)
        
        with gr.Row():
            debug_btn = gr.Button("Debug", visible=False)
            debug_log = gr.TextArea(label="Détails de l'erreur", visible=False, lines=10)
    
    with gr.Tab("Enregistrer API"):
        api_name = gr.Textbox(label="Nom de l'enregistrement")
        api_url = gr.Textbox(label="URL de l'API")
        api_request = gr.TextArea(label="Données de la requête (JSON)", lines=5)
        save_btn = gr.Button("Enregistrer")
        save_status = gr.Markdown()
    
    def refresh_recordings():
        controller.load_recordings()
        return gr.Dropdown(choices=list(controller.recordings.keys()))
    
    def save_api(name, url, request_data):
        try:
            # Validation des données JSON
            json_data = json.loads(request_data)
            result = controller.save_recording(name, url, json_data)
            return gr.Markdown("✅ Enregistrement sauvegardé avec succès!")
        except json.JSONDecodeError:
            return gr.Markdown("❌ Erreur: Les données de requête ne sont pas un JSON valide.")
        except Exception as e:
            return gr.Markdown(f"❌ Erreur lors de l'enregistrement: {str(e)}")
    
    def execute_api(name):
        success, log, debug_visible, debug_text = controller.execute_recording(name)
        return success, log, gr.Button(visible=not success), gr.TextArea(value=debug_text, visible=not success)
    
    # Événements
    refresh_btn.click(refresh_recordings, outputs=[recording_dropdown])
    save_btn.click(save_api, [api_name, api_url, api_request], [save_status])
    execute_btn.click(execute_api, [recording_dropdown], [status_label, execution_log, debug_btn, debug_log])

if __name__ == "__main__":
    app.launch()
