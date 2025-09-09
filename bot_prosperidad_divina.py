#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - PRUEBA ULTRA CONSERVADORA
Fecha: 08 de Septiembre de 2025

🐌 CONFIGURACIÓN ULTRA CONSERVADORA:
- ✅ Solo 5 comentarios para prueba rápida
- ✅ 10 segundos entre requests (6 RPM máximo)
- ✅ Diagnóstico completo de APIs
- ✅ Manejo robusto de todos los errores posibles
"""

import os
import re
import json
import time
import traceback
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set

import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ProsperidadDivina_PruebaConservadora:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*80)
        print(f"🐌 BOT PROSPERIDAD DIVINA - PRUEBA ULTRA CONSERVADORA")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. VERIFICACIÓN DETALLADA DE CREDENCIALES ---
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A"
        
        print(f"🔑 Diagnóstico de credenciales:")
        if self.gemini_api_key:
            print(f"   ✅ Gemini API Key: Presente (longitud: {len(self.gemini_api_key)} caracteres)")
            print(f"   🔍 Primeros 10 chars: {self.gemini_api_key[:10]}...")
        else:
            print(f"   ❌ Gemini API Key: FALTANTE")
            
        if self.youtube_credentials_comments:
            print(f"   ✅ YouTube OAuth: Presente (longitud: {len(self.youtube_credentials_comments)} caracteres)")
        else:
            print(f"   ❌ YouTube OAuth: FALTANTE")
        
        if not all([self.gemini_api_key, self.youtube_credentials_comments]):
            raise ValueError("❌ ERROR CRÍTICO: Faltan credenciales en las variables de entorno.")

        # --- 2. PARÁMETROS ULTRA CONSERVADORES ---
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.max_respuestas_por_ejecucion = 5  # 🐌 ULTRA CONSERVADOR: Solo 5 comentarios
        self.rate_limit_seconds = 10  # 🐌 ULTRA CONSERVADOR: 10 segundos = 6 RPM máximo
        self.timeout_gemini = 30  # 30 segundos timeout para Gemini

        # --- 3. INICIALIZACIÓN CON DIAGNÓSTICO ---
        self.model = self.configurar_gemini_con_diagnostico()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # --- 4. PERSISTENCIA ---
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"\n🎯 CONFIGURACIÓN DE PRUEBA:")
        print(f"   📝 Máximo comentarios: {self.max_respuestas_por_ejecucion}")
        print(f"   ⏱️  Rate limiting: {self.rate_limit_seconds}s entre requests")
        print(f"   🔢 RPM teórico: {90/self.rate_limit_seconds:.1f} requests/minuto")
        print(f"   📊 BD actual: {len(self.comentarios_ya_respondidos)} comentarios respondidos")
        print(f"   🧠 Memoria: {len(self.memoria_conversacion_usuario)} usuarios")
        print("="*80)

    def configurar_gemini_con_diagnostico(self) -> genai.GenerativeModel:
        """Configuración de Gemini con diagnóstico completo"""
        try:
            print("\n🤖 CONFIGURANDO GEMINI AI CON DIAGNÓSTICO COMPLETO...")
            
            # Paso 1: Configurar API key
            print("   🔧 Paso 1: Configurando API key...")
            genai.configure(api_key=self.gemini_api_key)
            print("   ✅ API key configurada")
            
            # Paso 2: Crear modelo
            print("   🔧 Paso 2: Creando modelo Gemini-1.5-Flash...")
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("   ✅ Modelo creado")
            
            # Paso 3: Prueba básica de conexión
            print("   🧪 Paso 3: Realizando prueba básica de conexión...")
            
            print(f"   ⏳ Aplicando rate limit inicial ({self.rate_limit_seconds}s)...")
            time.sleep(self.rate_limit_seconds)
            
            test_response = model.generate_content(
                "Responde exactamente: 'Prueba exitosa 2025'",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=50
                )
            )
            
            respuesta_prueba = test_response.text.strip()
            print(f"   ✅ Respuesta de prueba recibida: '{respuesta_prueba}'")
            
            if "prueba exitosa" in respuesta_prueba.lower():
                print("   🎉 GEMINI FUNCIONANDO PERFECTAMENTE")
            else:
                print("   ⚠️  Gemini responde, pero formato inesperado")
                
            return model
            
        except Exception as e:
            print(f"   ❌ ERROR EN CONFIGURACIÓN DE GEMINI:")
            print(f"   🔍 Tipo: {type(e).__name__}")
            print(f"   📝 Mensaje: {str(e)}")
            print(f"   📋 Traceback:")
            print("   " + "\n   ".join(traceback.format_exc().split('\n')[:5]))
            raise

    def configurar_youtube_lectura(self):
        try:
            print("\n📖 CONFIGURANDO YOUTUBE API PARA LECTURA...")
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ API de Lectura configurada")
            return youtube
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise

    def configurar_youtube_oauth(self):
        try:
            print("\n📝 CONFIGURANDO YOUTUBE OAUTH PARA ESCRITURA...")
            creds_data = json.loads(self.youtube_credentials_comments)
            creds = Credentials.from_authorized_user_info(creds_data)
            youtube = build('youtube', 'v3', credentials=creds)
            print("   ✅ OAuth configurado")
            return youtube
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise

    def cargar_db_respondidos(self) -> Set[str]:
        if not os.path.exists(self.db_respondidos_path):
            print(f"📁 Creando nuevo archivo: {self.db_respondidos_path}")
            return set()
        try:
            with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
                comentarios = {line.strip() for line in f if line.strip()}
            print(f"📁 Cargados {len(comentarios)} comentarios ya respondidos")
            return comentarios
        except Exception as e:
            print(f"⚠️  Error leyendo BD: {e}")
            return set()

    def guardar_en_db_respondidos(self, comment_id: str):
        try:
            with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
                f.write(f"{comment_id}\n")
            self.comentarios_ya_respondidos.add(comment_id)
        except Exception as e:
            print(f"⚠️  Error guardando ID: {e}")

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
        if not os.path.exists(self.db_conversaciones_path):
            print(f"🧠 Creando nueva memoria: {self.db_conversaciones_path}")
            return {}
        
        try:
            with open(self.db_conversaciones_path, 'r', encoding='utf-8') as f:
                memoria = json.load(f)
            print(f"🧠 Cargada memoria de {len(memoria)} usuarios")
            return memoria
        except Exception as e:
            print(f"⚠️  Error cargando memoria: {e}")
            return {}

    def guardar_memoria_conversaciones(self):
        try:
            with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
                json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando memoria: {e}")

    def obtener_videos_recientes(self) -> List[Dict]:
        try:
            print("\n📹 OBTENIENDO VIDEOS RECIENTES...")
            channel_response = self.youtube_lectura.channels().list(
                part='contentDetails', 
                id=self.channel_id
            ).execute()
            
            if not channel_response.get('items'):
                print("   ❌ Canal no encontrado")
                return []
                
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            playlist_items = self.youtube_lectura.playlistItems().list(
                part='snippet', 
                playlistId=uploads_id, 
                maxResults=10  # Solo 10 videos para prueba
            ).execute()
            
            videos = []
            for item in playlist_items.get('items', []):
                video = {
                    'id': item['snippet']['resourceId']['videoId'],
                    'titulo': item['snippet']['title'][:50] + '...' if len(item['snippet']['title']) > 50 else item['snippet']['title']
                }
                videos.append(video)
            
            print(f"   ✅ {len(videos)} videos encontrados")
            return videos
            
        except Exception as e:
            print(f"   ❌ Error obteniendo videos: {e}")
            return []
    
    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
        comentarios_nuevos = []
        try:
            print(f"   🔍 Buscando comentarios en: '{video_titulo}'")
            
            response = self.youtube_lectura.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=50,  # Reducido para prueba
                textFormat='plainText'
            ).execute()
            
            total_comentarios = len(response.get('items', []))
            print(f"      📊 {total_comentarios} comentarios encontrados en total")
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                
                # Verificar si ya respondimos
                if comment_id in self.comentarios_ya_respondidos:
                    continue
                
                # Verificar si ya tiene respuestas
                total_replies = item['snippet']['totalReplyCount']
                if total_replies > 0:
                    print(f"      ⏭️  Omitiendo comentario con {total_replies} respuesta(s)")
                    self.guardar_en_db_respondidos(comment_id)
                    self.stats['resumen']['comentarios_ya_respondidos_manualmente'] += 1
                    continue

                snippet = item['snippet']['topLevelComment']['snippet']
                
                # ID del autor más robusto
                autor_id = snippet.get('authorChannelId', {}).get('value') or f"anon_{hash(snippet['authorDisplayName']) % 10000}"
                
                comentario = {
                    'id': comment_id,
                    'texto': snippet['textDisplay'],
                    'autor_nombre': snippet['authorDisplayName'],
                    'autor_id': autor_id,
                    'video_titulo': video_titulo,
                    'fecha': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                }
                comentarios_nuevos.append(comentario)
            
            print(f"      ✅ {len(comentarios_nuevos)} comentarios nuevos sin respuesta")
            return comentarios_nuevos
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []

    def es_comentario_valido(self, texto: str) -> bool:
        """Validación simple pero efectiva"""
        if not texto or len(texto.strip()) < 3:
            return False
        if len(texto) > 500:  # Más restrictivo
            return False
        if re.search(r'http[s]?://', texto, re.IGNORECASE):
            return False
        return True

    def detectar_tipo_comentario(self, texto: str) -> str:
        """Detección simple de tipos"""
        texto_lower = texto.lower()
        
        if any(word in texto_lower for word in ['no aguanto', 'suicidio', 'morir']):
            return 'crisis'
        
        if len(texto.split()) <= 3:
            return 'saludo'
            
        if any(word in texto_lower for word in ['dinero', 'trabajo', 'prosperidad', 'abundancia']):
            return 'abundancia'
            
        if any(word in texto_lower for word in ['dolor', 'triste', 'sufro', 'lloro']):
            return 'dolor_confusion'
            
        if any(word in texto_lower for word in ['mentira', 'falso', 'no creo']):
            return 'duda_hostilidad'
            
        return 'general'

    def generar_respuesta_gemini_segura(self, comentario_actual: str, contexto_previo: List[str], 
                                      tipo: str, info_comentario: Dict) -> str:
        """Generador de respuestas con máxima seguridad"""
        
        if tipo == 'crisis':
            print(f"      🚫 Crisis detectada - ignorando por seguridad")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None

        try:
            # Prompt super simple para evitar problemas
            prompt = f"""Eres un asistente espiritual cálido del canal "Prosperidad Divina".

Usuario: {info_comentario['autor_nombre']}
Comentario: "{comentario_actual}"

Responde con 1-2 líneas máximo, con emojis espirituales, siendo empático y positivo."""

            print(f"      🧠 Enviando a Gemini (tipo: {tipo})")
            print(f"      ⏳ Rate limiting: {self.rate_limit_seconds}s...")
            
            # RATE LIMIT ULTRA CONSERVADOR
            time.sleep(self.rate_limit_seconds)
            
            # Llamada con configuración mínima
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=100
                )
            )
            
            if not response or not response.text:
                raise ValueError("Respuesta vacía de Gemini")
            
            respuesta = response.text.strip()[:200]  # Limitar longitud
            
            print(f"      ✅ Gemini respondió: \"{respuesta[:90]}...\"")
            self.stats['resumen']['respuestas_ia_exitosas'] += 1
            
            return respuesta
            
        except Exception as e:
            print(f"      ❌ Error en Gemini: {type(e).__name__} - {str(e)[:100]}...")
            self.stats['resumen']['errores_gemini'] += 1
            
            # Fallback ultra simple
            fallbacks = {
                'saludo': "Bendiciones de luz en tu camino ✨🙏",
                'abundancia': "Que la prosperidad divina florezca en tu vida 💰✨🙏",
                'dolor_confusion': "Que la paz divina sane tu corazón 💙✨🙏",
                'duda_hostilidad': "Respetamos tu perspectiva. Bendiciones 🕊️🙏",
                'general': "Que la luz divina te acompañe siempre ✨🙏"
            }
            
            fallback = fallbacks.get(tipo, fallbacks['general'])
            print(f"      🔄 Usando fallback: \"{fallback}\"")
            return fallback

    def responder_comentario_seguro(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        """Respuesta con manejo ultra seguro"""
        try:
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={'snippet': {'parentId': comentario_id, 'textOriginal': respuesta}}
            ).execute()
            
            print(f"      ✅ Respuesta enviada a '{autor_nombre}'")
            self.guardar_en_db_respondidos(comentario_id)
            return True
            
        except HttpError as e:
            error_msg = e.content.decode('utf-8') if e.content else str(e)
            print(f"      ❌ Error HTTP: {error_msg[:150]}...")
            self.stats['resumen']['errores_youtube'] += 1
            return False
        except Exception as e:
            print(f"      ❌ Error inesperado: {e}")
            self.stats['resumen']['errores_youtube'] += 1
            return False

    def inicializar_estadisticas(self):
        return {
            'info_ejecucion': {
                'id': self.run_id,
                'inicio': datetime.now().isoformat(),
                'fin': None,
                'modo': 'PRUEBA_ULTRA_CONSERVADORA_5_COMENTARIOS',
                'rate_limit': f"{self.rate_limit_seconds}s",
                'rpm_teorico': round(90/self.rate_limit_seconds, 1)
            },
            'resumen': {
                'comentarios_procesados': 0,
                'respuestas_exitosas': 0,
                'respuestas_ia_exitosas': 0,
                'errores_gemini': 0,
                'errores_youtube': 0,
                'comentarios_filtrados': 0,
                'comentarios_ya_respondidos_manualmente': 0
            },
            'tipos_procesados': {
                'saludo': 0, 'abundancia': 0, 'dolor_confusion': 0,
                'duda_hostilidad': 0, 'general': 0
            },
            'acciones_de_moderacion': {
                'crisis_ignorada': 0
            }
        }

    def ejecutar_prueba_conservadora(self):
        print(f"\n🚀 INICIANDO PRUEBA ULTRA CONSERVADORA")
        print(f"🎯 Objetivo: {self.max_respuestas_por_ejecucion} respuestas máximo")
        print(f"⏱️  Rate: {self.rate_limit_seconds}s entre requests")
        
        inicio = datetime.now()
        respuestas_enviadas = 0
        
        videos = self.obtener_videos_recientes()
        if not videos:
            print("❌ No se pudieron obtener videos")
            return
        
        for video_idx, video in enumerate(videos[:3]):  # Solo 3 videos máximo
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
                
            print(f"\n📹 VIDEO {video_idx + 1}/3: {video['titulo']}")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            if not comentarios:
                continue
            
            # Ordenar por fecha (más recientes primero)
            comentarios.sort(key=lambda x: x['fecha'], reverse=True)
            
            for comentario in comentarios[:10]:  # Máximo 10 por video
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                # Validar comentario
                if not self.es_comentario_valido(comentario['texto']):
                    print(f"   ⏭️  Comentario inválido de '{comentario['autor_nombre']}'")
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue
                
                print(f"\n   💬 PROCESANDO #{respuestas_enviadas + 1}:")
                print(f"   👤 Usuario: {comentario['autor_nombre']}")
                print(f"   📝 Texto: \"{comentario['texto'][:80]}...\"")
                
                # Detectar tipo
                tipo = self.detectar_tipo_comentario(comentario['texto'])
                print(f"   🏷️  Tipo detectado: {tipo}")
                
                # Generar respuesta
                respuesta = self.generar_respuesta_gemini_segura(
                    comentario['texto'], [], tipo, comentario
                )
                
                if not respuesta:
                    continue
                
                # Enviar respuesta
                if self.responder_comentario_seguro(
                    comentario['id'], respuesta, comentario['autor_nombre']
                ):
                    respuestas_enviadas += 1
                    self.stats['resumen']['respuestas_exitosas'] += 1
                    self.stats['tipos_procesados'][tipo] += 1
                    
                    print(f"   🎉 ÉXITO {respuestas_enviadas}/{self.max_respuestas_por_ejecucion}")
        
        # Guardar memoria
        self.guardar_memoria_conversaciones()
        
        # Reporte final
        duracion = (datetime.now() - inicio).total_seconds()
        self.generar_reporte_final(duracion)

    def generar_reporte_final(self, duracion_segundos: float):
        """Reporte final detallado"""
        
        self.stats['info_ejecucion']['fin'] = datetime.now().isoformat()
        self.stats['info_ejecucion']['duracion_segundos'] = round(duracion_segundos, 2)
        
        # Guardar reporte
        nombre_reporte = f"reporte_prueba_conservadora_{self.run_id}.json"
        with open(nombre_reporte, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("📊 REPORTE FINAL - PRUEBA ULTRA CONSERVADORA")
        print("="*80)
        print(f"🆔 ID: {self.run_id}")
        print(f"⏱️  Duración: {duracion_segundos:.1f}s ({duracion_segundos/90:.1f} minutos)")
        print(f"📁 Reporte: {nombre_reporte}")
        
        print(f"\n--- RESULTADOS ---")
        print(f"   📝 Comentarios procesados: {self.stats['resumen']['comentarios_procesados']}")
        print(f"   ✅ Respuestas enviadas: {self.stats['resumen']['respuestas_exitosas']}")
        print(f"   🤖 Respuestas de IA: {self.stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   🔄 Respuestas fallback: {self.stats['resumen']['respuestas_exitosas'] - self.stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   🚫 Filtrados: {self.stats['resumen']['comentarios_filtrados']}")
        print(f"   👤 Ya respondidos: {self.stats['resumen']['comentarios_ya_respondidos_manualmente']}")
        
        print(f"\n--- ERRORES ---")
        print(f"   🤖 Errores Gemini: {self.stats['resumen']['errores_gemini']}")
        print(f"   📺 Errores YouTube: {self.stats['resumen']['errores_youtube']}")
        print(f"   🚫 Crisis ignoradas: {self.stats['acciones_de_moderacion']['crisis_ignorada']}")
        
        # Diagnóstico
        if self.stats['resumen']['respuestas_ia_exitosas'] > 0:
            print(f"\n🎉 ¡GEMINI FUNCIONANDO PERFECTO!")
            print(f"   💡 Puedes aumentar el rate limiting gradualmente")
            print(f"   🚀 Listo para prueba con más comentarios")
        elif self.stats['resumen']['respuestas_exitosas'] > 0:
            print(f"\n⚠️  GEMINI CON PROBLEMAS - Solo fallbacks")
            print(f"   🔧 Revisar: API key, cuotas, conectividad")
        else:
            print(f"\n❌ NO SE ENVIARON RESPUESTAS")
            print(f"   🔍 Revisar configuración completa")
        
        print("="*80)

if __name__ == "__main__":
    try:
        bot = ProsperidadDivina_PruebaConservadora()
        bot.ejecutar_prueba_conservadora()
    except KeyboardInterrupt:
        print("\n⏹️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print("\nTraceback completo:")
        print(traceback.format_exc())
