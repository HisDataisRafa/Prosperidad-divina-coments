#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - GEMINI 2.5 FLASH-LITE OPTIMIZADO
Fecha: 09 de Septiembre de 2025

🚀 CONFIGURACIÓN OPTIMIZADA:
- ✅ Gemini 2.5 Flash-Lite (1,000 RPD - 4x más requests)
- ✅ Safety settings menos restrictivos para contenido espiritual
- ✅ Manejo robusto de bloqueos de seguridad
- ✅ Análisis de contexto de video mejorado
- ✅ 4 RPM seguro con capacidad de escalar
- ✅ Fallbacks inteligentes por tipo de comentario
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

class ProsperidadDivina_FlashLiteOptimizado:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*80)
        print(f"🚀 BOT PROSPERIDAD DIVINA - GEMINI 2.5 FLASH-LITE OPTIMIZADO")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. VERIFICACIÓN DETALLADA DE CREDENCIALES ---
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A"
        
        print(f"🔑 Diagnóstico de credenciales:")
        if not self.gemini_api_key: 
            print(f"   ❌ Gemini API Key: FALTANTE")
        else: 
            print(f"   ✅ Gemini API Key: Presente (longitud: {len(self.gemini_api_key)})")
            
        if not self.youtube_credentials_comments: 
            print(f"   ❌ YouTube OAuth: FALTANTE")
        else: 
            print(f"   ✅ YouTube OAuth: Presente (longitud: {len(self.youtube_credentials_comments)})")
        
        if not all([self.gemini_api_key, self.youtube_credentials_comments]):
            raise ValueError("❌ ERROR CRÍTICO: Faltan credenciales en las variables de entorno.")

        # --- 2. PARÁMETROS OPTIMIZADOS FLASH-LITE ---
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.max_respuestas_por_ejecucion = 10  # Mantener conservador, escalable a 40+
        self.rate_limit_seconds = 15  # 4 RPM seguro, escalable a 5+ RPM

        # --- 3. INICIALIZACIÓN CON DIAGNÓSTICO ---
        self.model = self.configurar_gemini_flash_lite()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # --- 4. PERSISTENCIA ---
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"\n🎯 CONFIGURACIÓN FLASH-LITE OPTIMIZADA:")
        print(f"   🤖 Modelo: Gemini 2.5 Flash-Lite (1,000 RPD)")
        print(f"   📝 Máximo comentarios: {self.max_respuestas_por_ejecucion}")
        print(f"   ⏱️  Pausa entre requests: {self.rate_limit_seconds}s")
        print(f"   🔢 RPM actual: {60/self.rate_limit_seconds:.1f}")
        print(f"   📈 RPM escalable: Hasta 16+ (con 1,000 RPD)")
        print(f"   ⏳ Tiempo estimado: {(self.max_respuestas_por_ejecucion * self.rate_limit_seconds)/60:.1f} min")
        print(f"   🛡️  Safety: Configuración optimizada para contenido espiritual")
        print("="*80)

    def configurar_gemini_flash_lite(self) -> genai.GenerativeModel:
        """Configuración de Gemini 2.5 Flash-Lite con safety settings optimizados."""
        try:
            print("\n🤖 CONFIGURANDO GEMINI 2.5 FLASH-LITE...")
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            print("   🧪 Realizando prueba de conexión con Flash-Lite...")
            print(f"   ⏱️  Aplicando pausa inicial de {self.rate_limit_seconds}s...")
            time.sleep(self.rate_limit_seconds)
            
            test_response = model.generate_content("Responde exactamente: 'Flash-Lite funcionando 2025'")
            
            if "flash-lite funcionando" in test_response.text.strip().lower():
                print("   🎉 ¡DIAGNÓSTICO EXITOSO! Gemini 2.5 Flash-Lite funcionando perfectamente.")
                print("   ⚡ Modelo optimizado para alto rendimiento y menos bloqueos.")
            else:
                print(f"   ⚠️  ADVERTENCIA: Flash-Lite responde, pero formato inesperado: '{test_response.text.strip()}'")
            return model
        except Exception as e:
            print(f"   ❌ ERROR FATAL EN CONFIGURACIÓN DE GEMINI FLASH-LITE:")
            print(f"   🔍 Tipo: {type(e).__name__}, Mensaje: {str(e)}")
            raise

    def configurar_youtube_lectura(self):
        """Configuración de YouTube API para lectura de comentarios."""
        try:
            print("\n📖 CONFIGURANDO YOUTUBE API (Lectura)...")
            service = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ YouTube API (lectura) configurada correctamente.")
            return service
        except Exception as e:
            print(f"   ❌ Error configurando YouTube API lectura: {e}")
            raise e

    def configurar_youtube_oauth(self):
        """Configuración de YouTube OAuth para escritura de comentarios."""
        try:
            print("\n📝 CONFIGURANDO YOUTUBE OAUTH (Escritura)...")
            creds_data = json.loads(self.youtube_credentials_comments)
            creds = Credentials.from_authorized_user_info(creds_data)
            service = build('youtube', 'v3', credentials=creds)
            print("   ✅ YouTube OAuth (escritura) configurado correctamente.")
            return service
        except Exception as e:
            print(f"   ❌ Error configurando YouTube OAuth: {e}")
            raise e

    def cargar_db_respondidos(self) -> Set[str]:
        """Carga la base de datos de comentarios ya respondidos."""
        if not os.path.exists(self.db_respondidos_path):
            print("   📝 Creando nueva base de datos de comentarios respondidos...")
            return set()
        
        with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
            respondidos = {line.strip() for line in f if line.strip()}
        print(f"   📊 Cargados {len(respondidos)} comentarios ya respondidos.")
        return respondidos

    def guardar_en_db_respondidos(self, comment_id: str):
        """Guarda un comentario ID en la base de datos de respondidos."""
        with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
            f.write(f"{comment_id}\n")
        self.comentarios_ya_respondidos.add(comment_id)

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
        """Carga la memoria de conversaciones por usuario."""
        if not os.path.exists(self.db_conversaciones_path):
            print("   🧠 Creando nueva memoria de conversaciones...")
            return {}
        
        with open(self.db_conversaciones_path, 'r', encoding='utf-8') as f:
            memoria = json.load(f)
        print(f"   🧠 Cargada memoria de {len(memoria)} usuarios.")
        return memoria

    def guardar_memoria_conversaciones(self):
        """Guarda la memoria de conversaciones en disco."""
        with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
            json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)

    def actualizar_memoria_usuario(self, autor_id: str, autor_nombre: str, nuevo_mensaje: str):
        """Actualiza la memoria de conversación de un usuario específico."""
        if autor_id not in self.memoria_conversacion_usuario:
            self.memoria_conversacion_usuario[autor_id] = {
                "nombre": autor_nombre,
                "mensajes": []
            }
        
        self.memoria_conversacion_usuario[autor_id]["mensajes"].append({
            "texto": nuevo_mensaje,
            "fecha": datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 3 mensajes
        self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
            self.memoria_conversacion_usuario[autor_id]["mensajes"][-3:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        """Obtiene el contexto previo de mensajes de un usuario."""
        if autor_id not in self.memoria_conversacion_usuario:
            return []
        return [msg["texto"] for msg in self.memoria_conversacion_usuario[autor_id]["mensajes"]]

    def obtener_videos_recientes(self) -> List[Dict]:
        """Obtiene los videos más recientes del canal."""
        try:
            print("\n📹 OBTENIENDO VIDEOS RECIENTES...")
            
            # Obtener el playlist de uploads del canal
            channel_response = self.youtube_lectura.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            if not channel_response.get('items'):
                print("   ❌ No se encontró el canal especificado.")
                return []
            
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Obtener los videos más recientes
            playlist_items = self.youtube_lectura.playlistItems().list(
                part='snippet',
                playlistId=uploads_id,
                maxResults=5
            ).execute()
            
            videos = []
            for item in playlist_items.get('items', []):
                video_info = {
                    'id': item['snippet']['resourceId']['videoId'],
                    'titulo': item['snippet']['title'],
                    'fecha': item['snippet']['publishedAt']
                }
                videos.append(video_info)
            
            print(f"   ✅ {len(videos)} videos encontrados para análisis.")
            for i, video in enumerate(videos, 1):
                print(f"      {i}. {video['titulo'][:50]}...")
            
            return videos
            
        except Exception as e:
            print(f"   ❌ Error obteniendo videos: {e}")
            return []

    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
        """Obtiene comentarios nuevos de un video específico."""
        comentarios_nuevos = []
        try:
            print(f"   🔍 Analizando: {video_titulo[:40]}...")
            
            response = self.youtube_lectura.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=50
            ).execute()
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                
                # Saltar comentarios ya respondidos o que ya tienen respuestas
                if comment_id in self.comentarios_ya_respondidos:
                    continue
                if item['snippet']['totalReplyCount'] > 0:
                    continue
                
                snippet = item['snippet']['topLevelComment']['snippet']
                autor_id = snippet.get('authorChannelId', {}).get('value')
                if not autor_id:
                    autor_id = f"fallback_{snippet['authorDisplayName']}"
                
                comentario_info = {
                    'id': comment_id,
                    'texto': snippet['textDisplay'],
                    'autor_nombre': snippet['authorDisplayName'],
                    'autor_id': autor_id,
                    'video_titulo': video_titulo,
                    'fecha': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                }
                comentarios_nuevos.append(comentario_info)
            
            print(f"      📊 {len(comentarios_nuevos)} comentarios nuevos encontrados.")
            return comentarios_nuevos
            
        except Exception as e:
            print(f"      ❌ Error obteniendo comentarios: {e}")
            return []
            
    def es_comentario_valido(self, texto: str) -> bool:
        """Valida si un comentario cumple los criterios para responder."""
        if not texto or len(texto.strip()) <= 3:
            return False
        if len(texto.strip()) > 500:
            return False
        if re.search(r'http[s]?://', texto, re.IGNORECASE):
            return False
        return True

    def detectar_tipo_comentario(self, texto: str, titulo_video: str = "") -> str:
        """Detecta el tipo de comentario para personalizar la respuesta."""
        texto_lower = texto.lower()
        titulo_lower = titulo_video.lower() if titulo_video else ""
        
        # Palabras de crisis - requieren atención especial
        palabras_crisis = ['no aguanto', 'suicidio', 'morir', 'matarme', 'acabar con todo']
        if any(word in texto_lower for word in palabras_crisis):
            return 'crisis'
        
        # Comentarios cortos/saludos
        if len(texto.split()) <= 3:
            return 'saludo'
        
        # Temas de abundancia/dinero (considerar también el título del video)
        palabras_abundancia = ['dinero', 'trabajo', 'abundancia', 'prosperidad', 'riqueza', 'financier']
        if (any(word in texto_lower for word in palabras_abundancia) or 
            any(word in titulo_lower for word in ['abundancia', 'prosperidad', 'dinero', 'riqueza'])):
            return 'abundancia'
        
        # Dolor emocional
        palabras_dolor = ['dolor', 'triste', 'depresión', 'ansiedad', 'solo', 'sufr']
        if any(word in texto_lower for word in palabras_dolor):
            return 'dolor_confusion'
        
        # Dudas o hostilidad
        palabras_duda = ['mentira', 'falso', 'estafa', 'no funciona', 'fake']
        if any(word in texto_lower for word in palabras_duda):
            return 'duda_hostilidad'
        
        # Agradecimientos y confirmaciones
        palabras_gratitud = ['gracias', 'bendiciones', 'amén', 'sí acepto', 'recibo']
        if any(word in texto_lower for word in palabras_gratitud):
            return 'gratitud'
        
        return 'general'

    def generar_respuesta_gemini_optimizada(self, comentario_actual: str, contexto_previo: List[str], 
                                           tipo: str, info_comentario: Dict) -> str:
        """Genera una respuesta usando Gemini 2.5 Flash-Lite con configuración optimizada."""
        
        # No responder a comentarios de crisis
        if tipo == 'crisis':
            print("      ⚠️  CRISIS DETECTADA - Comentario ignorado por seguridad.")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None
        
        try:
            # Construir contexto si existe
            contexto_str = ""
            if contexto_previo:
                contexto_str = ("Mensajes anteriores de este usuario:\n" + 
                               "\n".join(f"- \"{msg}\"" for msg in contexto_previo) + "\n\n")
            
            # Crear prompt personalizado incluyendo el contexto del video
            prompt = f"""Eres un asistente espiritual del canal "Prosperidad Divina". 

{contexto_str}Video actual: "{info_comentario['video_titulo']}"
Usuario: {info_comentario['autor_nombre']}
Comentario actual: "{comentario_actual}"

Instrucciones:
- Responde con máximo 2 líneas
- Sé empático, positivo y espiritual
- Usa emojis apropiados (✨🙏💫🌟)
- Si es relevante, conecta tu respuesta con el tema del video
- Enfócate en bendiciones y luz divina
- Mantén un tono cálido y alentador

Respuesta:"""
            
            print(f"      🧠 Enviando a Flash-Lite... (pausa de {self.rate_limit_seconds}s)")
            time.sleep(self.rate_limit_seconds)
            
            # Configurar safety settings menos restrictivos para contenido espiritual
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=150
                ),
                safety_settings=safety_settings
            )
            
            # Verificar si la respuesta fue bloqueada por filtros de seguridad
            if not response or not response.text:
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    if finish_reason == 2:  # SAFETY
                        print(f"      ⚠️  Respuesta bloqueada por filtros de seguridad de Gemini")
                        self.stats['resumen']['respuestas_bloqueadas_seguridad'] = self.stats['resumen'].get('respuestas_bloqueadas_seguridad', 0) + 1
                        raise ValueError("Respuesta bloqueada por seguridad - usando fallback")
                    else:
                        print(f"      ⚠️  Respuesta vacía, finish_reason: {finish_reason}")
                        raise ValueError("Respuesta vacía de Gemini")
                else:
                    raise ValueError("Respuesta vacía de Gemini")
            
            respuesta = response.text.strip()
            print(f"      ✅ Flash-Lite respondió: \"{respuesta[:70]}...\"")
            self.stats['resumen']['respuestas_ia_exitosas'] += 1
            return respuesta
            
        except Exception as e:
            print(f"      ❌ Error en Flash-Lite: {type(e).__name__} - {str(e)}")
            self.stats['resumen']['errores_gemini'] += 1
            
            # Fallbacks inteligentes por tipo de comentario
            fallbacks = {
                'saludo': [
                    "Bendiciones de luz en tu camino ✨🙏",
                    "Que la paz divina te acompañe 🌟🙏",
                    "Luz y amor para tu alma 💫✨🙏"
                ],
                'abundancia': [
                    "Que la prosperidad divina florezca en tu vida 💰✨🙏",
                    "Visualiza la abundancia llegando a ti 🌟💰🙏",
                    "Que el universo conspire para tu prosperidad 💫💰🙏"
                ],
                'dolor_confusion': [
                    "Que la paz divina sane tu corazón 💙✨🙏",
                    "Enviamos luz sanadora a tu alma 🌟💙🙏",
                    "Que encuentres fortaleza en la luz divina 💫💙🙏"
                ],
                'duda_hostilidad': [
                    "Respetamos tu perspectiva. Bendiciones 🕊️🙏",
                    "Que encuentres paz en tu corazón 💙✨🙏",
                    "Luz y comprensión para tu camino 🌟🕊️🙏"
                ],
                'gratitud': [
                    "¡Hermoso corazón agradecido! Que las bendiciones se multipliquen ✨🙏",
                    "Tu gratitud atrae más abundancia divina 🌟💫🙏",
                    "Que tu fe y gratitud sigan creciendo 💙✨🙏"
                ],
                'general': [
                    "Que la luz divina te acompañe siempre ✨🙏",
                    "Bendiciones infinitas para tu alma 💫🙏",
                    "Que la paz y el amor llenen tu vida 🌟💙🙏"
                ]
            }
            
            return random.choice(fallbacks.get(tipo, fallbacks['general']))

    def responder_comentario_seguro(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        """Responde a un comentario con manejo robusto de errores."""
        try:
            print(f"      📤 Enviando respuesta a YouTube...")
            
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': comentario_id,
                        'textOriginal': respuesta
                    }
                }
            ).execute()
            
            print(f"      ✅ Respuesta enviada exitosamente a '{autor_nombre}'.")
            self.guardar_en_db_respondidos(comentario_id)
            return True
            
        except HttpError as e:
            error_msg = e.content.decode('utf-8') if e.content else str(e)
            print(f"      ❌ Error HTTP al responder: {error_msg}")
            self.stats['resumen']['errores_youtube'] += 1
            return False
        except Exception as e:
            print(f"      ❌ Error inesperado al responder: {e}")
            self.stats['resumen']['errores_youtube'] += 1
            return False

    def inicializar_estadisticas(self):
        """Inicializa las estadísticas de la ejecución."""
        return {
            'info_ejecucion': {
                'id': self.run_id,
                'inicio': datetime.now().isoformat(),
                'modo': 'GEMINI_2.5_FLASH_LITE_OPTIMIZADO',
                'modelo': 'gemini-2.5-flash-lite',
                'max_comentarios': self.max_respuestas_por_ejecucion,
                'rpm_configurado': round(60/self.rate_limit_seconds, 1),
                'limite_diario_teorico': 1000
            },
            'resumen': {
                'comentarios_procesados': 0,
                'respuestas_exitosas': 0,
                'respuestas_ia_exitosas': 0,
                'errores_gemini': 0,
                'errores_youtube': 0,
                'comentarios_filtrados': 0,
                'respuestas_bloqueadas_seguridad': 0
            },
            'tipos_procesados': {},
            'acciones_de_moderacion': {
                'crisis_ignorada': 0
            }
        }

    def ejecutar_optimizado(self):
        """Ejecuta el bot con configuración optimizada Flash-Lite."""
        print(f"\n🚀 INICIANDO BOT OPTIMIZADO CON FLASH-LITE...")
        inicio = datetime.now()
        respuestas_enviadas = 0
        
        # Obtener videos recientes
        videos = self.obtener_videos_recientes()
        if not videos:
            print("❌ No se pudieron obtener videos. Abortando ejecución.")
            return
        
        print(f"\n🎯 OBJETIVO: Procesar {self.max_respuestas_por_ejecucion} comentarios")
        print(f"⚡ Modelo: Gemini 2.5 Flash-Lite (1,000 RPD)")
        print(f"⏱️  Tiempo estimado: {(self.max_respuestas_por_ejecucion * self.rate_limit_seconds)/60:.1f} minutos")
        print("-" * 60)
        
        # Procesar comentarios de cada video
        for video_idx, video in enumerate(videos, 1):
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
                
            print(f"\n📹 PROCESANDO VIDEO {video_idx}/{len(videos)}")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            if not comentarios:
                print("   📭 No hay comentarios nuevos en este video.")
                continue
            
            # Ordenar comentarios por fecha (más recientes primero)
            comentarios.sort(key=lambda x: x['fecha'], reverse=True)
            
            # Procesar cada comentario
            for comentario in comentarios:
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                # Validar comentario
                if not self.es_comentario_valido(comentario['texto']):
                    print(f"   ⏭️  Comentario filtrado (muy corto/largo/con enlaces)")
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue
                
                print(f"\n   💬 PROCESANDO COMENTARIO #{respuestas_enviadas + 1}")
                print(f"      👤 Usuario: {comentario['autor_nombre']}")
                print(f"      📝 Texto: \"{comentario['texto'][:60]}...\"")
                print(f"      🎬 Video: {comentario['video_titulo'][:40]}...")
                
                # Obtener contexto previo del usuario
                contexto_previo = self.obtener_contexto_usuario(comentario['autor_id'])
                if contexto_previo:
                    print(f"      🧠 Contexto previo: {len(contexto_previo)} mensajes")
                
                # Detectar tipo de comentario con contexto de video
                tipo = self.detectar_tipo_comentario(comentario['texto'], comentario['video_titulo'])
                print(f"      🏷️  Tipo detectado: {tipo}")
                
                # Generar respuesta con Flash-Lite optimizado
                respuesta = self.generar_respuesta_gemini_optimizada(
                    comentario['texto'], 
                    contexto_previo, 
                    tipo, 
                    comentario
                )
                
                if respuesta is None:
                    print("      ⏭️  Comentario omitido (crisis o error).")
                    continue
                
                # Enviar respuesta
                if self.responder_comentario_seguro(comentario['id'], respuesta, comentario['autor_nombre']):
                    respuestas_enviadas += 1
                    self.stats['resumen']['respuestas_exitosas'] += 1
                    self.stats['tipos_procesados'][tipo] = self.stats['tipos_procesados'].get(tipo, 0) + 1
                    
                    # Actualizar memoria del usuario
                    self.actualizar_memoria_usuario(
                        comentario['autor_id'], 
                        comentario['autor_nombre'], 
                        comentario['texto']
                    )
                    
                    print(f"      🎉 ¡Éxito! Progreso: {respuestas_enviadas}/{self.max_respuestas_por_ejecucion}")
                
                else:
                    print(f"      ❌ Error al enviar respuesta.")
        
        # Guardar memoria y generar reporte
        self.guardar_memoria_conversaciones()
        duracion_total = (datetime.now() - inicio).total_seconds()
        self.generar_reporte_final(duracion_total)

    def generar_reporte_final(self, duracion_segundos: float):
        """Genera el reporte final de la ejecución."""
        stats = self.stats
        stats['info_ejecucion']['fin'] = datetime.now().isoformat()
        stats['info_ejecucion']['duracion_segundos'] = round(duracion_segundos, 2)
        stats['info_ejecucion']['duracion_minutos'] = round(duracion_segundos / 60, 2)
        
        # Guardar estadísticas en archivo
        nombre_reporte = f"reporte_{self.run_id}.json"
        with open(nombre_reporte, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Mostrar reporte en consola
        print("\n" + "="*80)
        print("📊 REPORTE FINAL - GEMINI 2.5 FLASH-LITE OPTIMIZADO")
        print("="*80)
        
        print(f"⚡ MODELO Y CONFIGURACIÓN:")
        print(f"   - Modelo: {stats['info_ejecucion']['modelo']}")
        print(f"   - RPM configurado: {stats['info_ejecucion']['rpm_configurado']}")
        print(f"   - Límite diario teórico: {stats['info_ejecucion']['limite_diario_teorico']} RPD")
        
        print(f"\n⏱️  TIEMPO DE EJECUCIÓN:")
        print(f"   - Duración total: {stats['info_ejecucion']['duracion_minutos']} minutos")
        print(f"   - Tiempo promedio por comentario: {stats['info_ejecucion']['duracion_segundos']/max(stats['resumen']['respuestas_exitosas'], 1):.1f}s")
        
        print(f"\n📈 RESULTADOS:")
        print(f"   - Comentarios procesados: {stats['resumen']['comentarios_procesados']}")
        print(f"   - Respuestas enviadas: {stats['resumen']['respuestas_exitosas']}")
        print(f"   - Comentarios filtrados: {stats['resumen']['comentarios_filtrados']}")
        
        print(f"\n🤖 RENDIMIENTO DE IA:")
        print(f"   - Respuestas de Gemini: {stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   - Fallbacks usados: {stats['resumen']['respuestas_exitosas'] - stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   - Errores Gemini: {stats['resumen']['errores_gemini']}")
        print(f"   - Bloqueadas por seguridad: {stats['resumen'].get('respuestas_bloqueadas_seguridad', 0)}")
        print(f"   - Errores YouTube: {stats['resumen']['errores_youtube']}")
        
        if stats['tipos_procesados']:
            print(f"\n📝 TIPOS DE COMENTARIOS:")
            for tipo, cantidad in stats['tipos_procesados'].items():
                print(f"   - {tipo}: {cantidad}")
        
        print(f"\n🛡️  MODERACIÓN:")
        print(f"   - Comentarios de crisis ignorados: {stats['acciones_de_moderacion']['crisis_ignorada']}")
        print(f"   - Filtros de seguridad activados: {stats['resumen'].get('respuestas_bloqueadas_seguridad', 0)}")
        
        # Calcular tasa de éxito de IA
        if stats['resumen']['respuestas_exitosas'] > 0:
            tasa_ia = (stats['resumen']['respuestas_ia_exitosas'] / stats['resumen']['respuestas_exitosas']) * 100
            tasa_bloqueos = (stats['resumen'].get('respuestas_bloqueadas_seguridad', 0) / stats['resumen']['comentarios_procesados']) * 100 if stats['resumen']['comentarios_procesados'] > 0 else 0
        else:
            tasa_ia = 0
            tasa_bloqueos = 0
        
        print(f"\n📊 MÉTRICAS DE RENDIMIENTO:")
        print(f"   - Tasa de éxito IA: {tasa_ia:.1f}%")
        print(f"   - Tasa de bloqueos: {tasa_bloqueos:.1f}%")
        
        print(f"\n--- 🏆 DIAGNÓSTICO FINAL ---")
        if stats['resumen']['respuestas_ia_exitosas'] >= 8:
            print("🎉 ¡EXCELENTE! Flash-Lite funcionando perfectamente. Listo para escalar.")
            print("💡 Puedes aumentar RPM o comentarios por ejecución.")
        elif stats['resumen']['respuestas_ia_exitosas'] >= 5:
            print("✅ BUENO. Flash-Lite funciona bien con algunos bloqueos menores.")
            print("💡 Los safety settings optimizados están funcionando.")
        elif stats['resumen']['respuestas_exitosas'] > 0:
            print("⚠️  PROBLEMAS CON FLASH-LITE. Muchos fallbacks. Revisa configuración.")
        else:
            print("❌ ERROR CRÍTICO. No se enviaron respuestas. Revisa configuración completa.")
        
        print(f"\n🚀 POTENCIAL DE ESCALAMIENTO:")
        print(f"   - Configuración actual: {stats['info_ejecucion']['rpm_configurado']} RPM")
        print(f"   - Máximo teórico con 1,000 RPD: ~16 RPM")
        print(f"   - Comentarios/día actuales: ~{stats['resumen']['respuestas_exitosas'] * 24}")
        print(f"   - Comentarios/día máximo teórico: ~1,000")
        
        print(f"\n📄 Reporte detallado guardado en: {nombre_reporte}")
        print("="*80)

if __name__ == "__main__":
    try:
        bot = ProsperidadDivina_FlashLiteOptimizado()
        bot.ejecutar_optimizado()
        
        print("\n🎯 EJECUCIÓN COMPLETADA CON ÉXITO")
        print("\n🚀 PRÓXIMOS PASOS RECOMENDADOS:")
        print("1. Si todo funcionó bien, puedes:")
        print("   • Aumentar max_respuestas_por_ejecucion hasta 40+")
        print("   • Reducir rate_limit_seconds a 4-6 segundos")
        print("   • Ejecutar cada 20 minutos: cron '0,20,40 * * *'")
        print("2. Flash-Lite soporta hasta 1,000 RPD - ¡mucho margen de crecimiento!")
        print("3. Monitorea bloqueos de seguridad en los reportes")
        
    except KeyboardInterrupt:
        print("\n⏹️  Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO NO MANEJADO: {e}")
        print(traceback.format_exc())
