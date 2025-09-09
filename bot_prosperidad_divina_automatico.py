#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN DE PRUEBA
Ministerio Digital con IA - MODO PRUEBA (5 comentarios máximo)
CHANNEL_ID: UCgRg_G9C4-_AHBETHcc7cQQ
"""

import os
import json
import time
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ProsperidadDivinaBotPrueba:
    def __init__(self):
        print("👑 INICIANDO BOT PROSPERIDAD DIVINA - MODO PRUEBA")
        print("="*70)
        print("🧪 CONFIGURACIÓN DE PRUEBA:")
        print("   📊 Máximo 5 respuestas")
        print("   ⏰ Comentarios de últimas 12 horas")
        print("   🔍 Análisis detallado paso a paso")
        print("="*70)
        
        # 🔑 Configuración de APIs
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials = os.environ.get('YOUTUBE_CREDENTIALS')
        
        if not all([self.gemini_api_key, self.youtube_credentials]):
            raise ValueError("❌ Faltan credenciales del ministerio en variables de entorno")
        
        # 🤖 Configurar Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 📺 Configurar YouTube con OAuth
        self.youtube = self.configurar_youtube_oauth()
        
        # 🆔 Channel ID confirmado
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'  # Prosperidad Divina
        
        # 📊 Estadísticas de la prueba
        self.stats = {
            'respuestas_exitosas': 0,
            'comentarios_procesados': 0,
            'errores': 0,
            'peticiones_oracion': 0,
            'testimonios': 0,
            'abundancia_respuestas': 0,
            'saludos': 0,
            'general': 0
        }
        
        # ⏰ Configuración para PRUEBA
        self.hace_horas = 12  # Más horas para encontrar comentarios
        self.max_respuestas = 5  # SOLO 5 para prueba
        
        # 📝 Log detallado
        self.log_detallado = []
        
        print(f"✅ Bot configurado para canal: {self.channel_id}")
        
    def configurar_youtube_oauth(self):
        """🔐 Configurar YouTube API con credenciales OAuth"""
        try:
            # Parsear credenciales JSON
            creds_data = json.loads(self.youtube_credentials)
            
            # Crear objeto de credenciales
            creds = Credentials.from_authorized_user_info(creds_data)
            
            # Crear servicio YouTube
            youtube = build('youtube', 'v3', credentials=creds)
            
            print("✅ Autenticación OAuth exitosa")
            return youtube
            
        except Exception as e:
            print(f"❌ Error configurando OAuth: {e}")
            raise
    
    def verificar_canal(self):
        """🔍 Verificar que podemos acceder al canal correcto"""
        try:
            print(f"\n🔍 VERIFICANDO ACCESO AL CANAL...")
            
            # Verificar canal por ID
            response = self.youtube.channels().list(
                part='id,snippet,statistics',
                id=self.channel_id
            ).execute()
            
            if response['items']:
                canal = response['items'][0]
                nombre = canal['snippet']['title']
                suscriptores = canal['statistics'].get('subscriberCount', 'N/A')
                videos = canal['statistics'].get('videoCount', 'N/A')
                
                print(f"✅ Canal encontrado: {nombre}")
                print(f"📊 Suscriptores: {suscriptores}")
                print(f"📹 Videos: {videos}")
                
                self.log_detallado.append({
                    'paso': 'verificacion_canal',
                    'resultado': 'exitoso',
                    'canal': nombre,
                    'suscriptores': suscriptores
                })
                
                return True
            else:
                print("❌ Canal no encontrado con ese ID")
                return False
                
        except HttpError as e:
            print(f"❌ Error verificando canal: {e}")
            return False
    
    def obtener_videos_recientes(self) -> List[Dict]:
        """📺 Obtener videos recientes del canal"""
        try:
            print(f"\n📺 OBTENIENDO VIDEOS RECIENTES...")
            
            # Obtener uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            uploads_playlist = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Obtener videos recientes
            playlist_response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist,
                maxResults=5  # Solo 5 videos para prueba
            ).execute()
            
            videos = []
            for i, item in enumerate(playlist_response['items'], 1):
                video_info = {
                    'id': item['snippet']['resourceId']['videoId'],
                    'titulo': item['snippet']['title'],
                    'fecha': item['snippet']['publishedAt']
                }
                videos.append(video_info)
                print(f"📹 Video {i}: {video_info['titulo'][:60]}...")
            
            print(f"✅ {len(videos)} videos encontrados para análisis")
            
            self.log_detallado.append({
                'paso': 'obtencion_videos',
                'resultado': 'exitoso',
                'cantidad': len(videos),
                'videos': [v['titulo'][:50] for v in videos]
            })
            
            return videos
            
        except HttpError as e:
            print(f"❌ Error obteniendo videos: {e}")
            return []
    
    def obtener_comentarios_recientes(self, video_id: str, titulo_video: str) -> List[Dict]:
        """💬 Obtener comentarios recientes de un video"""
        try:
            print(f"\n💬 ANALIZANDO COMENTARIOS DE: {titulo_video[:50]}...")
            
            # Calcular fecha límite con timezone UTC
            fecha_limite = datetime.now(timezone.utc) - timedelta(hours=self.hace_horas)
            print(f"⏰ Buscando comentarios desde: {fecha_limite.strftime('%Y-%m-%d %H:%M UTC')}")
            
            response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=20,  # Aumentado para encontrar comentarios recientes
                textFormat='plainText'
            ).execute()
            
            comentarios_recientes = []
            comentarios_totales = len(response.get('items', []))
            
            print(f"📊 {comentarios_totales} comentarios totales encontrados")
            
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
                        'likes': comentario.get('likeCount', 0),
                        'video_titulo': titulo_video
                    }
                    comentarios_recientes.append(comentario_info)
                    
                    # Mostrar comentario encontrado
                    print(f"   💭 {comentario_info['autor']}: {comentario_info['texto'][:70]}...")
            
            print(f"✅ {len(comentarios_recientes)} comentarios recientes (últimas {self.hace_horas}h)")
            
            self.log_detallado.append({
                'paso': f'comentarios_{video_id}',
                'video': titulo_video[:50],
                'comentarios_totales': comentarios_totales,
                'comentarios_recientes': len(comentarios_recientes),
                'fecha_limite': fecha_limite.isoformat()
            })
            
            return comentarios_recientes
            
        except HttpError as e:
            print(f"❌ Error obteniendo comentarios del video: {e}")
            return []
    
    def detectar_tipo_comentario(self, texto: str) -> str:
        """🔍 Detectar el tipo de comentario para personalizar respuesta"""
        texto_lower = texto.lower()
        
        # Palabras clave para diferentes tipos
        peticion_oracion = ['ora', 'oración', 'orar', 'ruega', 'ayuda', 'enfermo', 'problema', 'dificil', 'por favor', 'necesito']
        testimonio = ['testimonio', 'milagro', 'sanó', 'bendición', 'gracias dios', 'funcionó', 'gloria', 'aleluya']
        duda_fe = ['duda', 'no creo', 'funciona', 'real', 'verdad', 'fake', 'falso']
        abundancia = ['dinero', 'trabajo', 'empleo', 'abundancia', 'prosperidad', 'económico', 'plata', 'negocio']
        saludo = ['hola', 'bendiciones', 'saludos', 'buenas', 'amén', 'bendición']
        
        if any(palabra in texto_lower for palabra in peticion_oracion):
            self.stats['peticiones_oracion'] += 1
            return 'peticion_oracion'
        elif any(palabra in texto_lower for palabra in testimonio):
            self.stats['testimonios'] += 1
            return 'testimonio'
        elif any(palabra in texto_lower for palabra in duda_fe):
            return 'duda_fe'
        elif any(palabra in texto_lower for palabra in abundancia):
            self.stats['abundancia_respuestas'] += 1
            return 'abundancia'
        elif any(palabra in texto_lower for palabra in saludo):
            self.stats['saludos'] += 1
            return 'saludo'
        else:
            self.stats['general'] += 1
            return 'general'
    
    def generar_respuesta_ia(self, comentario: Dict, tipo: str) -> str:
        """🤖 Generar respuesta personalizada con Gemini"""
        try:
            print(f"🤖 Generando respuesta tipo '{tipo}' para: {comentario['texto'][:50]}...")
            
            # Prompts personalizados según el tipo
            prompts = {
                'peticion_oracion': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde con amor y compasión a esta petición de oración:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta cálida y empática (máximo 35 palabras)
                - Confirma que orarás por la persona
                - Usa emojis apropiados: 🙏, ✨, 💫, 💖
                - Menciona el amor de Dios
                - NO uses comillas ni asteriscos
                """,
                
                'testimonio': f"""
                Como asistente espiritual del canal "Prosperidad Divina", celebra este testimonio:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta de gozo y celebración (máximo 35 palabras)
                - Agradece por compartir
                - Usa emojis: 🎉, ✨, 🙌, 💖, 🌟
                - Glorifica a Dios por el milagro
                - NO uses comillas ni asteriscos
                """,
                
                'abundancia': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde sobre prosperidad:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta sobre abundancia divina (máximo 35 palabras)
                - Menciona que Dios provee
                - Usa emojis: 💰, ✨, 🙏, 🌟, 💫
                - Habla de fe y confianza
                - NO uses comillas ni asteriscos
                """,
                
                'saludo': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde al saludo:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Saludo cálido y bendición (máximo 25 palabras)
                - Agradece por ser parte de la comunidad
                - Usa emojis: ✨, 🙏, 💖, 🌅
                - Incluye bendiciones
                - NO uses comillas ni asteriscos
                """,
                
                'general': f"""
                Como asistente espiritual del canal "Prosperidad Divina", responde con amor:
                
                "{comentario['texto']}"
                
                INSTRUCCIONES:
                - Respuesta cálida y alentadora (máximo 35 palabras)
                - Agradece la participación
                - Usa emojis apropiados: ✨, 🙏, 💖, 🌅
                - Incluye bendiciones
                - NO uses comillas ni asteriscos
                """
            }
            
            prompt = prompts.get(tipo, prompts['general'])
            
            response = self.model.generate_content(prompt)
            respuesta = response.text.strip()
            
            # Limpiar respuesta de comillas y asteriscos
            respuesta = respuesta.replace('"', '').replace("'", '').replace('*', '')
            
            # Limitar longitud
            if len(respuesta) > 180:
                respuesta = respuesta[:177] + "..."
            
            print(f"✅ Respuesta generada: {respuesta}")
            
            return respuesta
            
        except Exception as e:
            print(f"❌ Error generando respuesta IA: {e}")
            # Respuestas de respaldo según tipo
            respuestas_respaldo = {
                'peticion_oracion': "Estaré orando por ti 🙏✨ Dios te ama y tiene cuidado de ti siempre 💖",
                'testimonio': "¡Gloria a Dios! 🎉 Qué bendición leer tu testimonio ✨ Gracias por compartir 🙏",
                'abundancia': "Dios es tu proveedor 💰✨ Confía en su perfecta provisión para tu vida 🙏",
                'saludo': "Bendiciones abundantes para ti ✨🙏 Gracias por ser parte de esta hermosa familia 💖",
                'general': "Bendiciones infinitas para ti! 🙏✨ Que el amor divino llene tu corazón siempre 💖"
            }
            return respuestas_respaldo.get(tipo, respuestas_respaldo['general'])
    
    def responder_comentario(self, comentario_id: str, respuesta: str, comentario_original: Dict) -> bool:
        """📝 Responder a un comentario REALMENTE"""
        try:
            print(f"\n📝 ENVIANDO RESPUESTA...")
            print(f"   👤 Autor: {comentario_original['autor']}")
            print(f"   💬 Comentario: {comentario_original['texto'][:80]}...")
            print(f"   📝 Respuesta: {respuesta}")
            
            # Preparar datos de la respuesta
            respuesta_data = {
                'snippet': {
                    'parentId': comentario_id,
                    'textOriginal': respuesta
                }
            }
            
            # Enviar respuesta usando la API
            response = self.youtube.comments().insert(
                part='snippet',
                body=respuesta_data
            ).execute()
            
            print(f"✅ RESPUESTA ENVIADA EXITOSAMENTE")
            print(f"   🆔 Comment ID: {response.get('id', 'N/A')}")
            
            # Agregar a log detallado
            self.log_detallado.append({
                'paso': 'respuesta_enviada',
                'autor': comentario_original['autor'],
                'comentario_original': comentario_original['texto'][:100],
                'respuesta_enviada': respuesta,
                'comment_id': response.get('id'),
                'timestamp': datetime.now().isoformat()
            })
            
            return True
            
        except HttpError as e:
            error_details = e.content.decode('utf-8') if hasattr(e, 'content') else str(e)
            print(f"❌ ERROR ENVIANDO RESPUESTA: {error_details}")
            self.stats['errores'] += 1
            
            # Agregar error a log
            self.log_detallado.append({
                'paso': 'error_respuesta',
                'autor': comentario_original['autor'],
                'error': error_details,
                'timestamp': datetime.now().isoformat()
            })
            
            return False
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {e}")
            self.stats['errores'] += 1
            return False
    
    def procesar_comentarios(self):
        """🚀 Proceso principal: obtener y responder comentarios - MODO PRUEBA"""
        print(f"\n🔄 INICIANDO PROCESAMIENTO EN MODO PRUEBA")
        print(f"⏰ Buscando comentarios de las últimas {self.hace_horas} horas")
        print(f"🎯 MÁXIMO {self.max_respuestas} respuestas (MODO PRUEBA)")
        print(f"📺 Canal: {self.channel_id}")
        
        # Verificar acceso al canal
        if not self.verificar_canal():
            print("❌ No se pudo verificar acceso al canal")
            return
        
        # Obtener videos recientes
        videos = self.obtener_videos_recientes()
        
        if not videos:
            print("❌ No se encontraron videos para procesar")
            return
        
        total_respuestas = 0
        
        # Procesar cada video
        for video in videos:
            if total_respuestas >= self.max_respuestas:
                print(f"✅ LÍMITE DE PRUEBA ALCANZADO: {self.max_respuestas} respuestas")
                break
                
            comentarios = self.obtener_comentarios_recientes(video['id'], video['titulo'])
            
            for comentario in comentarios:
                if total_respuestas >= self.max_respuestas:
                    break
                
                self.stats['comentarios_procesados'] += 1
                
                print(f"\n" + "="*80)
                print(f"📝 PROCESANDO COMENTARIO #{total_respuestas + 1}")
                print(f"👤 Autor: {comentario['autor']}")
                print(f"📹 Video: {comentario['video_titulo'][:50]}...")
                print(f"💬 Comentario: {comentario['texto']}")
                
                # Detectar tipo de comentario
                tipo = self.detectar_tipo_comentario(comentario['texto'])
                print(f"🔍 Tipo detectado: {tipo.upper()}")
                
                # Generar respuesta personalizada
                respuesta = self.generar_respuesta_ia(comentario, tipo)
                
                # Enviar respuesta REAL
                if self.responder_comentario(comentario['id'], respuesta, comentario):
                    self.stats['respuestas_exitosas'] += 1
                    total_respuestas += 1
                    
                    print(f"✅ RESPUESTA #{total_respuestas} ENVIADA EXITOSAMENTE")
                    
                    # Pausa entre respuestas para evitar rate limiting
                    if total_respuestas < self.max_respuestas:
                        print(f"⏸️  Pausa de 3 segundos antes del siguiente comentario...")
                        time.sleep(3)
                else:
                    print("❌ NO SE PUDO ENVIAR RESPUESTA")
                    
                print("="*80)
        
        print(f"\n🎉 PRUEBA COMPLETADA")
        print(f"📊 {total_respuestas} respuestas enviadas exitosamente")
    
    def generar_reporte_prueba(self):
        """📊 Generar reporte detallado de la prueba"""
        ahora = datetime.now()
        
        reporte = {
            'timestamp': ahora.isoformat(),
            'fecha_legible': ahora.strftime('%d de %B %Y - %H:%M'),
            'channel_id': self.channel_id,
            'modo': 'PRUEBA_5_COMENTARIOS',
            'stats': self.stats,
            'config': {
                'horas_buscadas': self.hace_horas,
                'max_respuestas': self.max_respuestas,
                'tipo': 'RESPUESTAS_REALES_OAUTH'
            },
            'log_detallado': self.log_detallado
        }
        
        # Guardar reporte JSON
        with open('reporte_prueba_ministerio.json', 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        # Reporte legible
        print(f"\n📋 REPORTE DETALLADO DE PRUEBA")
        print(f"🕐 {reporte['fecha_legible']}")
        print(f"📺 Canal: {self.channel_id}")
        print(f"🧪 Modo: PRUEBA (máximo {self.max_respuestas} respuestas)")
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   💬 Comentarios procesados: {self.stats['comentarios_procesados']}")
        print(f"   ✅ Respuestas enviadas: {self.stats['respuestas_exitosas']}")
        print(f"   🙏 Peticiones de oración: {self.stats['peticiones_oracion']}")
        print(f"   🎉 Testimonios: {self.stats['testimonios']}")
        print(f"   💰 Abundancia: {self.stats['abundancia_respuestas']}")
        print(f"   👋 Saludos: {self.stats['saludos']}")
        print(f"   📝 General: {self.stats['general']}")
        print(f"   ❌ Errores: {self.stats['errores']}")
        
        print(f"\n📁 Reporte detallado guardado en: reporte_prueba_ministerio.json")
        
        return reporte

def main():
    """🚀 Función principal del bot - MODO PRUEBA"""
    try:
        print("🙏 BOT PROSPERIDAD DIVINA - MODO PRUEBA")
        print("="*70)
        print("🧪 CONFIGURACIÓN ESPECIAL DE PRUEBA:")
        print("   📊 Máximo 5 respuestas")
        print("   🔍 Análisis detallado paso a paso")
        print("   📝 Log completo de cada acción")
        print("   🔥 Respuestas REALES con OAuth")
        print("="*70)
        
        # Inicializar bot
        bot = ProsperidadDivinaBotPrueba()
        
        # Procesar comentarios
        bot.procesar_comentarios()
        
        # Generar reporte
        bot.generar_reporte_prueba()
        
        print(f"\n✨ PRUEBA COMPLETADA CON ÉXITO")
        print(f"🔍 Revisa el reporte detallado para ver todos los pasos")
        print(f"👑 Prosperidad Divina - Ministerio Digital Activo")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {e}")
        print(f"🔍 Revisa la configuración de credenciales")
        
        # Guardar error para análisis
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'tipo': type(e).__name__,
            'modo': 'PRUEBA'
        }
        
        with open('error_prueba.json', 'w', encoding='utf-8') as f:
            json.dump(error_info, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
