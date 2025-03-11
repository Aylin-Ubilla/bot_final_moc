import os
import re
import json
from datetime import datetime
from collections import defaultdict
import random
import time
import uuid
from pdf_knowledge import ManualKnowledge

class WhatsAppBot:
    def __init__(self):
        # Sistemas y problemas con palabras clave expandidas
        self.sistemas = {
            'APU': ['apu', 'auxiliary', 'auxiliar', 'power unit', 'unidad auxiliar'],
            'MOTOR': ['motor', 'engine', 'engines', 'powerplant', 'motores', 'turbina', 'propulsor', 'n1', 'n2'],
            'TREN': ['tren', 'gear', 'landing', 'lgear', 'ruedas', 'aterrizaje', 'mlg', 'nlg', 'llantas'],
            'HIDRAULICO': ['hidraulico', 'hydraulic', 'hyd', 'presion', 'fluido', 'fluid', 'presión', 'bomba', 'pump'],
            'ELECTRICO': ['electrico', 'electrical', 'power', 'bateria', 'energia', 'battery', 'electric', 'luz', 'light'],
            'CABINA': ['cabina', 'cabin', 'pax', 'pasajeros', 'passenger', 'asientos', 'seats', 'oxigeno', 'oxygen'],
            'GALLEY': ['galley', 'cocina', 'catering', 'comida', 'food', 'bebida', 'drink', 'horno', 'oven']
        }
        
        # Problemas con frases completas
        self.problemas = {
            'NO_ARRANCA': ['no arranca', 'no enciende', 'no prende', 'falla arranque', 'problema arranque', 
                          'won\'t start', 'no start', 'failed to start', 'start failure'],
            'NO_FUNCIONA': ['no funciona', 'no opera', 'inoperativo', 'falla', 'mal funcionamiento', 
                           'not working', 'inoperative', 'failure', 'malfunction', 'broken'],
            'ERROR': ['error', 'warning', 'alerta', 'mensaje', 'indicacion', 'luz', 'indication', 
                     'light', 'caution', 'fault', 'code', 'código'],
            'REVISAR': ['revisar', 'verificar', 'chequear', 'check', 'inspeccionar', 'inspect', 
                       'review', 'examine', 'test', 'probar']
        }
        
        # Historial de conversaciones
        self.conversaciones = defaultdict(list)
        self.contexto_actual = {}
        
        # Cargar respuestas predefinidas
        self.respuestas_comunes = {
            'saludo': ['Hola', 'Buen día', 'Saludos', 'Hola, ¿en qué puedo ayudarte?'],
            'despedida': ['Hasta luego', 'Adiós', 'Que tengas buen día', 'Gracias por contactarnos'],
            'agradecimiento': ['De nada', 'Con gusto', 'Para servirte', 'Estamos para ayudar']
        }
        
        # Respuestas automatizadas para casos comunes
        self.respuestas_automaticas = {
            ('APU', 'NO_ARRANCA'): [
                "Para problemas de arranque de APU, verifica lo siguiente:\n\n"
                "1. Asegúrate que el interruptor de batería esté en posición ON\n"
                "2. Verifica que el nivel de combustible sea adecuado\n"
                "3. Comprueba que no haya mensajes de error en el ECAM/EICAS\n"
                "4. Intenta un ciclo completo de apagado y encendido\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ],
            ('MOTOR', 'NO_ARRANCA'): [
                "Para problemas de arranque de motor, verifica lo siguiente:\n\n"
                "1. Asegúrate que el suministro de combustible sea adecuado\n"
                "2. Verifica que el sistema de ignición esté funcionando correctamente\n"
                "3. Comprueba que no haya mensajes de error en el ECAM/EICAS\n"
                "4. Revisa el procedimiento de arranque en el manual\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ],
            ('TREN', 'NO_FUNCIONA'): [
                "Para problemas con el tren de aterrizaje, verifica lo siguiente:\n\n"
                "1. Comprueba el sistema hidráulico y nivel de presión\n"
                "2. Verifica que no haya obstrucciones mecánicas\n"
                "3. Revisa los indicadores de posición del tren\n"
                "4. Considera usar el sistema de extensión de emergencia si es necesario\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ],
            ('HIDRAULICO', 'ERROR'): [
                "Para problemas con el sistema hidráulico, verifica lo siguiente:\n\n"
                "1. Comprueba el nivel de fluido hidráulico\n"
                "2. Verifica que no haya fugas visibles\n"
                "3. Revisa la presión del sistema\n"
                "4. Comprueba el funcionamiento de las bombas\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ],
            ('ELECTRICO', 'ERROR'): [
                "Para problemas con el sistema eléctrico, verifica lo siguiente:\n\n"
                "1. Comprueba los disyuntores (circuit breakers)\n"
                "2. Verifica el estado de las baterías\n"
                "3. Revisa las conexiones de los generadores\n"
                "4. Comprueba los buses eléctricos principales\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ],
            ('GALLEY', 'NO_FUNCIONA'): [
                "Para problemas con el galley, verifica lo siguiente:\n\n"
                "1. Comprueba que el interruptor de alimentación esté activado\n"
                "2. Verifica que el sistema eléctrico del galley esté operativo\n"
                "3. Revisa los disyuntores específicos del galley\n"
                "4. Comprueba las conexiones de los equipos\n\n"
                "Si el problema persiste, proporciona más detalles para ayudarte mejor."
            ]
        }
        
        # Respuestas para problemas específicos
        self.respuestas_especificas = {
            'apu overheat': "Para un mensaje de APU OVERHEAT:\n\n"
                           "1. Apaga el APU inmediatamente\n"
                           "2. Verifica posibles fugas de fluidos alrededor del APU\n"
                           "3. Espera al menos 30 minutos para enfriamiento\n"
                           "4. Consulta el MEL para determinar si el vuelo puede continuar\n\n"
                           "Este problema requiere inspección de mantenimiento antes del próximo vuelo.",
            
            'low oil pressure': "Para un mensaje de LOW OIL PRESSURE:\n\n"
                               "1. Monitorea la presión de aceite y temperatura\n"
                               "2. Reduce la potencia del motor si es posible\n"
                               "3. Prepárate para un posible apagado del motor\n"
                               "4. Consulta el QRH para el procedimiento específico\n\n"
                               "Este problema requiere atención inmediata de mantenimiento.",
            
            'hydraulic low level': "Para un mensaje de HYDRAULIC LOW LEVEL:\n\n"
                                  "1. Verifica posibles fugas en el sistema hidráulico\n"
                                  "2. Monitorea la presión del sistema\n"
                                  "3. Considera las limitaciones de operación\n"
                                  "4. Consulta el MEL para determinar restricciones\n\n"
                                  "Este problema requiere inspección de mantenimiento antes del próximo vuelo.",
            
            'cargo door': "Para problemas con la puerta de carga:\n\n"
                         "1. Verifica que los mecanismos de cierre estén correctamente enganchados\n"
                         "2. Comprueba que no haya obstrucciones en los sellos\n"
                         "3. Revisa los indicadores de estado de la puerta\n"
                         "4. Considera un reinicio del sistema eléctrico\n\n"
                         "Si el problema persiste, se requiere inspección de mantenimiento."
        }

        # Añadir configuración para el registro de conversaciones
        self.log_dir = "logs"
        self.stats_file = "conversation_stats.json"
        
        # Crear directorio de logs si no existe
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Inicializar estadísticas
        self.stats = self.cargar_estadisticas()
        
        # Cargar base de conocimiento del manual
        self.manual_knowledge = ManualKnowledge()
        knowledge_path = os.path.join(self.log_dir, 'knowledge_base.json')
        if os.path.exists(knowledge_path):
            self.manual_knowledge.load_knowledge_base(knowledge_path)
        else:
            print("No se encontró la base de conocimiento del manual.")

    def cargar_estadisticas(self):
        """Carga las estadísticas desde el archivo JSON"""
        stats_path = os.path.join(self.log_dir, self.stats_file)
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar estadísticas: {e}")
                return self.inicializar_estadisticas()
        else:
            return self.inicializar_estadisticas()
    
    def inicializar_estadisticas(self):
        """Inicializa la estructura de estadísticas"""
        return {
            "total_conversaciones": 0,
            "total_mensajes": 0,
            "tiempo_respuesta_promedio": 0,
            "consultas_por_sistema": {},
            "consultas_por_problema": {},
            "consultas_urgentes": 0,
            "derivaciones_agente": 0,
            "respuestas_automaticas": 0,
            "conversaciones": [],
            "consultas_satisfactorias": 0,
            "total_encuestas": 0
        }
    
    def guardar_estadisticas(self):
        """Guarda las estadísticas en el archivo JSON"""
        stats_path = os.path.join(self.log_dir, self.stats_file)
        try:
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")
    
    def registrar_conversacion(self, id_usuario, mensajes, sistema=None, problema=None, matricula=None, es_urgente=False, derivado_agente=False, respuesta_automatica=False):
        """Registra una conversación completa en las estadísticas"""
        # Incrementar contadores
        self.stats["total_conversaciones"] += 1
        self.stats["total_mensajes"] += len(mensajes)
        
        if es_urgente:
            self.stats["consultas_urgentes"] += 1
        
        if derivado_agente:
            self.stats["derivaciones_agente"] += 1
        
        if respuesta_automatica:
            self.stats["respuestas_automaticas"] += 1
        
        # Registrar sistema y problema
        if sistema:
            self.stats["consultas_por_sistema"][sistema] = self.stats["consultas_por_sistema"].get(sistema, 0) + 1
        
        if problema:
            self.stats["consultas_por_problema"][problema] = self.stats["consultas_por_problema"].get(problema, 0) + 1
        
        # Crear registro de conversación
        conversacion = {
            "id": str(uuid.uuid4()),
            "id_usuario": id_usuario,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sistema": sistema,
            "problema": problema,
            "matricula": matricula,
            "es_urgente": es_urgente,
            "derivado_agente": derivado_agente,
            "respuesta_automatica": respuesta_automatica,
            "mensajes": mensajes
        }
        
        # Añadir a la lista de conversaciones
        self.stats["conversaciones"].append(conversacion)
        
        # Guardar estadísticas actualizadas
        self.guardar_estadisticas()
        
        # También guardar esta conversación en un archivo separado para facilitar la búsqueda
        self.guardar_conversacion_individual(conversacion)
    
    def guardar_conversacion_individual(self, conversacion):
        """Guarda una conversación individual en un archivo JSON separado"""
        conv_id = conversacion["id"]
        conv_path = os.path.join(self.log_dir, f"conv_{conv_id}.json")
        try:
            with open(conv_path, 'w', encoding='utf-8') as f:
                json.dump(conversacion, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar conversación individual: {e}")

    def detectar_sistema_y_problema(self, mensaje):
        """Detecta el sistema, problema y matrícula mencionados en el mensaje"""
        mensaje_lower = mensaje.lower()
        
        # Sistemas posibles (ampliados y mejorados)
        sistemas = {
            'apu': ['apu', 'auxiliary power unit', 'unidad auxiliar'],
            'motor': ['motor', 'engine', 'turbina', 'propulsor'],
            'tren': ['tren', 'landing gear', 'ruedas', 'aterrizaje', 'landing'],
            'hidraulico': ['hidraulico', 'hydraulic', 'hidráulico', 'fluido'],
            'electrico': ['electrico', 'eléctrico', 'electric', 'electrical', 'sistema eléctrico'],
            'cabina': ['cabina', 'cockpit', 'panel', 'instrumentos'],
            'galley': ['galley', 'cocina', 'catering']
        }
        
        # Problemas posibles (ampliados y mejorados)
        problemas = {
            'NO_ARRANCA': ['no arranca', 'no enciende', 'no prende', 'won\'t start', 'no start'],
            'NO_FUNCIONA': ['no funciona', 'no opera', 'inoperativo', 'falla', 'not working', 'doesn\'t work', 'fallo'],
            'ERROR': ['error', 'warning', 'alerta', 'mensaje', 'indicador', 'luz'],
            'REVISAR': ['revisar', 'verificar', 'check', 'inspeccionar', 'comprobar', 'verificación'],
            'RESET': ['reset', 'reinicio', 'reiniciar', 'resetear', 'restart']
        }
        
        # Detectar sistema con mayor flexibilidad
        sistema_detectado = None
        for sistema, keywords in sistemas.items():
            for keyword in keywords:
                if keyword in mensaje_lower:
                    sistema_detectado = sistema.upper()
                    break
            if sistema_detectado:
                break
        
        # Detectar problema con mayor flexibilidad
        problema_detectado = None
        for problema, keywords in problemas.items():
            for keyword in keywords:
                if keyword in mensaje_lower:
                    problema_detectado = problema
                    break
            if problema_detectado:
                break
        
        # Caso especial para "check" o "verificar" + sistema
        if 'check' in mensaje_lower or 'verificar' in mensaje_lower or 'revisar' in mensaje_lower:
            problema_detectado = 'REVISAR'
        
        # Si no se detectó un problema específico pero hay palabras como "problema" o "issue"
        if not problema_detectado and ('problema' in mensaje_lower or 'issue' in mensaje_lower or 'falla' in mensaje_lower):
            problema_detectado = 'NO_FUNCIONA'  # Asignar un problema genérico
        
        # Detectar matrícula (formato CC-XXX) con mayor flexibilidad
        matricula_match = re.search(r'CC-[A-Z]{3}', mensaje.upper())
        if not matricula_match:
            # Intentar otros formatos como "CC XXX" o "CCXXX"
            matricula_match = re.search(r'CC\s+[A-Z]{3}', mensaje.upper())
            if matricula_match:
                matricula_detectada = matricula_match.group(0).replace(' ', '-')
            else:
                matricula_match = re.search(r'CC[A-Z]{3}', mensaje.upper())
                if matricula_match:
                    texto = matricula_match.group(0)
                    matricula_detectada = f"{texto[:2]}-{texto[2:]}"
                else:
                    matricula_detectada = None
        else:
            matricula_detectada = matricula_match.group(0)
        
        # Imprimir para depuración
        print(f"Sistema detectado: {sistema_detectado}, Problema detectado: {problema_detectado}, Matrícula detectada: {matricula_detectada}")
        
        return sistema_detectado, problema_detectado, matricula_detectada

    def detectar_problema_especifico(self, texto):
        """Detecta problemas específicos en el texto"""
        texto = texto.lower()
        
        for problema_clave in self.respuestas_especificas.keys():
            if problema_clave in texto:
                return problema_clave
        
        return None

    def obtener_contexto(self, id_usuario):
        """Recupera el contexto de la conversación actual"""
        return self.contexto_actual.get(id_usuario, {})

    def procesar_mensaje(self, mensaje, id_usuario="web_user"):
        # Registrar tiempo de inicio
        tiempo_inicio = time.time()
        
        # Inicializar contexto si no existe
        if id_usuario not in self.contexto_actual:
            self.contexto_actual[id_usuario] = {}
        
        # Verificar si el usuario está en una encuesta de satisfacción
        if 'en_encuesta' in self.contexto_actual[id_usuario] and self.contexto_actual[id_usuario]['en_encuesta']:
            # Procesar respuesta de la encuesta
            respuesta = self.procesar_respuesta_encuesta(mensaje, id_usuario)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        
        # Verificar si estamos en proceso de recopilación de información para agente
        if 'recopilando_info_agente' in self.contexto_actual[id_usuario] and self.contexto_actual[id_usuario]['recopilando_info_agente']:
            respuesta = self.procesar_recopilacion_info_agente(mensaje, id_usuario)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        
        # Verificar si el mensaje es "agente" después de una encuesta negativa
        if mensaje.lower() == 'agente' and self.contexto_actual[id_usuario].get('encuesta_respondida', False):
            return self.iniciar_recopilacion_info_agente(id_usuario, tiempo_inicio)
        
        # Verificar si el mensaje indica que el usuario no necesita más ayuda
        if self.es_mensaje_despedida(mensaje):
            # Verificar si ya se ha enviado una encuesta anteriormente
            if not self.contexto_actual[id_usuario].get('encuesta_respondida', False):
                # Enviar la encuesta solo si no se ha respondido antes
                self.contexto_actual[id_usuario]['en_encuesta'] = True
                respuesta = "¿El problema o tu consulta fue resuelta? Responde Sí o No."
                self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
                return respuesta
            else:
                # Si ya se respondió, enviar un mensaje de despedida
                respuesta = "Gracias por usar nuestro servicio. ¡Que tengas un buen día!"
                self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
                return respuesta
        
        # Verificar si el mensaje es "agente" o solicita contacto con agente
        if mensaje.lower() == 'agente' or 'contactar' in mensaje.lower() or 'hablar con agente' in mensaje.lower():
            # Iniciar proceso de recopilación de información
            return self.iniciar_recopilacion_info_agente(id_usuario, tiempo_inicio)
        
        # Verificar si es un mensaje repetido
        ultimo_mensaje = None
        penultimo_mensaje = None
        if id_usuario in self.conversaciones and len(self.conversaciones[id_usuario]) >= 1:
            for msg in reversed(self.conversaciones[id_usuario]):
                if msg.get('tipo') == 'usuario':
                    if ultimo_mensaje is None:
                        ultimo_mensaje = msg.get('mensaje', '')
                    elif penultimo_mensaje is None:
                        penultimo_mensaje = msg.get('mensaje', '')
                        break
        
        # Si el mensaje actual es igual al último mensaje del usuario
        if ultimo_mensaje and mensaje.lower() == ultimo_mensaje.lower():
            # Verificar si también es igual al penúltimo mensaje (repetición múltiple)
            if penultimo_mensaje and mensaje.lower() == penultimo_mensaje.lower():
                # Detectar sistema y problema para dar una respuesta más específica
                sistema, problema, matricula = self.detectar_sistema_y_problema(mensaje)
                
                if sistema and problema:
                    # Si podemos detectar sistema y problema, dar una respuesta específica
                    respuesta = f"Veo que estás mencionando un problema con {sistema}. Para ayudarte mejor, necesito más detalles específicos sobre el problema '{problema}'. ¿Podrías proporcionar información adicional como mensajes de error, cuándo comenzó el problema o qué acciones has intentado?"
                else:
                    # Si no podemos detectar sistema y problema, dar una respuesta genérica
                    respuesta = "Parece que estás enviando el mismo mensaje varias veces. Para ayudarte mejor, necesito más detalles sobre tu consulta. ¿Podrías proporcionar más información o explicar tu problema de otra manera?"
                
                self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
                return respuesta
        
        # Guardar mensaje en historial
        self.conversaciones[id_usuario].append({
            'mensaje': mensaje,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': 'usuario'
        })
        
        # Variables para registro
        es_urgente = False
        derivado_agente = False
        respuesta_automatica = False
        
        # Comandos especiales - verificar primero
        mensaje_lower = mensaje.lower()
        
        # Verificar si el usuario quiere iniciar una nueva consulta
        if mensaje_lower in ['nueva consulta', 'nuevo problema', 'otra consulta', 'reiniciar']:
            self.reiniciar_conversacion(id_usuario)
            respuesta = "Entendido. ¿En qué puedo ayudarte con esta nueva consulta?"
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        
        # Resto de comandos especiales
        if mensaje_lower == 'ayuda':
            respuesta = self.mostrar_ayuda()
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        elif mensaje_lower == 'ejemplos':
            respuesta = self.mostrar_ejemplos()
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        elif mensaje_lower == 'urgente':
            es_urgente = True
            respuesta = "He marcado tu caso como urgente. Un agente de mantenimiento te contactará lo antes posible. Mientras tanto, ¿puedes proporcionar más detalles sobre el problema?"
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio, es_urgente=True)
            return respuesta
        
        # Detectar preguntas sobre reset
        if ('reset' in mensaje_lower or 'reinicio' in mensaje_lower or 'reiniciar' in mensaje_lower or 
            'como hago el reset' in mensaje_lower or 'cómo hago el reset' in mensaje_lower):
            
            # Detectar sistema mencionado en el mensaje
            sistema = None
            if 'apu' in mensaje_lower:
                sistema = 'APU'
            elif 'electrico' in mensaje_lower or 'eléctrico' in mensaje_lower:
                sistema = 'ELECTRICO'
            elif 'tren' in mensaje_lower or 'aterrizaje' in mensaje_lower:
                sistema = 'TREN'
            
            # Si no se detecta sistema en el mensaje, intentar obtenerlo del contexto
            if not sistema:
                contexto = self.obtener_contexto(id_usuario)
                sistema = contexto.get('sistema')
            
            respuesta = self.manejar_reset_sistema(id_usuario, sistema)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            
            # Determinar si debemos enviar la encuesta
            if not self.contexto_actual[id_usuario].get('encuesta_respondida', False):
                self.contexto_actual[id_usuario]['en_encuesta'] = True
                respuesta += "\n\n¿El problema o tu consulta fue resuelta? Responde Sí o No."
            
            return respuesta
        
        # Detectar sistema, problema y matrícula
            sistema, problema, matricula = self.detectar_sistema_y_problema(mensaje)
        
        # Caso especial para "APU no arranca"
        if (sistema == 'APU' and problema == 'NO_ARRANCA') or ('apu' in mensaje_lower and ('no arranca' in mensaje_lower or 'no enciende' in mensaje_lower)):
            # Obtener contexto actual
            contexto = self.obtener_contexto(id_usuario)
            
            # Actualizar contexto con la información detectada
            contexto['sistema'] = 'APU'
            contexto['problema'] = 'NO_ARRANCA'
            if matricula:
                contexto['matricula'] = matricula
            
            # Guardar contexto actualizado
            self.contexto_actual[id_usuario] = contexto
            
            # Si ya tenemos la matrícula, dar la solución completa
            if matricula or contexto.get('matricula'):
                matricula_final = matricula or contexto.get('matricula')
                
                respuesta = (f"Para solucionar el problema de APU que no arranca en {matricula_final}, verifica lo siguiente:\n\n"
                            f"1. Comprueba que el interruptor de control del APU esté en posición ON\n"
                            f"2. Verifica el nivel de combustible y que la válvula de combustible del APU esté abierta\n"
                            f"3. Revisa los breakers relacionados con el APU en el panel eléctrico\n"
                            f"4. Comprueba si hay mensajes de error específicos en la ECAM/EICAS\n"
                            f"5. Verifica que la temperatura exterior esté dentro de los límites operativos del APU\n\n"
                            f"Si después de estas verificaciones el APU sigue sin arrancar, podría ser necesario realizar un reset del sistema o contactar al equipo de mantenimiento para una inspección más detallada.")
            
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            
                # Determinar si debemos enviar la encuesta
                if not self.contexto_actual[id_usuario].get('encuesta_respondida', False):
                    self.contexto_actual[id_usuario]['en_encuesta'] = True
                    respuesta += "\n\n¿El problema o tu consulta fue resuelta? Responde Sí o No."
            
            return respuesta
            else:
                # Si no tenemos la matrícula, pedirla
                respuesta = "Detecto que el APU no arranca. ¿Podrías indicarme la matrícula de la aeronave?"
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        
        # Caso especial para "Tren de aterrizaje"
        if (sistema == 'TREN') or ('tren' in mensaje_lower and 'aterrizaje' in mensaje_lower):
            problema_tren = problema or 'REVISAR'  # Si no detectamos problema específico, asumir REVISAR
            respuesta = self.manejar_tren_aterrizaje(id_usuario, problema_tren, matricula)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            
            # Determinar si debemos enviar la encuesta
            if matricula and not self.contexto_actual[id_usuario].get('encuesta_respondida', False):
                self.contexto_actual[id_usuario]['en_encuesta'] = True
                respuesta += "\n\n¿El problema o tu consulta fue resuelta? Responde Sí o No."
            
            return respuesta
        
        # Caso especial para "Sistema eléctrico"
        if (sistema == 'ELECTRICO') or ('electrico' in mensaje_lower or 'eléctrico' in mensaje_lower):
            problema_elec = problema or 'REVISAR'  # Si no detectamos problema específico, asumir REVISAR
            respuesta = self.manejar_sistema_electrico(id_usuario, problema_elec, matricula)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            
            # Determinar si debemos enviar la encuesta
            if matricula and not self.contexto_actual[id_usuario].get('encuesta_respondida', False):
                self.contexto_actual[id_usuario]['en_encuesta'] = True
                respuesta += "\n\n¿El problema o tu consulta fue resuelta? Responde Sí o No."
            
            return respuesta
        
        # Manejar mensajes cortos o ambiguos
        if len(mensaje.strip()) <= 5:
            respuesta = self.manejar_mensaje_corto(mensaje, id_usuario)
            self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
            return respuesta
        
        # Detectar si hay un cambio de tema
        if self.detectar_cambio_tema(mensaje, id_usuario):
            # Reiniciar el contexto pero mantener el estado de la encuesta
            encuesta_respondida = self.contexto_actual[id_usuario].get('encuesta_respondida', False)
            self.contexto_actual[id_usuario] = {'encuesta_respondida': encuesta_respondida}
            print(f"Detectado cambio de tema para usuario {id_usuario}")
        
        # Al final, registrar la respuesta y el tiempo
        respuesta = self.procesar_mensaje_normal(mensaje, id_usuario, sistema, problema, matricula)
        self.registrar_respuesta(id_usuario, respuesta, tiempo_inicio)
        
        # Determinar si la conversación ha terminado y debemos enviar la encuesta
        # Condiciones para considerar que una conversación ha terminado:
        # 1. No es una solicitud de agente (porque eso derivaría a un humano)
        # 2. No es una consulta urgente (porque eso requiere seguimiento)
        # 3. No es un comando de ayuda o ejemplos (porque son informativos)
        # 4. La respuesta contiene una solución completa (verificamos por palabras clave)
        # 5. El usuario ha enviado al menos 2 mensajes (para evitar encuestas prematuras)
        
        conversacion_terminada = (
            not derivado_agente and 
            not es_urgente and 
            not mensaje_lower in ['ayuda', 'ejemplos'] and
            len(self.conversaciones.get(id_usuario, [])) >= 2 and
            self._es_respuesta_final(respuesta) and
            not self.contexto_actual[id_usuario].get('encuesta_respondida', False)  # No enviar si ya se respondió
        )
        
        if conversacion_terminada:
            # Añadir la encuesta al final de la respuesta
            self.contexto_actual[id_usuario]['en_encuesta'] = True
            respuesta += "\n\n¿El problema o tu consulta fue resuelta? Responde Sí o No."
        
        return respuesta

    def obtener_estadisticas(self):
        """Devuelve las estadísticas actuales"""
        return self.stats