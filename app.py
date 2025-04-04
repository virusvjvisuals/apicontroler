import gradio as gr
import requests
import json
import os
import logging
import re
from datetime import datetime
from gradio_client import Client

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_controller.log'
)
logger = logging.getLogger('api_controller')

# Dossier pour stocker les configurations API
CONFIG_DIR = "api_configs"
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

# Classe pour gérer les API
class APIManager:
    def __init__(self):
        self.apis = self._load_apis()
        self.recordings = {}
    
    def _load_apis(self):
        """Charge les configurations API depuis le dossier de configuration"""
        apis = {}
        if os.path.exists(CONFIG_DIR):
            for filename in os.listdir(CONFIG_DIR):
                if filename.endswith(".json"):
                    with open(os.path.join(CONFIG_DIR, filename), 'r') as f:
                        api_config = json.load(f)
                        apis[api_config['name']] = api_config
        return apis
    
    def save_api(self, name, url, method, headers, params, body):
        """Enregistre une nouvelle configuration API"""
        api_config = {
            'name': name,
            'url': url,
            'method': method,
            'headers': headers,
            'params': params,
            'body': body,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Enregistre dans le dictionnaire
        self.apis[name] = api_config
        
        # Enregistre dans un fichier
        filename = f"{name.lower().replace(' ', '_')}.json"
        with open(os.path.join(CONFIG_DIR, filename), 'w') as f:
            json.dump(api_config, f, indent=4)
        
        return f"API '{name}' enregistrée avec succès"
    
    def save_recording(self, name, url, recording_data):
        """Enregistre une séquence d'API enregistrée via Gradio Recorder"""
        recording = {
            'name': name,
            'url': url,
            'steps': recording_data,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Enregistre dans le dictionnaire
        self.apis[name] = recording
        
        # Enregistre dans un fichier
        filename = f"{name.lower().replace(' ', '_')}.json"
        with open(os.path.join(CONFIG_DIR, filename), 'w') as f:
            json.dump(recording, f, indent=4)
        
        return f"Enregistrement '{name}' sauvegardé avec succès"

    def parse_recording(self, recording_text):
        """Parse le texte d'enregistrement Gradio Client en séquence d'étapes API"""
        steps = []
        
        # Extraction des appels client.predict
        predict_pattern = r'client\.predict\((.*?)\)'
        predict_matches = re.findall(predict_pattern, recording_text, re.DOTALL)
        
        for match in predict_matches:
            # Nettoie et transforme les paramètres en dict
            step_params = {}
            
            # Extraction des paramètres nommés
            param_pattern = r'(\w+)=([^,\n]*)'
            param_matches = re.findall(param_pattern, match)
            
            for param, value in param_matches:
                # Essayer de convertir en type approprié
                if value == 'None':
                    step_params[param] = None
                elif value.lower() == 'true':
                    step_params[param] = True
                elif value.lower() == 'false':
                    step_params[param] = False
                elif value.isdigit():
                    step_params[param] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    step_params[param] = float(value)
                else:
                    # C'est probablement une chaîne ou une structure complexe
                    step_params[param] = value.strip('"\'')
            
            # Si api_name est présent, c'est un endpoint
            if 'api_name' in step_params:
                steps.append(step_params)
        
        return steps
    
    def execute_api(self, name):
        """Exécute une API enregistrée"""
        if name not in self.apis:
            logger.error(f"API '{name}' non trouvée")
            return False, f"Erreur: API '{name}' non trouvée"
        
        api = self.apis[name]
        
        # Si c'est une séquence d'API enregistrée (contient 'steps')
        if 'steps' in api:
            return self.execute_recording(api)
        
        # Sinon c'est une API simple
        try:
            headers = json.loads(api['headers']) if api['headers'] else {}
            params = json.loads(api['params']) if api['params'] else {}
            body = json.loads(api['body']) if api['body'] else {}
            
            response = requests.request(
                method=api['method'],
                url=api['url'],
                headers=headers,
                params=params,
                json=body,
                timeout=30
            )
            
            logger.info(f"API '{name}' exécutée. Status: {response.status_code}")
            
            # Vérifie si la réponse est un succès (codes 2xx)
            if 200 <= response.status_code < 300:
                try:
                    return True, f"Succès: {response.status_code}\n{json.dumps(response.json(), indent=2)}"
                except:
                    return True, f"Succès: {response.status_code}\n{response.text[:1000]}"
            else:
                return False, f"Échec: {response.status_code}\n{response.text[:1000]}"
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'API '{name}': {str(e)}")
            return False, f"Erreur: {str(e)}"
    
    def execute_recording(self, recording):
        """Exécute une séquence d'appels API enregistrée"""
        try:
            client = Client(recording['url'])
            results = []
            success = True
            
            for step in recording['steps']:
                try:
                    # Extrait api_name et supprime-le des paramètres
                    api_name = step.pop('api_name', None)
                    if not api_name:
                        continue
                    
                    # Exécute l'étape
                    result = client.predict(**step, api_name=api_name)
                    results.append(f"Succès: {api_name}")
                except Exception as e:
                    results.append(f"Échec: {api_name} - {str(e)}")
                    success = False
            
            result_text = "\n".join(results)
            return success, f"Exécution de l'enregistrement '{recording['name']}':\n{result_text}"
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'enregistrement '{recording['name']}': {str(e)}")
            return False, f"Erreur: {str(e)}"
    
    def debug_api(self, name):
        """Débogue une API en vérifiant sa configuration et en testant sa connectivité"""
        if name not in self.apis:
            return f"API '{name}' non trouvée dans les configurations."
        
        api = self.apis[name]
        debug_info = [f"=== Débogage de l'API '{name}' ==="]
        
        # Si c'est un enregistrement, traitement spécifique
        if 'steps' in api:
            debug_info.append("\n1. Vérification de l'enregistrement:")
            debug_info.append(f"✓ URL: {api['url']}")
            debug_info.append(f"✓ Nombre d'étapes: {len(api['steps'])}")
            
            # Test de connectivité
            debug_info.append("\n2. Test de connectivité:")
            try:
                response = requests.head(api['url'], timeout=5)
                debug_info.append(f"✓ Serveur joignable: {api['url']} (Status: {response.status_code})")
            except requests.exceptions.ConnectionError:
                debug_info.append(f"❌ Impossible de se connecter au serveur: {api['url']}")
            except requests.exceptions.Timeout:
                debug_info.append(f"❌ Timeout lors de la connexion au serveur: {api['url']}")
            
            debug_info.append("\n3. Détails des étapes:")
            for i, step in enumerate(api['steps']):
                api_name = step.get('api_name', 'Inconnu')
                debug_info.append(f"Étape {i+1}: {api_name}")
                
            debug_info.append("\n4. Solutions possibles:")
            if "❌ Impossible de se connecter" in '\n'.join(debug_info):
                debug_info.append("- Vérifiez que l'application cible est en ligne")
                debug_info.append("- Vérifiez que l'URL est correcte")
                debug_info.append("- Si l'URL est locale, assurez-vous que le service est démarré")
            
            return '\n'.join(debug_info)
        
        # Sinon, débogage standard d'API
        # Vérification de la configuration
        debug_info.append("\n1. Vérification de la configuration:")
        if not api['url']:
            debug_info.append("❌ URL manquante")
        else:
            debug_info.append(f"✓ URL: {api['url']}")
        
        if not api['method']:
            debug_info.append("❌ Méthode HTTP manquante")
        else:
            debug_info.append(f"✓ Méthode: {api['method']}")
        
        # Test de connectivité
        debug_info.append("\n2. Test de connectivité:")
        try:
            # Juste un HEAD request pour vérifier la connectivité
            response = requests.head(api['url'], timeout=5)
            debug_info.append(f"✓ Serveur joignable: {api['url']} (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            debug_info.append(f"❌ Impossible de se connecter au serveur: {api['url']}")
        except requests.exceptions.Timeout:
            debug_info.append(f"❌ Timeout lors de la connexion au serveur: {api['url']}")
        except Exception as e:
            debug_info.append(f"❌ Erreur de connexion: {str(e)}")
        
        # Analyse des dernières exécutions
        debug_info.append("\n3. Solutions possibles:")
        if "non trouvée" in debug_info[0]:
            debug_info.append("- Vérifiez que le nom de l'API est correct")
            debug_info.append("- Réenregistrez l'API si nécessaire")
        elif "❌ URL manquante" in debug_info:
            debug_info.append("- Ajoutez une URL valide à la configuration")
        elif "❌ Méthode HTTP manquante" in debug_info:
            debug_info.append("- Définissez une méthode HTTP (GET, POST, etc.)")
        elif "❌ Impossible de se connecter" in '\n'.join(debug_info):
            debug_info.append("- Vérifiez que le serveur est en ligne")
            debug_info.append("- Vérifiez votre connexion internet")
            debug_info.append("- Si l'URL contient 'localhost', assurez-vous que le service local est démarré")
        elif "❌ Timeout" in '\n'.join(debug_info):
            debug_info.append("- Le serveur est peut-être surchargé ou répond lentement")
            debug_info.append("- Réessayez plus tard ou augmentez le timeout")
        
        return '\n'.join(debug_info)
    
    def get_api_names(self):
        """Retourne la liste des noms d'API enregistrées"""
        return list(self.apis.keys())

# Initialisation du gestionnaire d'API
api_manager = APIManager()

# Fonction pour enregistrer une nouvelle API
def record_api(name, url, method, headers, params, body):
    if not name:
        return "Erreur: Le nom de l'API est requis"
    if not url:
        return "Erreur: L'URL de l'API est requise"
    if not method:
        return "Erreur: La méthode HTTP est requise"
    
    return api_manager.save_api(name, url, method, headers, params, body)

# Fonction pour enregistrer une séquence Gradio Client
def save_recording(name, url, recording_text):
    if not name:
        return "Erreur: Le nom de l'enregistrement est requis"
    if not url:
        return "Erreur: L'URL de l'application cible est requise"
    if not recording_text:
        return "Erreur: Le contenu de l'enregistrement est requis"
    
    try:
        recording_data = api_manager.parse_recording(recording_text)
        if not recording_data:
            return "Erreur: Aucune étape API valide trouvée dans l'enregistrement"
        
        return api_manager.save_recording(name, url, recording_data)
    except Exception as e:
        return f"Erreur lors de l'analyse de l'enregistrement: {str(e)}"

# Fonction pour exécuter une API
def execute_api(api_name):
    success, result = api_manager.execute_api(api_name)
    return success, result

# Fonction pour déboguer une API
def debug_api(api_name):
    return api_manager.debug_api(api_name)

# Fonction pour actualiser la liste des API
def refresh_api_list():
    api_manager.apis = api_manager._load_apis()
    return gr.Dropdown(choices=api_manager.get_api_names())

# Interface Gradio
with gr.Blocks(title="Contrôleur d'API") as app:
    gr.Markdown("# Contrôleur d'API")
    
    with gr.Tabs():
        # Onglet d'enregistrement d'API
        with gr.TabItem("Enregistrer une API"):
            with gr.Row():
                with gr.Column():
                    api_name = gr.Textbox(label="Nom de l'API")
                    api_url = gr.Textbox(label="URL")
                    api_method = gr.Dropdown(
                        label="Méthode HTTP", 
                        choices=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                        value="GET"
                    )
            
            with gr.Row():
                with gr.Column():
                    api_headers = gr.Textbox(
                        label="Headers (JSON)",
                        placeholder='{"Content-Type": "application/json"}'
                    )
                    api_params = gr.Textbox(
                        label="Paramètres (JSON)",
                        placeholder='{"param1": "value1"}'
                    )
                    api_body = gr.Textbox(
                        label="Corps de la requête (JSON)",
                        placeholder='{"key": "value"}'
                    )
            
            record_btn = gr.Button("Enregistrer l'API")
            record_result = gr.Textbox(label="Résultat")
            
            record_btn.click(
                record_api,
                inputs=[api_name, api_url, api_method, api_headers, api_params, api_body],
                outputs=record_result
            )
        
        # Onglet d'enregistrement de séquence Gradio Client
        with gr.TabItem("Importer un enregistrement Gradio"):
            gr.Markdown("""
            ## Importer un enregistrement Gradio Client
            
            Collez le code généré par Gradio Recorder pour créer une séquence d'appels API.
            """)
            
            with gr.Row():
                with gr.Column():
                    recording_name = gr.Textbox(label="Nom de l'enregistrement")
                    recording_url = gr.Textbox(
                        label="URL de l'application cible", 
                        placeholder="http://127.0.0.1:7860/"
                    )
            
            with gr.Row():
                with gr.Column():
                    recording_text = gr.Textbox(
                        label="Code d'enregistrement Gradio Client",
                        placeholder='client.predict(\n  param1=value1,\n  param2=value2,\n  api_name="/endpoint"\n)',
                        lines=15
                    )
            
            save_recording_btn = gr.Button("Enregistrer la séquence")
            save_recording_result = gr.Textbox(label="Résultat")
            
            save_recording_btn.click(
                save_recording,
                inputs=[recording_name, recording_url, recording_text],
                outputs=save_recording_result
            )
        
        # Onglet d'exécution d'API
        with gr.TabItem("Exécuter des API"):
            with gr.Row():
                with gr.Column():
                    api_dropdown = gr.Dropdown(
                        label="Sélectionner une API", 
                        choices=api_manager.get_api_names()
                    )
                    refresh_btn = gr.Button("Actualiser la liste")
            
            execute_btn = gr.Button("Exécuter l'API")
            
            with gr.Row():
                with gr.Column():
                    status_indicator = gr.Label(label="Statut")
                    api_response = gr.Textbox(label="Réponse", lines=10)
                    debug_btn = gr.Button("Déboguer", visible=False)
                    debug_info = gr.Textbox(label="Informations de débogage", lines=15, visible=False)
            
            refresh_btn.click(
                refresh_api_list,
                inputs=[],
                outputs=[api_dropdown]
            )
            
            def update_status(success, result):
                debug_btn_visible = not success
                debug_info_visible = False
                status = "✅ Succès" if success else "❌ Échec"
                return status, result, debug_btn_visible, debug_info_visible
            
            execute_btn.click(
                execute_api,
                inputs=[api_dropdown],
                outputs=[status_indicator, api_response, debug_btn, debug_info]
            ).then(
                update_status,
                inputs=[status_indicator, api_response],
                outputs=[status_indicator, api_response, debug_btn, debug_info]
            )
            
            debug_btn.click(
                debug_api,
                inputs=[api_dropdown],
                outputs=[debug_info]
            ).then(
                lambda x: True,
                inputs=[],
                outputs=[debug_info]
            )

# Lancement de l'application
if __name__ == "__main__":
    app.launch()
