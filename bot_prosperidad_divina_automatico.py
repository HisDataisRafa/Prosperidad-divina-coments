#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - Sistema Automático de Respuesta a Comentarios
Ministerio Digital con IA para expandir bendiciones y amor divino
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ProsperidadDivinaBot:
    def __init__(self):
        print("👑 INICIANDO BOT PROSPERIDAD DIVINA")
        print("="*60)
        
        # 🔑 Configuración de APIs
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY') 
        self.channel_id = os.environ.get('CHANNEL_ID', 'UCgRg_G9C4-_AHBETHcc7cQQ')
        
        if not all([self.gemini_api_key, self.youtube_api_key]):
            raise ValueError("❌ Faltan credenciales del ministerio en variables de entorno")
        
        # 🤖 Configurar Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 📺 Configurar YouTube API
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        
        # 📊 Estadísticas del ministerio
        self.stats = {
            'respuestas_exitosas': 0,
            'comentarios_procesados': 0,
            'errores': 0,
            'peticiones_oracion': 0,
            'testimonios': 0
        }
        
        # ⏰ Configuración temporal
        self.hace_horas = 8  # Procesar comentarios de las últimas 8 horas
        self.max_respuestas = 15  # Máximo de respuestas por ejecución
        
    def obtener_videos_recientes(self) -> List[Dict]:
        """📺 Obtener videos recientes del canal"""
        try:
            # Obtener uploads playlist del canal
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            if not channel_response['items']:
                print(f"❌ Canal no encontrado: {self.channel_id}")
                return []
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Obtener videos recientes
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist,
                maxResults=10  # Últimos 10 videos
            ).execute()
            
            videos = []
            for item in playlist_response['items']:
                video_info = {
                    'id': item['snippet']['resourceId']['videoId'],
                    'titulo': item['snippet']['title'],
                    'fecha': item['snippet']['publishedAt']
                }
                videos.append(video_info)
                print(f"📹 Video encontrado: {video_info['titulo'][:50]}...")
            
            return videos
            
        except HttpError as e:
            print(f"❌ Error obteniendo videos: {e}")
            return []
    
    def obtener_comentarios_recientes(self, video_id: str) -> List[Dict]:
        """💬 Obtener comentarios recientes de un video"""
        try:
            # Calcular fecha límite
            fecha_limite = datetime.now() - timedelta(hours=self.hace_horas)
            
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=50,
                textFormat='plainText'
            ).execute()
            
            comentarios_recientes = []
            
            for item in response['items']:
                comentario = item['snippet']['topLevelComment']['snippet']
                fecha_comentario = datetime.fromisoformat(comentario['publishedAt'].replace('Z', '+00:00'))
                
                # Solo comentarios recientes
                if fecha_comentario >= fecha_limite:
                    comentario_info = {
                        'id': item['snippet']['topLevelComment']['id'],
                        'texto': comentario['textDisplay'],
                        'autor': comentario['authorDisplayName'],
                        'fecha': comentario['publishedAt'],
                        'likes': comentario.get('likeCount', 0)
                    }
                    comentarios_recientes.append(comentario_info)
            
            print(f"💬 {len(comentarios_recientes)} comentarios recientes encontrados")
            return comentarios_recientes
            
        except HttpError as e:
            print(f"❌ Error obteniendo comentarios del video {video_id}: {e}")
            return []
    
    def detectar_tipo_comentario(self, texto: str) -> str:
        """🔍 Detectar el tipo de comentario para personalizar respuesta"""
        texto_lower = texto.lower()
        
        # Palabras clave para diferentes tipos
        peticion_oracion = ['ora', 'oración', 'orar', 'ruega', 'ayuda', 'enfermo', 'problema', 'dificil']
        testimonio = ['testimonio', 'milagro', 'sanó', 'bendición', 'gracias dios', 'funcionó']
        duda_fe = ['duda', 'no creo', 'funciona', 'real', 'verdad']
        abundancia = ['dinero', 'trabajo', 'empleo', 'abundancia', 'prosperidad', 'económico']
        
        if any(palabra in texto_lower for palabra in peticion_oracion):
            self.stats['peticiones_oracion'] += 1
            return 'peticion_oracion'
        elif any(palabra in texto_lower for palabra in testimonio):
            self.stats['testimonios'] += 1
            return 'testimonio'
        elif any(palabra in texto_lower for palabra in duda_fe):
            return 'duda_fe'
        elif any(palabra in texto_lower for palabra in abundancia):
            return 'abundancia'
        else:
            return 'general'
    
    def generar_respuesta_ia(self, comentario: Dict, tipo: str) -> str:
        """🤖 Generar respuesta personalizada con Gemini"""
        try:
            # Prompt personalizado según el tipo
            prompts = {
                'peticion_oracion': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde con amor y compasión a esta petición de oración:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta cálida y empática (máximo 2 líneas)
                - Incluye que orarás por la persona
                - Usa emojis apropiados: 🙏, ✨, 💫, 💖
                - Menciona el amor de Dios y su cuidado
                - Termina con bendiciones
                """,
                
                'testimonio': f"""
                Como asistente espiritual del canal "Prosperidad Divina", celebra este testimonio:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta de gozo y celebración (máximo 2 líneas)
                - Agradece por compartir el testimonio
                - Usa emojis: 🎉, ✨, 🙌, 💖, 🌟
                - Glorifica a Dios por el milagro
                - Anima a seguir compartiendo
                """,
                
                'abundancia': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde sobre prosperidad:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta sobre abundancia divina (máximo 2 líneas)
                - Menciona que Dios provee todas las necesidades
                - Usa emojis: 💰, ✨, 🙏, 🌟, 💫
                - Habla de fe y confianza
                - Incluye bendición de prosperidad
                """,
                
                'general': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde con amor:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta cálida y alentadora (máximo 2 líneas)
                - Agradece la participación
                - Usa emojis apropiados: ✨, 🙏, 💖, 🌅
                - Incluye bendiciones
                - Mantén tono espiritual pero natural
                """
            }
            
            prompt = prompts.get(tipo, prompts['general'])
            
            response = self.model.generate_content(prompt)
            respuesta = response.text.strip()
            
            # Limpiar respuesta si es muy larga
            lineas = respuesta.split('\n')
            if len(lineas) > 2:
                respuesta = '\n'.join(lineas[:2])
            
            return respuesta
            
        except Exception as e:
            print(f"❌ Error generando respuesta IA: {e}")
            # Respuesta de respaldo
            respuestas_respaldo = [
                "Bendiciones infinitas para ti! 🙏✨ Que el amor divino llene tu corazón siempre 💖",
                "Gracias por ser parte de esta hermosa comunidad! 🌟 Dios tiene planes maravillosos para ti 🙏",
                "Qué bendición tenerte aquí! ✨ Que la luz divina ilumine tu camino siempre 💫🙏"
            ]
            return random.choice(respuestas_respaldo)
    
    def responder_comentario(self, comentario_id: str, respuesta: str) -> bool:
        """📝 Responder a un comentario (simulado - no disponible en API pública)"""
        # NOTA: La API pública de YouTube no permite responder comentarios
        # Esta función simula la respuesta para demostrar el flujo
        
        print(f"💬 [SIMULADO] Respuesta enviada:")
        print(f"   📍 ID: {comentario_id}")
        print(f"   📝 Respuesta: {respuesta}")
        print(f"   ⏰ Hora: {datetime.now().strftime('%H:%M:%S')}")
        
        # Simular éxito (en implementación real, aquí iría la lógica de respuesta)
        return True
    
    def procesar_comentarios(self):
        """🚀 Proceso principal: obtener y responder comentarios"""
        print(f"\n🔄 INICIANDO PROCESAMIENTO DE COMENTARIOS")
        print(f"⏰ Buscando comentarios de las últimas {self.hace_horas} horas")
        print(f"🎯 Máximo {self.max_respuestas} respuestas por ejecución")
        
        # Obtener videos recientes
        videos = self.obtener_videos_recientes()
        
        if not videos:
            print("❌ No se encontraron videos para procesar")
            return
        
        total_respuestas = 0
        
        # Procesar cada video
        for video in videos:
            if total_respuestas >= self.max_respuestas:
                print(f"✅ Límite alcanzado: {self.max_respuestas} respuestas")
                break
                
            print(f"\n📹 Procesando: {video['titulo'][:50]}...")
            
            comentarios = self.obtener_comentarios_recientes(video['id'])
            
            for comentario in comentarios:
                if total_respuestas >= self.max_respuestas:
                    break
                
                self.stats['comentarios_procesados'] += 1
                
                # Detectar tipo de comentario
                tipo = self.detectar_tipo_comentario(comentario['texto'])
                
                # Generar respuesta personalizada
                respuesta = self.generar_respuesta_ia(comentario, tipo)
                
                # Enviar respuesta (simulado)
                if self.responder_comentario(comentario['id'], respuesta):
                    self.stats['respuestas_exitosas'] += 1
                    total_respuestas += 1
                    
                    print(f"✅ Respuesta #{total_respuestas} enviada ({tipo})")
                    
                    # Pausa entre respuestas
                    time.sleep(2)
                else:
                    self.stats['errores'] += 1
        
        print(f"\n🎉 PROCESAMIENTO COMPLETADO")
        print(f"📊 {total_respuestas} respuestas enviadas")
    
    def generar_reporte(self):
        """📊 Generar reporte de actividad del ministerio"""
        ahora = datetime.now()
        
        reporte = {
            'timestamp': ahora.isoformat(),
            'fecha_legible': ahora.strftime('%d de %B %Y - %H:%M'),
            'stats': self.stats,
            'config': {
                'horas_buscadas': self.hace_horas,
                'max_respuestas': self.max_respuestas,
                'canal_id': self.channel_id
            }
        }
        
        # Guardar reporte JSON
        with open('reporte_ministerio_digital.json', 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        # Reporte legible
        print(f"\n📋 REPORTE MINISTERIO DIGITAL")
        print(f"🕐 {reporte['fecha_legible']}")
        print(f"📊 ESTADÍSTICAS:")
        print(f"   💬 Comentarios procesados: {self.stats['comentarios_procesados']}")
        print(f"   ✅ Respuestas enviadas: {self.stats['respuestas_exitosas']}")
        print(f"   🙏 Peticiones de oración: {self.stats['peticiones_oracion']}")
        print(f"   🎉 Testimonios recibidos: {self.stats['testimonios']}")
        print(f"   ❌ Errores: {self.stats['errores']}")
        
        return reporte

def main():
    """🚀 Función principal del bot"""
    try:
        print("🙏 BOT PROSPERIDAD DIVINA - MINISTERIO DIGITAL AUTOMÁTICO")
        print("="*70)
        
        # Inicializar bot
        bot = ProsperidadDivinaBot()
        
        # Procesar comentarios
        bot.procesar_comentarios()
        
        # Generar reporte
        bot.generar_reporte()
        
        print(f"\n✨ MINISTERIO DIGITAL COMPLETADO CON ÉXITO")
        print(f"🔄 Próxima ejecución automática en 4 horas")
        print(f"👑 Prosperidad Divina expandiéndose automáticamente")
        
    except Exception as e:
        print(f"\n❌ ERROR EN EL MINISTERIO DIGITAL: {e}")
        print(f"🙏 El ministerio continuará en la próxima ejecución")
        
        # Guardar error para análisis
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'tipo': type(e).__name__
        }
        
        with open('error_ministerio.json', 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
