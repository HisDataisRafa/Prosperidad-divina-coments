#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - CONFIGURACIÓN 800 RPD
Fecha: 09 de Septiembre de 2025

🎯 CONFIGURACIÓN OPTIMIZADA PARA 800 RPD:
- ✅ Gemini 2.5 Flash-Lite (1,000 RPD disponibles)
- ✅ 4 RPM (15 segundos entre requests)
- ✅ 17 comentarios por ejecución
- ✅ Ejecutar cada 30 minutos = 816 RPD diarios
- ✅ Safety settings optimizados
- ✅ Manejo inteligente de bloqueos
- ✅ Contexto de video y memoria persistente
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

class ProsperidadDivina_800RPD:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*80)
        print(f"🎯 BOT PROSPERIDAD DIVINA - CONFIGURACIÓN 800 RPD")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. VERIFICACIÓN DE CREDENCIALES ---
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

        # --- 2. PARÁMETROS PARA 800 RPD ---
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.max_respuestas_por_ejecucion = 17  # 17 × 48 ejecuciones/día = 816 RPD
        self.rate_limit_seconds = 15  # 4 RPM exactos

        # --- 3. INICIALIZACIÓN ---
        self.model = self.configurar_gemini_flash_lite()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # --- 4. PERSISTENCIA ---
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"\n🎯 CONFIGURACIÓN 800 RPD:")
        print(f"   🤖 Modelo: Gemini 2.5 Flash-Lite")
        print(f"   📝 Comentarios por ejecución: {self.max_respuestas_por_ejecucion}")
        print(f"   ⏱️  Pausa entre requests: {self.rate_limit_seconds}s")
        print(f"   🔢 RPM: {60/self.rate_limit_seconds:.1f}")
        print(f"   📅 Ejecuciones/día: 48 (cada 30 min)")
        print(f"   📈 RPD objetivo: {self.max_respuestas_por_ejecucion * 48}")
        print(f"   ⏳ Tiempo por ejecución: {(self.max_respuestas_por_ejecucion * self.rate_limit_seconds)/60:.1f} min")
        print(f"   🛡️  Límite Flash-Lite: 1,000 RPD (margen: {1000 - (self.max_respuestas_por_ejecucion * 48)})")
        print("="*80)

    def configurar_gemini_flash_lite(self) -> genai.GenerativeModel:
        """Configuración de Gemini 2.5 Flash-Lite optimizado."""
        try:
            print("\n🤖 CONFIGURANDO GEMINI 2.5 FLASH-LITE...")
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            print("   🧪 Realizando prueba de conexión...")
            print(f"   ⏱️  Aplicando pausa inicial de {self.rate_limit_seconds}s...")
            time.sleep(self.rate_limit_seconds)
            
            test_response = model.generate_content("Responde exactamente: 'Configuración 800 RPD lista'")
            
            if "800 rpd lista" in test_response.text.strip().lower():
                print("   🎉 ¡ÉXITO! Gemini Flash-Lite configurado para 800 RPD.")
            else:
                print(f"   ⚠️  ADVERTENCIA: Respuesta inesperada: '{test_response.text.strip()}'")
            return model
        except Exception as e:
            print(f"   ❌ ERROR FATAL: {type(e).__name__} - {str(e)}")
            raise

    def configurar_youtube_lectura(self):
        """Configuración de YouTube API para lectura."""
        try:
            print("\n📖 CONFIGURANDO YOUTUBE API (Lectura)...")
            service = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ YouTube API configurada correctamente.")
            return service
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise e

    def configurar_youtube_oauth(self):
        """Configuración de YouTube OAuth para escritura."""
        try:
            print("\n📝 CONFIGURANDO YOUTUBE OAUTH (Escritura)...")
            creds_data = json.loads(self.youtube_credentials_comments)
            creds = Credentials.from_authorized_user_info(creds_data)
            service = build('youtube', 'v3', credentials=creds)
            print("   ✅ YouTube OAuth configurado correctamente.")
            return service
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise e

    def cargar_db_respondidos(self) -> Set[str]:
        """Carga la base de datos de comentarios respondidos."""
        if not os.path.exists(self.db_respondidos_path):
            return set()
        
        with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
            respondidos = {line.strip() for line in f if line.strip()}
        print(f"   📊 {len(respondidos)} comentarios ya respondidos.")
        return respondidos

    def guardar_en_db_respondidos(self, comment_id: str):
        """Guarda un comentario ID en la BD."""
        with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
            f.write(f"{comment_id}\n")
        self.comentarios_ya_respondidos.add(comment_id)

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
        """Carga la memoria de conversaciones."""
        if not os.path.exists(self.db_conversaciones_path):
            return {}
        
        with open(self.db_conversaciones_path, 'r', encoding='utf-8') as f:
            memoria = json.load(f)
        print(f"   🧠 Memoria de {len(memoria)} usuarios cargada.")
        return memoria

    def guardar_memoria_conversaciones(self):
        """Guarda la memoria de conversaciones."""
        with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
            json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)

    def actualizar_memoria_usuario(self, autor_id: str, autor_nombre: str, nuevo_mensaje: str):
        """Actualiza la memoria de un usuario."""
        if autor_id not in self.memoria_conversacion_usuario:
            self.memoria_conversacion_usuario[autor_id] = {
                "nombre": autor_nombre,
                "mensajes": []
            }
        
        self.memoria_conversacion_usuario[autor_id]["mensajes"].append({
            "texto": nuevo_mensaje,
            "fecha": datetime.now().isoformat()
        })
        
        # Mantener solo últimos 3 mensajes
        self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
            self.memoria_conversacion_usuario[autor_id]["mensajes"][-3:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        """Obtiene el contexto de mensajes previos."""
        if autor_id not in self.memoria_conversacion_usuario:
            return []
        return [msg["texto"] for msg in self.memoria_conversacion_usuario[autor_id]["mensajes"]]

    def obtener_videos_recientes(self) -> List[Dict]:
        """Obtiene los videos más recientes del canal."""
        try:
            print("\n📹 OBTENIENDO VIDEOS RECIENTES...")
            
            channel_response = self.youtube_lectura.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            if not channel_response.get('items'):
                print("   ❌ Canal no encontrado.")
                return []
            
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
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
            
            print(f"   ✅ {len(videos)} videos encontrados.")
            return videos
            
        except Exception as e:
            print(f"   ❌ Error obteniendo videos: {e}")
            return []

    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
        """Obtiene comentarios nuevos de un video."""
        comentarios_nuevos = []
        try:
            print(f"   🔍 {video_titulo[:30]}...")
            
            response = self.youtube_lectura.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=50
            ).execute()
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                
                # Filtrar comentarios ya respondidos
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
            
            print(f"      📊 {len(comentarios_nuevos)} comentarios nuevos.")
            return comentarios_nuevos
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []
            
    def es_comentario_valido(self, texto: str) -> bool:
        """Valida si un comentario es procesable."""
        if not texto or len(texto.strip()) <= 3:
            return False
        if len(texto.strip()) > 500:
            return False
        if re.search(r'http[s]?://', texto, re.IGNORECASE):
            return False
        return True

    def detectar_tipo_comentario(self, texto: str, titulo_video: str = "") -> str:
        """Detecta el tipo de comentario para personalización."""
        texto_lower = texto.lower()
        titulo_lower = titulo_video.lower() if titulo_video else ""
        
        # Crisis - ignorar
        palabras_crisis = ['no aguanto', 'suicidio', 'morir', 'matarme', 'acabar con todo']
        if any(word in texto_lower for word in palabras_crisis):
            return 'crisis'
        
        # Saludos cortos
        if len(texto.split()) <= 3:
            return 'saludo'
        
        # Abundancia/dinero (considerar título del video)
        palabras_abundancia = ['dinero', 'trabajo', 'abundancia', 'prosperidad', 'riqueza']
        if (any(word in texto_lower for word in palabras_abundancia) or 
            any(word in titulo_lower for word in ['abundancia', 'prosperidad', 'dinero', 'riqueza'])):
            return 'abundancia'
        
        # Dolor emocional
        palabras_dolor = ['dolor', 'triste', 'depresión', 'ansiedad', 'solo', 'sufr']
        if any(word in texto_lower for word in palabras_dolor):
            return 'dolor_confusion'
        
        # Dudas/hostilidad
        palabras_duda = ['mentira', 'falso', 'estafa', 'no funciona', 'fake']
        if any(word in texto_lower for word in palabras_duda):
            return 'duda_hostilidad'
        
        # Gratitud
        palabras_gratitud = ['gracias', 'bendiciones', 'amén', 'sí acepto', 'recibo']
        if any(word in texto_lower for word in palabras_gratitud):
            return 'gratitud'
        
        return 'general'

    def generar_respuesta_800rpd(self, comentario_actual: str, contexto_previo: List[str], 
                                tipo: str, info_comentario: Dict) -> str:
        """Genera respuesta optimizada para 800 RPD con Flash-Lite."""
        
        if tipo == 'crisis':
            print("      ⚠️  CRISIS - Comentario omitido.")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None
        
        try:
            # Contexto previo
            contexto_str = ""
            if contexto_previo:
                contexto_str = ("Historial:\n" + 
                               "\n".join(f"- \"{msg}\"" for msg in contexto_previo) + "\n\n")
            
            # Prompt optimizado para 800 RPD
            # Prompt optimizado - uso selectivo del contexto del video
            prompt = f"""Eres un asistente espiritual del canal "Prosperidad Divina". 

{contexto_str}Video: "{info_comentario['video_titulo']}"
Usuario: {info_comentario['autor_nombre']}
Comentario: "{comentario_actual}"

Instrucciones:
- Responde con máximo 2 líneas
- Sé empático, positivo y espiritual
- Usa emojis apropiados (✨🙏💫🌟)
- Responde DIRECTAMENTE al comentario del usuario
- SOLO menciona elementos del título del video si el usuario los menciona específicamente
- Si el usuario habla de Dios, responde sobre Dios
- Si el usuario habla de bendiciones, responde sobre bendiciones
- NO fuerces conexiones con el título si no son naturales
- Mantén un tono cálido y alentador

Respuesta:"""
            
            print(f"      🧠 Enviando a Flash-Lite... (pausa {self.rate_limit_seconds}s)")
            time.sleep(self.rate_limit_seconds)
            
            # Safety settings optimizados
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=150
                ),
                safety_settings=safety_settings
            )
            
            # Verificar bloqueos de seguridad
            if not response or not response.text:
                if hasattr(response, 'candidates') and response.candidates:
                    finish_reason = response.candidates[0].finish_reason
                    if finish_reason == 2:  # SAFETY
                        print(f"      ⚠️  Bloqueado por seguridad")
                        self.stats['resumen']['respuestas_bloqueadas_seguridad'] = \
                            self.stats['resumen'].get('respuestas_bloqueadas_seguridad', 0) + 1
                        raise ValueError("Bloqueado por seguridad")
                    else:
                        print(f"      ⚠️  Respuesta vacía, finish_reason: {finish_reason}")
                        raise ValueError("Respuesta vacía")
                else:
                    raise ValueError("Respuesta vacía")
            
            respuesta = response.text.strip()
            print(f"      ✅ Flash-Lite: \"{respuesta[:50]}...\"")
            self.stats['resumen']['respuestas_ia_exitosas'] += 1
            return respuesta
            
        except Exception as e:
            print(f"      ❌ Error Flash-Lite: {type(e).__name__}")
            self.stats['resumen']['errores_gemini'] += 1
            
            # Fallbacks neutros sin forzar elementos del título
            fallbacks = {
                'saludo': [
                    "Bendiciones en tu camino ✨🙏", 
                    "Luz divina te acompañe 🌟🙏"
                ],
                'abundancia': [
                    "Que la prosperidad fluya hacia ti 💰✨🙏", 
                    "Abundancia divina en tu vida 🌟💰🙏"
                ],
                'dolor_confusion': [
                    "Que Dios sane tu corazón 💙✨🙏", 
                    "Paz divina te envuelva 🌟💙🙏"
                ],
                'duda_hostilidad': [
                    "Bendiciones y comprensión 🕊️🙏", 
                    "Que encuentres paz 💙✨🙏"
                ],
                'gratitud': [
                    "Que tus bendiciones se multipliquen ✨🙏", 
                    "Dios ve tu corazón agradecido 🌟💫🙏"
                ],
                'general': [
                    "Que Dios te bendiga siempre ✨🙏", 
                    "Paz y luz divina para ti 🌟💙🙏",
                    "Bendiciones infinitas en tu camino 💫🙏",
                    "Que la luz divina te acompañe ✨🌟🙏",
                    "Amor y paz para tu alma 💙✨🙏",
                    "Que Dios llene tu vida de gozo 🌟💫🙏"
                ]
            }
            
            return random.choice(fallbacks.get(tipo, fallbacks['general']))

    def responder_comentario_800rpd(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        """Responde comentario optimizado para 800 RPD."""
        try:
            print(f"      📤 Enviando respuesta...")
            
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={
                    'snippet': {
                        'parentId': comentario_id,
                        'textOriginal': respuesta
                    }
                }
            ).execute()
            
            print(f"      ✅ Enviada a '{autor_nombre}'.")
            self.guardar_en_db_respondidos(comentario_id)
            return True
            
        except HttpError as e:
            error_msg = e.content.decode('utf-8') if e.content else str(e)
            print(f"      ❌ Error HTTP: {error_msg}")
            self.stats['resumen']['errores_youtube'] += 1
            return False
        except Exception as e:
            print(f"      ❌ Error: {e}")
            self.stats['resumen']['errores_youtube'] += 1
            return False

    def inicializar_estadisticas(self):
        """Inicializa estadísticas para 800 RPD."""
        return {
            'info_ejecucion': {
                'id': self.run_id,
                'inicio': datetime.now().isoformat(),
                'modo': 'CONFIGURACION_800_RPD',
                'modelo': 'gemini-2.5-flash-lite',
                'max_comentarios': self.max_respuestas_por_ejecucion,
                'rpm_configurado': round(60/self.rate_limit_seconds, 1),
                'rpd_objetivo': self.max_respuestas_por_ejecucion * 48,
                'ejecuciones_dia': 48
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

    def ejecutar_800rpd(self):
        """Ejecución principal optimizada para 800 RPD."""
        print(f"\n🚀 INICIANDO EJECUCIÓN 800 RPD...")
        inicio = datetime.now()
        respuestas_enviadas = 0
        
        videos = self.obtener_videos_recientes()
        if not videos:
            print("❌ No hay videos disponibles.")
            return
        
        print(f"\n🎯 PROCESANDO {self.max_respuestas_por_ejecucion} COMENTARIOS:")
        print(f"   ⚡ Configuración: 4 RPM × {self.max_respuestas_por_ejecucion} comentarios")
        print(f"   📅 Objetivo diario: {self.max_respuestas_por_ejecucion * 48} RPD")
        print(f"   ⏱️  Tiempo estimado: {(self.max_respuestas_por_ejecucion * self.rate_limit_seconds)/60:.1f} min")
        print("-" * 60)
        
        # Procesar videos
        for video_idx, video in enumerate(videos, 1):
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
                
            print(f"\n📹 VIDEO {video_idx}/{len(videos)}")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            if not comentarios:
                continue
            
            # Ordenar por fecha
            comentarios.sort(key=lambda x: x['fecha'], reverse=True)
            
            # Procesar comentarios
            for comentario in comentarios:
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                if not self.es_comentario_valido(comentario['texto']):
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue
                
                print(f"\n   💬 COMENTARIO #{respuestas_enviadas + 1}")
                print(f"      👤 {comentario['autor_nombre']}")
                print(f"      📝 \"{comentario['texto'][:50]}...\"")
                
                # Contexto y tipo
                contexto_previo = self.obtener_contexto_usuario(comentario['autor_id'])
                tipo = self.detectar_tipo_comentario(comentario['texto'], comentario['video_titulo'])
                print(f"      🏷️  Tipo: {tipo}")
                
                # Generar respuesta
                respuesta = self.generar_respuesta_800rpd(
                    comentario['texto'], 
                    contexto_previo, 
                    tipo, 
                    comentario
                )
                
                if respuesta is None:
                    continue
                
                # Enviar respuesta
                if self.responder_comentario_800rpd(comentario['id'], respuesta, comentario['autor_nombre']):
                    respuestas_enviadas += 1
                    self.stats['resumen']['respuestas_exitosas'] += 1
                    self.stats['tipos_procesados'][tipo] = self.stats['tipos_procesados'].get(tipo, 0) + 1
                    
                    self.actualizar_memoria_usuario(
                        comentario['autor_id'], 
                        comentario['autor_nombre'], 
                        comentario['texto']
                    )
                    
                    print(f"      🎉 Progreso: {respuestas_enviadas}/{self.max_respuestas_por_ejecucion}")
        
        # Guardar y reportar
        self.guardar_memoria_conversaciones()
        duracion_total = (datetime.now() - inicio).total_seconds()
        self.generar_reporte_800rpd(duracion_total)

    def generar_reporte_800rpd(self, duracion_segundos: float):
        """Genera reporte optimizado para 800 RPD."""
        stats = self.stats
        stats['info_ejecucion']['fin'] = datetime.now().isoformat()
        stats['info_ejecucion']['duracion_segundos'] = round(duracion_segundos, 2)
        stats['info_ejecucion']['duracion_minutos'] = round(duracion_segundos / 60, 2)
        
        # Guardar reporte
        nombre_reporte = f"reporte_{self.run_id}.json"
        with open(nombre_reporte, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Reporte en consola
        print("\n" + "="*80)
        print("📊 REPORTE 800 RPD - EJECUCIÓN COMPLETADA")
        print("="*80)
        
        print(f"🎯 CONFIGURACIÓN:")
        print(f"   - Modelo: {stats['info_ejecucion']['modelo']}")
        print(f"   - RPM: {stats['info_ejecucion']['rpm_configurado']}")
        print(f"   - Comentarios/ejecución: {stats['info_ejecucion']['max_comentarios']}")
        print(f"   - Ejecuciones/día: {stats['info_ejecucion']['ejecuciones_dia']}")
        print(f"   - RPD objetivo: {stats['info_ejecucion']['rpd_objetivo']}")
        
        print(f"\n⏱️  RENDIMIENTO:")
        print(f"   - Duración: {stats['info_ejecucion']['duracion_minutos']} min")
        print(f"   - Tiempo/comentario: {stats['info_ejecucion']['duracion_segundos']/max(stats['resumen']['respuestas_exitosas'], 1):.1f}s")
        
        print(f"\n📈 RESULTADOS:")
        print(f"   - Procesados: {stats['resumen']['comentarios_procesados']}")
        print(f"   - Enviados: {stats['resumen']['respuestas_exitosas']}")
        print(f"   - Filtrados: {stats['resumen']['comentarios_filtrados']}")
        
        print(f"\n🤖 IA:")
        print(f"   - Gemini: {stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   - Fallbacks: {stats['resumen']['respuestas_exitosas'] - stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   - Bloqueados: {stats['resumen'].get('respuestas_bloqueadas_seguridad', 0)}")
        print(f"   - Errores: {stats['resumen']['errores_gemini']} + {stats['resumen']['errores_youtube']}")
        
        # Proyección diaria
        if stats['resumen']['respuestas_exitosas'] > 0:
            proyeccion_diaria = stats['resumen']['respuestas_exitosas'] * 48
            print(f"\n📊 PROYECCIÓN DIARIA:")
            print(f"   - Con esta ejecución: {proyeccion_diaria} RPD")
            print(f"   - Objetivo 800 RPD: {proyeccion_diaria/800*100:.1f}%")
        
        # Diagnóstico
        print(f"\n--- 🎯 DIAGNÓSTICO 800 RPD ---")
        if stats['resumen']['respuestas_exitosas'] >= 15:
            print("🎉 EXCELENTE! Configuración 800 RPD funcionando perfectamente.")
        elif stats['resumen']['respuestas_exitosas'] >= 10:
            print("✅ BUENO. Cerca del objetivo. Revisar disponibilidad de comentarios.")
        elif stats['resumen']['respuestas_exitosas'] > 0:
            print("⚠️  PARCIAL. Revisar filtros o incrementar comentarios disponibles.")
        else:
            print("❌ ERROR. No se procesaron comentarios. Revisar configuración.")
        
        print(f"\n📄 Reporte guardado: {nombre_reporte}")
        print("="*80)

if __name__ == "__main__":
    try:
        bot = ProsperidadDivina_800RPD()
        bot.ejecutar_800rpd()
        
        print("\n🎯 CONFIGURACIÓN 800 RPD COMPLETADA")
        print("\n📋 INSTRUCCIONES PARA EL WORKFLOW:")
        print("• Cambiar cron a: '0,30 * * *' (cada 30 minutos)")
        print("• 48 ejecuciones/día × 17 comentarios = 816 RPD")
        print("• Dentro del límite Flash-Lite de 1,000 RPD")
        
    except KeyboardInterrupt:
        print("\n⏹️  Ejecución interrumpida.")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print(traceback.format_exc())
