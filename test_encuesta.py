from bot_simple import WhatsAppBot

def test_encuesta():
    bot = WhatsAppBot()
    
    # Simular una conversación
    user_id = "test_user"
    
    # Primer mensaje del usuario
    respuesta1 = bot.procesar_mensaje("Problema con APU", user_id)
    print(f"Usuario: Problema con APU")
    print(f"Bot: {respuesta1}")
    
    # Respuesta a la encuesta
    respuesta2 = bot.procesar_mensaje("Sí", user_id)
    print(f"Usuario: Sí")
    print(f"Bot: {respuesta2}")
    
    # Verificar estadísticas
    stats = bot.obtener_estadisticas()
    print("\nEstadísticas:")
    print(f"Total encuestas: {stats.get('total_encuestas', 0)}")
    print(f"Consultas satisfactorias: {stats.get('consultas_satisfactorias', 0)}")

if __name__ == "__main__":
    test_encuesta() 