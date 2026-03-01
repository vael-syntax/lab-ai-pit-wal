import json
import os

class KnowledgeRetriever:
    """
    Módulo RAG simple y ligero.
    Sustituye a una base de datos vectorial costosa cargando un archivo JSON
    plano en memoria y devolviendo reglas de telemetría específicas.
    """
    def __init__(self, json_path: str = "brain/knowledge/acc_tips.json"):
        self.rules = []
        self._load_knowledge(json_path)

    def _load_knowledge(self, path: str):
        if not os.path.exists(path):
            print(f"[RAG] Advertencia: No se encontró la base de conocimiento en {path}")
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            print(f"[RAG] Cargados {len(self.rules)} tips técnicos de Telemetría.")
        except Exception as e:
            print(f"[RAG] Error cargando conocimiento: {e}")

    def get_all_context(self) -> str:
        """
        Para este caso de uso (prompting rápido a Gemini), inyectamos 
        todas las reglas juntas ya que el archivo JSON es pequeño.
        """
        if not self.rules:
            return ""
            
        context = "Aplica estrictamente estas Reglas Técnicas de Conducción:\n"
        for idx, rule in enumerate(self.rules):
            context += f"{idx+1}. {rule['titulo']}: {rule['descripcion']}\n"
        
        return context
