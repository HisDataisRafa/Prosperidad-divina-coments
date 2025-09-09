#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN CON CONTEXTO PERSISTENTE
Fecha de Versión: 08 de Septiembre de 2025

MEJORAS IMPLEMENTADAS:
- ✅ Contexto de usuarios persistente entre ejecuciones
- ✅ Procesamiento de comentarios de más recientes a más antiguos
- ✅ Sistema de archivos separado para memoria de conversaciones
- ✅ Limpieza automática de conversaciones antiguas
"""

import os
import re
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Set

import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ProsperidadDivinaBotPersistente:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*80)
        print(f"👑 INICIANDO BOT PROSPERIDAD DIVINA - VERSIÓN CONTEXTO PERSISTENTE")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. CONFIGURACIÓN ---
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A"
        if not all([self.gemini_api_key, self.youtube_credentials_comments]):
            raise ValueError("❌ ERROR CRÍTICO: Faltan credenciales en las variables de entorno.")

        # --- 2. PARÁMETROS DE OPERACIÓN ---
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.max_respuestas_por_ejecucion = 50

        # --- 3. INICIALIZACIÓN DE APIs ---
        self.model = self.configurar_gemini()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # --- 4. PERSISTENCIA MEJORADA ---
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"✅ Bot inicializado.")
        print(f"📝 {len(self.comentarios_ya_respondidos)} comentarios respondidos en BD")
        print(f"🧠 {len(self.memoria_conversacion_usuario)} usuarios con historial")

    def configurar_gemini(self) -> genai.GenerativeModel:
        """Configura y devuelve el cliente de la API de Gemini."""
        try:
            print("🤖 Configurando Gemini AI...")
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("   ✅ Gemini configurado.")
            return model
        except Exception as e:
            print(f"❌ Error configurando Gemini: {e}")
            raise

    def configurar_youtube_lectura(self):
        """Configura el cliente de YouTube para lectura (usando API Key)."""
        try:
            print("📖 Configurando YouTube API para Lectura...")
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ API de Lectura configurada.")
            return youtube
        except Exception as e:
            print(f"❌ Error configurando API de Lectura de YouTube: {e}")
            raise

    def configurar_youtube_oauth(self):
        """Configura el cliente de YouTube para escritura (usando OAuth)."""
        try:
            print("📝 Configurando YouTube API para Escritura (OAuth)...")
            creds_data = json.loads(self.youtube_credentials_comments)
            creds = Credentials.from_authorized_user_info(creds_data)
            youtube = build('youtube', 'v3', credentials=creds)
            print("   ✅ API de Escritura configurada.")
            return youtube
        except Exception as e:
            print(f"❌ Error configurando OAuth de YouTube: {e}")
            raise

    def cargar_db_respondidos(self) -> Set[str]:
        """Carga los IDs de los comentarios ya respondidos desde archivo de texto."""
        if not os.path.exists(self.db_respondidos_path):
            return set()
        try:
            with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
                return {line.strip() for line in f}
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo leer BD de respondidos: {e}")
            return set()

    def guardar_en_db_respondidos(self, comment_id: str):
        """Añade un nuevo ID de comentario a la BD y al set en memoria."""
        try:
            with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
                f.write(f"{comment_id}\n")
            self.comentarios_ya_respondidos.add(comment_id)
        except Exception as e:
            print(f"⚠️  Error guardando en BD respondidos: {e}")

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
        """
        Carga la memoria persistente de conversaciones desde archivo JSON.
        Estructura: {
            "autor_id": {
                "nombre": "Nombre del Usuario",
                "mensajes": ["mensaje1", "mensaje2", ...],
                "ultima_interaccion": "2025-09-08T10:30:00"
            }
        }
        """
        if not os.path.exists(self.db_conversaciones_path):
            return {}
        
        try:
            with open(self.db_conversaciones_path, 'r', encoding='utf-8') as f:
                memoria_cruda = json.load(f)
            
            # Limpiar conversaciones muy antiguas (más de 90 días)
            memoria_limpia = {}
            fecha_limite = datetime.now() - timedelta(days=90)
            
            for autor_id, datos in memoria_cruda.items():
                try:
                    ultima_fecha = datetime.fromisoformat(datos['ultima_interaccion'])
                    if ultima_fecha > fecha_limite:
                        memoria_limpia[autor_id] = datos
                except:
                    # Si hay error en fecha, conservar el registro
                    memoria_limpia[autor_id] = datos
            
            conversaciones_eliminadas = len(memoria_cruda) - len(memoria_limpia)
            if conversaciones_eliminadas > 0:
                print(f"🧹 Limpieza: {conversaciones_eliminadas} conversaciones antiguas eliminadas")
            
            return memoria_limpia
            
        except Exception as e:
            print(f"⚠️  Error cargando memoria de conversaciones: {e}")
            return {}

    def guardar_memoria_conversaciones(self):
        """Guarda la memoria de conversaciones en archivo JSON."""
        try:
            with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
                json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando memoria de conversaciones: {e}")

    def actualizar_memoria_usuario(self, autor_id: str, autor_nombre: str, nuevo_mensaje: str):
        """Actualiza la memoria de conversación de un usuario específico."""
        if autor_id not in self.memoria_conversacion_usuario:
            self.memoria_conversacion_usuario[autor_id] = {
                "nombre": autor_nombre,
                "mensajes": [],
                "ultima_interaccion": datetime.now().isoformat()
            }
        
        # Actualizar datos
        self.memoria_conversacion_usuario[autor_id]["nombre"] = autor_nombre  # Actualizar si cambió
        self.memoria_conversacion_usuario[autor_id]["mensajes"].append(nuevo_mensaje)
        self.memoria_conversacion_usuario[autor_id]["ultima_interaccion"] = datetime.now().isoformat()
        
        # Limitar historial a últimos 5 mensajes por usuario para no saturar la IA
        if len(self.memoria_conversacion_usuario[autor_id]["mensajes"]) > 5:
            self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
                self.memoria_conversacion_usuario[autor_id]["mensajes"][-5:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        """Obtiene el historial de mensajes previos de un usuario."""
        if autor_id in self.memoria_conversacion_usuario:
            return self.memoria_conversacion_usuario[autor_id]["mensajes"]
        return []
    
    def obtener_videos_recientes(self) -> List[Dict]:
        """Obtiene videos más recientes del canal."""
        try:
            channel_response = self.youtube_lectura.channels().list(part='contentDetails', id=self.channel_id).execute()
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            playlist_items = self.youtube_lectura.playlistItems().list(
                part='snippet', playlistId=uploads_id, maxResults=15
            ).execute()
            
            videos = [{
                'id': item['snippet']['resourceId']['videoId'],
                'titulo': item['snippet']['title']
            } for item in playlist_items.get('items', [])]
            
            print(f"📹 Encontrados {len(videos)} videos recientes para analizar.")
            return videos
        except Exception as e:
            print(f"⚠️  No se pudieron obtener videos: {e}")
            return []
    
    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
        """
        Obtiene comentarios de un video, filtrando ya respondidos.
        IMPORTANTE: Luego se ordenarán por fecha (más recientes primero).
        """
        comentarios = []
        try:
            response = self.youtube_lectura.commentThreads().list(
                part='snippet', videoId=video_id, order='time', maxResults=100, textFormat='plainText'
            ).execute()
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                if comment_id in self.comentarios_ya_respondidos:
                    continue
                if item['snippet']['totalReplyCount'] > 0:  # Ya tiene respuestas
                    continue

                comentario_snippet = item['snippet']['topLevelComment']['snippet']
                
                # Manejar caso donde authorChannelId puede no existir
                autor_id = None
                if 'authorChannelId' in comentario_snippet and comentario_snippet['authorChannelId']:
                    autor_id = comentario_snippet['authorChannelId']['value']
                else:
                    # Usar authorDisplayName como fallback si no hay authorChannelId
                    autor_id = f"fallback_{comentario_snippet['authorDisplayName']}"
                
                comentarios.append({
                    'id': comment_id,
                    'texto': comentario_snippet['textDisplay'],
                    'autor_nombre': comentario_snippet['authorDisplayName'],
                    'autor_id': autor_id,
                    'video_titulo': video_titulo,
                    'fecha': datetime.fromisoformat(comentario_snippet['publishedAt'].replace('Z', '+00:00'))
                })
            return comentarios
        except Exception as e:
            print(f"⚠️  Error obteniendo comentarios del video: {e}")
            return []

    def es_comentario_valido(self, texto: str) -> bool:
        """Filtro de calidad para descartar spam."""
        if len(texto) > 800: return False
        if re.search(r'http[s]?://|www\.', texto, re.IGNORECASE): return False
        if texto.isdigit() and len(texto) > 10: return False
        if len(texto.strip()) < 5: return False  # Muy corto
        return True

    def detectar_tipo_comentario(self, texto: str) -> str:
        """Clasifica el comentario para estrategia de respuesta."""
        texto_lower = texto.lower()
        
        # Crisis (se ignora por seguridad)
        crisis = ['no aguanto', 'me quiero morir', 'suicidio', 'quiero morirme']
        if any(p in texto_lower for p in crisis): return 'crisis'
        
        # Texto incoherente o muy confuso
        palabras_largas_y_raras = re.findall(r'\b\w{18,}\b', texto)
        if len(palabras_largas_y_raras) > 0: return 'incoherente_o_confuso'

        # Hostilidad o duda
        hostilidad = ['mentira', 'falso', 'chantas', 'estafa', 'no es cierto', 'jamas ruego', 'no confio']
        if any(p in texto_lower for p in hostilidad): return 'duda_hostilidad'
        
        # Saludo simple
        if len(texto.split()) <= 3 and len(texto) < 20: return 'saludo'

        # Peticiones de abundancia/prosperidad
        abundancia = ['dinero', 'trabajo', 'empleo', 'prosperidad', 'negocio', 'loteria']
        if any(p in texto_lower for p in abundancia): return 'abundancia'
        
        # Dolor emocional
        dolor = ['dolor', 'lloro', 'sufro', 'triste', 'no siento', 'perdida', 'confundida']
        if any(p in texto_lower for p in dolor): return 'dolor_confusion'

        return 'general'

    def generar_respuesta_ia(self, comentario_actual: str, contexto_previo: List[str], tipo: str, info_comentario: Dict) -> str:
        """Genera respuesta usando IA con contexto completo."""
        if tipo == 'crisis':
            print(f"🚫 Detectada crisis en comentario de '{info_comentario['autor_nombre']}'. Ignorado por seguridad.")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None

        # Construir historial de contexto
        historial_str = ""
        if contexto_previo:
            historial_str = f"\nHistorial previo con {info_comentario['autor_nombre']}:\n"
            for i, msg in enumerate(contexto_previo, 1):
                historial_str += f"{i}. \"{msg}\"\n"
            historial_str += "---\n"

        prompt_base = f"""Eres un asistente espiritual del canal "Prosperidad Divina". Tu tono es empático, positivo y espiritual.

INFORMACIÓN DEL USUARIO:
- Nombre: {info_comentario['autor_nombre']}
- Video: "{info_comentario['video_titulo']}"

{historial_str}
COMENTARIO NUEVO A RESPONDER: "{comentario_actual}"
"""
        
        instrucciones_por_tipo = {
            'incoherente_o_confuso': """El comentario es difícil de leer, pero responde a la EMOCIÓN que intuyes. No corrijas el texto. Si parece positivo: "Sentimos la energía de tu corazón. Te enviamos luz y bendiciones ✨🙏". Si parece doloroso: "Aunque las palabras sean difíciles, sentimos tu corazón. Te enviamos paz y luz 💖🙏".""",
            
            'duda_hostilidad': """El usuario expresa dolor/desconfianza. NO debatas. Valida sus sentimientos ("Leemos el dolor en tus palabras...") y ofrece paz incondicionalmente ("Deseamos que encuentres paz y sanación en tu camino."). Sé breve y compasivo.""",
            
            'saludo': """Responde con una bendición breve y cálida. Varía tus respuestas entre: "Bendiciones de luz en tu camino ✨", "Que la paz divina te acompañe 🙏", etc.""",
            
            'abundancia': """Reconoce su deseo de prosperidad y ofrece bendiciones específicas: "Que la abundancia divina se manifieste en tu vida de formas hermosas. Visualiza ya la prosperidad llegando a ti. 💰✨".""",
            
            'dolor_confusion': """Reconoce su dolor con compasión ("Siento la tristeza en tu mensaje...") y ofrece consuelo espiritual ("Que la luz divina sane tu corazón y traiga claridad a tu camino. No estás sol@. 💙🙏").""",
            
            'general': """Responde al sentimiento del comentario con calidez espiritual. Mantén coherencia con conversaciones previas si las hay."""
        }

        prompt_final = prompt_base + "\nINSTRUCCIONES ESPECÍFICAS: " + instrucciones_por_tipo.get(tipo, instrucciones_por_tipo['general'])
        prompt_final += "\n\nResponde en máximo 2-3 líneas, con emojis espirituales apropiados."

        try:
            print(f"   🧠 Enviando a IA (tipo: {tipo}) con {len(contexto_previo)} mensaje(s) de contexto.")
            response = self.model.generate_content(
                prompt_final, 
                generation_config=genai.types.GenerationConfig(temperature=0.8)
            )
            respuesta_limpia = response.text.strip().replace('"', '')
            
            if tipo in self.stats['tipos_de_respuesta_enviada']:
                self.stats['tipos_de_respuesta_enviada'][tipo] += 1
            
            return respuesta_limpia
        except Exception as e:
            print(f"   ⚠️  Error en API de Gemini: {e}")
            self.stats['resumen']['errores_api'] += 1
            return "Que la paz y la luz divina te acompañen siempre. Bendiciones. 🙏✨"

    def responder_comentario(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        """Envía respuesta a YouTube y actualiza BD si exitoso."""
        try:
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={'snippet': {'parentId': comentario_id, 'textOriginal': respuesta}}
            ).execute()
            print(f"   ✅ Respuesta enviada a '{autor_nombre}'.")
            self.guardar_en_db_respondidos(comentario_id)
            return True
        except HttpError as e:
            print(f"   ❌ ERROR HTTP respondiendo a '{autor_nombre}': {e.content.decode('utf-8')}")
            self.stats['resumen']['errores_api'] += 1
            return False

    def inicializar_estadisticas(self):
        """Inicializa diccionario de estadísticas."""
        return {
            'info_ejecucion': {
                'id': self.run_id, 
                'inicio': datetime.now().isoformat(), 
                'fin': None, 
                'duracion_segundos': None
            },
            'resumen': {
                'comentarios_procesados': 0, 
                'respuestas_exitosas': 0, 
                'errores_api': 0, 
                'comentarios_filtrados': 0,
                'usuarios_con_historial': len(self.memoria_conversacion_usuario)
            },
            'tipos_de_respuesta_enviada': {
                'abundancia': 0, 'saludo': 0, 'duda_hostilidad': 0, 'dolor_confusion': 0,
                'incoherente_o_confuso': 0, 'general': 0
            },
            'acciones_de_moderacion': {'crisis_ignorada': 0}
        }

    def generar_reporte_final(self):
        """Genera reporte JSON y muestra resumen."""
        fin_dt = datetime.now()
        self.stats['info_ejecucion']['fin'] = fin_dt.isoformat()
        duracion = (fin_dt - datetime.fromisoformat(self.stats['info_ejecucion']['inicio'])).total_seconds()
        self.stats['info_ejecucion']['duracion_segundos'] = round(duracion, 2)
        self.stats['resumen']['usuarios_con_historial'] = len(self.memoria_conversacion_usuario)

        nombre_archivo = f"reporte_{self.run_id}.json"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("📊 REPORTE FINAL DE EJECUCIÓN")
        print("="*80)
        print(f"🆔 ID: {self.run_id} | ⏱️  Duración: {self.stats['info_ejecucion']['duracion_segundos']}s")
        print(f"📁 Reporte guardado: {nombre_archivo}")
        print("\n--- RESUMEN ---")
        print(f"   📝 Comentarios Procesados: {self.stats['resumen']['comentarios_procesados']}")
        print(f"   ✅ Respuestas Enviadas: {self.stats['resumen']['respuestas_exitosas']}")
        print(f"   👤 Ya Respondidos Manualmente: {self.stats['resumen']['comentarios_ya_respondidos_manualmente']}")
        print(f"   🧠 Usuarios con Historial: {self.stats['resumen']['usuarios_con_historial']}")
        print(f"   🚫 Comentarios Filtrados: {self.stats['resumen']['comentarios_filtrados']}")
        print(f"   ❌ Errores API: {self.stats['resumen']['errores_api']}")
        
        if any(self.stats['tipos_de_respuesta_enviada'].values()):
            print("\n--- TIPOS DE RESPUESTA ---")
            for tipo, cantidad in self.stats['tipos_de_respuesta_enviada'].items():
                if cantidad > 0: 
                    print(f"   - {tipo.replace('_', ' ').title()}: {cantidad}")

        print(f"\n--- MODERACIÓN ---")
        print(f"   🚫 Crisis Ignoradas: {self.stats['acciones_de_moderacion']['crisis_ignorada']}")
        print("="*80)

    def ejecutar(self):
        """Proceso principal del bot."""
        print("\n▶️  INICIANDO CICLO DE PROCESAMIENTO...")
        
        respuestas_enviadas = 0
        videos = self.obtener_videos_recientes()

        for video in videos:
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
            
            print(f"\n🔍 Analizando video: '{video['titulo'][:50]}...'")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            # ✅ ORDENAR DE MÁS RECIENTE A MÁS ANTIGUO
            comentarios.sort(key=lambda c: c['fecha'], reverse=True)
            print(f"   📝 {len(comentarios)} comentarios nuevos encontrados (ordenados por fecha descendente)")

            for comentario in comentarios:
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    print(f"\n✋ Límite de {self.max_respuestas_por_ejecucion} respuestas alcanzado.")
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                if not self.es_comentario_valido(comentario['texto']):
                    print(f"⏭️  Comentario de '{comentario['autor_nombre']}' filtrado.")
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue

                autor_id = comentario['autor_id']
                autor_nombre = comentario['autor_nombre']
                texto_actual = comentario['texto']
                
                # Obtener contexto previo del usuario
                contexto_previo = self.obtener_contexto_usuario(autor_id)

                print("\n" + "-"*80)
                print(f"💬 Procesando #{respuestas_enviadas + 1}: '{autor_nombre}'")
                print(f"   📅 Fecha: {comentario['fecha'].strftime('%d/%m/%Y %H:%M')}")
                print(f"   💭 Texto: \"{texto_actual[:70]}...\"")
                print(f"   🧠 Contexto previo: {len(contexto_previo)} mensaje(s)")
                
                tipo = self.detectar_tipo_comentario(texto_actual)
                respuesta = self.generar_respuesta_ia(texto_actual, contexto_previo, tipo, comentario)

                if respuesta:
                    if self.responder_comentario(comentario['id'], respuesta, autor_nombre):
                        self.stats['resumen']['respuestas_exitosas'] += 1
                        respuestas_enviadas += 1
                        
                        # ✅ ACTUALIZAR MEMORIA DEL USUARIO
                        self.actualizar_memoria_usuario(autor_id, autor_nombre, texto_actual)
                        print(f"   🧠 Memoria actualizada para '{autor_nombre}'")

                time.sleep(5)  # Rate limiting
        
        # ✅ GUARDAR MEMORIA DE CONVERSACIONES
        self.guardar_memoria_conversaciones()
        print(f"\n💾 Memoria de conversaciones guardada: {len(self.memoria_conversacion_usuario)} usuarios")
        
        self.generar_reporte_final()

if __name__ == "__main__":
    try:
        bot = ProsperidadDivinaBotPersistente()
        bot.ejecutar()
    except Exception as e:
        print("\n❌ ERROR CRÍTICO:")
        print(traceback.format_exc())
