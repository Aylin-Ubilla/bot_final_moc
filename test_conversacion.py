from bot_simple import WhatsAppBot
import time

def test_conversacion_completa():
    bot = WhatsAppBot()
    
    # Simular una conversación completa
    user_id = "test_user_" + str(int(time.time()))
    
    # Primer mensaje - saludo
    print("\n--- INICIO DE CONVERSACIÓN ---")
    mensaje1 = "Hola, tengo un problema"
    print(f"Usuario: {mensaje1}")
    respuesta1 = bot.procesar_mensaje(mensaje1, user_id)
    print(f"Bot: {respuesta1}")
    
    # Segundo mensaje - problema específico
    mensaje2 = "El APU del CC-AWN no arranca"
    print(f"\nUsuario: {mensaje2}")
    respuesta2 = bot.procesar_mensaje(mensaje2, user_id)
    print(f"Bot: {respuesta2}")
    
    # Verificar si se envió la encuesta
    if "¿El problema o tu consulta fue resuelta?" in respuesta2:
        print("\n[Se envió la encuesta de satisfacción]")
        
        # Responder a la encuesta
        mensaje3 = "Sí"
        print(f"\nUsuario: {mensaje3}")
        respuesta3 = bot.procesar_mensaje(mensaje3, user_id)
        print(f"Bot: {respuesta3}")
    else:
        # Tercer mensaje - más detalles
        mensaje3 = "Además, muestra un mensaje de error"
        print(f"\nUsuario: {mensaje3}")
        respuesta3 = bot.procesar_mensaje(mensaje3, user_id)
        print(f"Bot: {respuesta3}")
        
        # Verificar si ahora se envió la encuesta
        if "¿El problema o tu consulta fue resuelta?" in respuesta3:
            print("\n[Se envió la encuesta de satisfacción]")
            
            # Responder a la encuesta
            mensaje4 = "Sí"
            print(f"\nUsuario: {mensaje4}")
            respuesta4 = bot.procesar_mensaje(mensaje4, user_id)
            print(f"Bot: {respuesta4}")
    
    # Verificar estadísticas
    stats = bot.obtener_estadisticas()
    print("\n--- ESTADÍSTICAS ---")
    print(f"Total conversaciones: {stats.get('total_conversaciones', 0)}")
    print(f"Total mensajes: {stats.get('total_mensajes', 0)}")
    print(f"Total encuestas: {stats.get('total_encuestas', 0)}")
    print(f"Consultas satisfactorias: {stats.get('consultas_satisfactorias', 0)}")

if __name__ == "__main__":
    test_conversacion_completa() 