import os
from bot_simple import WhatsAppBot

def main():
    # Create bot instance
    bot = WhatsAppBot()
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    print("WhatsAppBot de Mantenimiento MOC iniciado.")
    print("Escribe 'salir' para terminar la conversación.")
    print("Escribe 'ayuda' para ver comandos disponibles.")
    print("-" * 50)
    
    user_id = "local_user"  # ID for local testing
    
    while True:
        # Get user input
        user_message = input("\nTú: ")
        
        # Check if user wants to exit
        if user_message.lower() in ['salir', 'exit', 'quit']:
            print("\nBot: Gracias por usar el WhatsAppBot de Mantenimiento MOC. ¡Hasta pronto!")
            break
        
        # Process message and get response
        response = bot.procesar_mensaje(user_message, user_id)
        
        # Display bot response
        print(f"\nBot: {response}")
        
        # Optional: Display stats after each interaction
        if user_message.lower() == 'stats':
            stats = bot.obtener_estadisticas()
            print("\n--- ESTADÍSTICAS ---")
            print(f"Total conversaciones: {stats['total_conversaciones']}")
            print(f"Total mensajes: {stats['total_mensajes']}")
            print(f"Tiempo respuesta promedio: {stats['tiempo_respuesta_promedio']:.3f} segundos")
            print(f"Consultas urgentes: {stats['consultas_urgentes']}")
            print(f"Derivaciones a agente: {stats['derivaciones_agente']}")
            print(f"Respuestas automáticas: {stats['respuestas_automaticas']}")
            print("--- SISTEMAS ---")
            for sistema, count in stats['consultas_por_sistema'].items():
                print(f"  {sistema}: {count}")
            print("--- PROBLEMAS ---")
            for problema, count in stats['consultas_por_problema'].items():
                print(f"  {problema}: {count}")
            print("-" * 50)

if __name__ == "__main__":
    main() 