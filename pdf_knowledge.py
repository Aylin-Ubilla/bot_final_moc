import os
import PyPDF2
import re
import json
import nltk
from nltk.tokenize import sent_tokenize

# Descargar recursos necesarios de NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ManualKnowledge:
    def __init__(self, pdf_path=None):
        self.pdf_path = pdf_path
        self.knowledge_base = {}
        self.system_keywords = {
            'APU': ['apu', 'auxiliary power unit', 'unidad auxiliar'],
            'MOTOR': ['motor', 'engine', 'turbina', 'propulsor', 'powerplant'],
            'TREN': ['tren', 'landing gear', 'ruedas', 'aterrizaje', 'lgear'],
            'HIDRAULICO': ['hidraulico', 'hydraulic', 'hyd', 'presion', 'fluido'],
            'ELECTRICO': ['electrico', 'electrical', 'power', 'bateria', 'energia'],
            'CABINA': ['cabina', 'cabin', 'pax', 'pasajeros', 'asientos'],
            'GALLEY': ['galley', 'cocina', 'catering', 'comida', 'bebida']
        }
        self.problem_keywords = {
            'NO_ARRANCA': ['no arranca', 'no enciende', 'falla arranque', 'won\'t start'],
            'NO_FUNCIONA': ['no funciona', 'inoperativo', 'falla', 'not working'],
            'ERROR': ['error', 'warning', 'alerta', 'mensaje', 'luz', 'indication'],
            'REVISAR': ['revisar', 'verificar', 'chequear', 'check', 'inspeccionar']
        }
        
        # Cargar conocimiento si se proporciona un PDF
        if pdf_path and os.path.exists(pdf_path):
            self.extract_knowledge_from_pdf()
    
    def extract_knowledge_from_pdf(self):
        """Extrae conocimiento del PDF y lo organiza por sistema y problema"""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            print(f"Error: No se puede encontrar el archivo PDF en {self.pdf_path}")
            return
        
        # Extraer texto del PDF
        text = self._extract_text_from_pdf()
        
        # Dividir en secciones (párrafos)
        sections = self._split_into_sections(text)
        
        # Clasificar secciones por sistema y problema
        self._classify_sections(sections)
        
        # Guardar la base de conocimiento
        self._save_knowledge_base()
    
    def _extract_text_from_pdf(self):
        """Extrae todo el texto del PDF"""
        text = ""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error al extraer texto del PDF: {e}")
            return ""
    
    def _split_into_sections(self, text):
        """Divide el texto en secciones (párrafos)"""
        # Eliminar saltos de línea múltiples
        text = re.sub(r'\n+', '\n', text)
        
        # Dividir por párrafos (bloques separados por líneas en blanco)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Dividir párrafos largos en oraciones
        sections = []
        for paragraph in paragraphs:
            if len(paragraph.split()) > 50:  # Si el párrafo es muy largo
                sentences = sent_tokenize(paragraph)
                sections.extend(sentences)
            else:
                sections.append(paragraph)
        
        return [s.strip() for s in sections if s.strip()]
    
    def _classify_sections(self, sections):
        """Clasifica las secciones por sistema y problema"""
        for section in sections:
            section_lower = section.lower()
            
            # Detectar sistemas mencionados
            systems_found = []
            for system, keywords in self.system_keywords.items():
                if any(keyword in section_lower for keyword in keywords):
                    systems_found.append(system)
            
            # Detectar problemas mencionados
            problems_found = []
            for problem, keywords in self.problem_keywords.items():
                if any(keyword in section_lower for keyword in keywords):
                    problems_found.append(problem)
            
            # Si se encontró al menos un sistema y un problema, guardar la sección
            if systems_found and problems_found:
                for system in systems_found:
                    if system not in self.knowledge_base:
                        self.knowledge_base[system] = {}
                    
                    for problem in problems_found:
                        if problem not in self.knowledge_base[system]:
                            self.knowledge_base[system][problem] = []
                        
                        self.knowledge_base[system][problem].append(section)
    
    def _save_knowledge_base(self):
        """Guarda la base de conocimiento en un archivo JSON"""
        knowledge_path = os.path.join(os.path.dirname(self.pdf_path), 'knowledge_base.json')
        try:
            with open(knowledge_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            print(f"Base de conocimiento guardada en {knowledge_path}")
        except Exception as e:
            print(f"Error al guardar la base de conocimiento: {e}")
    
    def load_knowledge_base(self, json_path):
        """Carga la base de conocimiento desde un archivo JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"Base de conocimiento cargada desde {json_path}")
            return True
        except Exception as e:
            print(f"Error al cargar la base de conocimiento: {e}")
            return False
    
    def get_response(self, system, problem):
        """Obtiene una respuesta para un sistema y problema específicos"""
        if system in self.knowledge_base and problem in self.knowledge_base[system]:
            # Devolver la sección más relevante (la primera por ahora)
            return self.knowledge_base[system][problem][0]
        return None
    
    def get_all_responses(self, system, problem):
        """Obtiene todas las respuestas para un sistema y problema específicos"""
        if system in self.knowledge_base and problem in self.knowledge_base[system]:
            return self.knowledge_base[system][problem]
        return []

# Función para procesar un PDF y generar la base de conocimiento
def process_manual(pdf_path):
    knowledge = ManualKnowledge(pdf_path)
    return knowledge 

def load_knowledge_base(file_path):
    """Load knowledge base from a JSON file"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            print(f"Knowledge base loaded from {file_path}")
            return knowledge_base
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {}
    else:
        print(f"Knowledge base file not found: {file_path}")
        return {}

def save_knowledge_base(file_path, knowledge_base):
    """Save knowledge base to a JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        print(f"Knowledge base saved to {file_path}")
    except Exception as e:
        print(f"Error saving knowledge base: {e}")

def add_knowledge(sistema, problema, respuesta):
    """Add knowledge to the knowledge base"""
    key = f"{sistema}_{problema}".lower()
    knowledge_base[key] = respuesta

def get_response(sistema, problema):
    """Get response from knowledge base"""
    if not sistema or not problema:
        return None
            
    key = f"{sistema}_{problema}".lower()
    return knowledge_base.get(key) 