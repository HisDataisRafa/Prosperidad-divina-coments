#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN PRUEBA (10 COMENTARIOS)
Fecha: 08 de Septiembre de 2025

🧪 CONFIGURACIÓN DE PRUEBA:
- ✅ Solo 10 comentarios por ejecución (10 minutos total)
- ✅ 1 request por minuto a Gemini
- ✅ Perfecto para verificar que todo funciona
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

class ProsperidadDivinaBotPrueba:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*80)
        print(f"👑 BOT PROSPERIDAD DIVINA - VERSIÓN PRUEBA (10 COMENTARIOS)")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. CONFIGURACIÓN ---
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A"
        if not all([self.gemini_api_key, self.youtube_credentials_comments]):
            raise ValueError("❌ ERROR CRÍTICO: Faltan credenciales en las variables de entorno.")

        # --- 2. PARÁMETROS DE PRUEBA ---
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.max_respuestas_por_ejecucion = 10  # 🧪 PRUEBA: Solo 10 comentarios

        # --- 3. INICIALIZACIÓN DE APIs ---
        self.model = self.configurar_gemini()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # --- 4. PERSISTENCIA ---
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"✅ Bot inicializado - MODO PRUEBA")
        print(f"📝 {len(self.comentarios_ya_respondidos)} comentarios respondidos en BD")
        print(f"🧠 {len(self.memoria_conversacion_usuario)} usuarios con historial")

    def configurar_gemini(self) -> genai.GenerativeModel:
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
        try:
            print("📖 Configurando YouTube API para Lectura...")
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ API de Lectura configurada.")
            return youtube
        except Exception as e:
            print(f"❌ Error configurando API de Lectura de YouTube: {e}")
            raise

    def configurar_youtube_oauth(self):
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
        if not os.path.exists(self.db_respondidos_path):
            return set()
        try:
            with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
                return {line.strip() for line in f}
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo leer BD de respondidos: {e}")
            return set()

    def guardar_en_db_respondidos(self, comment_id: str):
        try:
            with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
                f.write(f"{comment_id}\n")
            self.comentarios_ya_respondidos.add(comment_id)
        except Exception as e:
            print(f"⚠️  Error guardando en BD respondidos: {e}")

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
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
                    memoria_limpia[autor_id] = datos
            
            conversaciones_eliminadas = len(memoria_cruda) - len(memoria_limpia)
            if conversaciones_eliminadas > 0:
                print(f"🧹 Limpieza: {conversaciones_eliminadas} conversaciones antiguas eliminadas")
            
            return memoria_limpia
            
        except Exception as e:
            print(f"⚠️  Error cargando memoria de conversaciones: {e}")
            return {}

    def guardar_memoria_conversaciones(self):
        try:
            with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
                json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Error guardando memoria de conversaciones: {e}")

    def actualizar_memoria_usuario(self, autor_id: str, autor_nombre: str, nuevo_mensaje: str):
        if autor_id not in self.memoria_conversacion_usuario:
            self.memoria_conversacion_usuario[autor_id] = {
                "nombre": autor_nombre,
                "mensajes": [],
                "ultima_interaccion": datetime.now().isoformat()
            }
        
        self.memoria_conversacion_usuario[autor_id]["nombre"] = autor_nombre
        self.memoria_conversacion_usuario[autor_id]["mensajes"].append(nuevo_mensaje)
        self.memoria_conversacion_usuario[autor_id]["ultima_interaccion"] = datetime.now().isoformat()
        
        if len(self.memoria_conversacion_usuario[autor_id]["mensajes"]) > 5:
            self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
                self.memoria_conversacion_usuario[autor_id]["mensajes"][-5:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        if autor_id in self.memoria_conversacion_usuario:
            return self.memoria_conversacion_usuario[autor_id]["mensajes"]
        return []
    
    def obtener_videos_recientes(self) -> List[Dict]:
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
        comentarios = []
        try:
            response = self.youtube_lectura.commentThreads().list(
                part='snippet', videoId=video_id, order='time', maxResults=100, textFormat='plainText'
            ).execute()
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                
                # 1️⃣ Verificar si el bot ya respondió (base de datos local)
                if comment_id in self.comentarios_ya_respondidos:
                    continue
                
                # 2️⃣ Verificar si ALGUIEN (manual o bot) ya respondió
                total_replies = item['snippet']['totalReplyCount']
                if total_replies > 0:
                    print(f"   ⏭️  Comentario ya tiene {total_replies} respuesta(s) - ignorando")
                    self.guardar_en_db_respondidos(comment_id)
                    self.stats['resumen']['comentarios_ya_respondidos_manualmente'] += 1
                    continue

                comentario_snippet = item['snippet']['topLevelComment']['snippet']
                
                autor_id = None
                if 'authorChannelId' in comentario_snippet and comentario_snippet['authorChannelId']:
                    autor_id = comentario_snippet['authorChannelId']['value']
                else:
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
        if len(texto) > 800: return False
        if re.search(r'http[s]?://|www\.', texto, re.IGNORECASE): return False
        if texto.isdigit() and len(texto) > 10: return False
        if len(texto.strip()) < 5: return False
        return True

    def detectar_tipo_comentario(self, texto: str) -> str:
        texto_lower = texto.lower()
        
        crisis = ['no aguanto', 'me quiero morir', 'suicidio', 'quiero morirme']
        if any(p in texto_lower for p in crisis): return 'crisis'
        
        palabras_largas_y_raras = re.findall(r'\b\w{18,}\b', texto)
        if len(palabras_largas_y_raras) > 0: return 'incoherente_o_confuso'

        hostilidad = ['mentira', 'falso', 'chantas', 'estafa', 'no es cierto', 'jamas ruego', 'no confio']
        if any(p in texto_lower for p in hostilidad): return 'duda_hostilidad'
        
        if len(texto.split()) <= 3 and len(texto) < 20: return 'saludo'

        abundancia = ['dinero', 'trabajo', 'empleo', 'prosperidad', 'negocio', 'loteria']
        if any(p in texto_lower for p in abundancia): return 'abundancia'
        
        dolor = ['dolor', 'lloro', 'sufro', 'triste', 'no siento', 'perdida', 'confundida']
        if any(p in texto_lower for p in dolor): return 'dolor_confusion'

        return 'general'

    def generar_respuesta_ia(self, comentario_actual: str, contexto_previo: List[str], tipo: str, info_comentario: Dict) -> str:
        if tipo == 'crisis':
            print(f"🚫 Detectada crisis en comentario de '{info_comentario['autor_nombre']}'. Ignorado por seguridad.")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None

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
            
            # 🧪 RATE LIMITING PRUEBA: 1 request por minuto
            print(f"   ⏳ Esperando 60 segundos (rate limiting 1/minuto)...")
            time.sleep(60)
            
            response = self.model.generate_content(
                prompt_final, 
                generation_config=genai.types.GenerationConfig(temperature=0.8)
            )
            respuesta_limpia = response.text.strip().replace('"', '')
            
            if tipo in self.stats['tipos_de_respuesta_enviada']:
                self.stats['tipos_de_respuesta_enviada'][tipo] += 1
            
            print(f"   ✅ Respuesta generada por IA exitosamente")
            return respuesta_limpia
            
        except Exception as e:
            print(f"   ⚠️  Error en API de Gemini: {e}")
            self.stats['resumen']['errores_api'] += 1
            
            respuestas_fallback = {
                'saludo': "Bendiciones y luz en tu camino 🙏✨",
                'abundancia': "Que la prosperidad divina florezca en tu vida 💰🙏",
                'dolor_confusion': "Que la paz divina sane tu corazón. No estás sol@ 💙🙏",
                'duda_hostilidad': "Enviamos luz y comprensión a tu camino 🕯️🙏",
                'general': "Que la paz y la luz divina te acompañen siempre. Bendiciones 🙏✨"
            }
            return respuestas_fallback.get(tipo, respuestas_fallback['general'])

    def responder_comentario(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
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
        return {
            'info_ejecucion': {
                'id': self.run_id, 
                'inicio': datetime.now().isoformat(), 
                'fin': None, 
                'duracion_segundos': None,
                'modo': 'PRUEBA_10_COMENTARIOS'
            },
            'resumen': {
                'comentarios_procesados': 0, 
                'respuestas_exitosas': 0, 
                'errores_api': 0, 
                'comentarios_filtrados': 0,
                'comentarios_ya_respondidos_manualmente': 0,
                'usuarios_con_historial': len(self.memoria_conversacion_usuario)
            },
            'tipos_de_respuesta_enviada': {
                'abundancia': 0, 'saludo': 0, 'duda_hostilidad': 0, 'dolor_confusion': 0,
                'incoherente_o_confuso': 0, 'general': 0
            },
            'acciones_de_moderacion': {'crisis_ignorada': 0}
        }

    def generar_reporte_final(self):
        fin_dt = datetime.now()
        self.stats['info_ejecucion']['fin'] = fin_dt.isoformat()
        duracion = (fin_dt - datetime.fromisoformat(self.stats['info_ejecucion']['inicio'])).total_seconds()
        self.stats['info_ejecucion']['duracion_segundos'] = round(duracion, 2)
        self.stats['resumen']['usuarios_con_historial'] = len(self.memoria_conversacion_usuario)

        nombre_archivo = f"reporte_prueba_{self.run_id}.json"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=4, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("📊 REPORTE FINAL - PRUEBA (10 COMENTARIOS)")
        print("="*80)
        print(f"🆔 ID: {self.run_id} | ⏱️  Duración: {self.stats['info_ejecucion']['duracion_segundos']}s")
        print(f"📁 Reporte guardado: {nombre_archivo}")
        print("\n--- RESUMEN PRUEBA ---")
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
        
        if self.stats['resumen']['respuestas_exitosas'] > 0:
            print(f"\n🎉 ¡PRUEBA EXITOSA! Bot funcionando correctamente.")
            print(f"💡 Listo para activar modo producción (60 comentarios)")
        else:
            print(f"\n⚠️  Sin respuestas enviadas. Revisar configuración de APIs.")
            
        print("="*80)

    def ejecutar(self):
        print("\n▶️  INICIANDO CICLO DE PRUEBA (10 comentarios máximo)...")
        inicio_ejecucion = datetime.now()
        
        respuestas_enviadas = 0
        videos = self.obtener_videos_recientes()

        for video in videos:
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
            
            print(f"\n🔍 Analizando video: '{video['titulo'][:50]}...'")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            comentarios.sort(key=lambda c: c['fecha'], reverse=True)
            print(f"   📝 {len(comentarios)} comentarios nuevos encontrados")
            
            if not comentarios:
                print(f"   ℹ️  No hay comentarios nuevos en este video")
                continue

            for comentario in comentarios:
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    tiempo_transcurrido = (datetime.now() - inicio_ejecucion).total_seconds() / 60
                    print(f"\n✋ Límite de PRUEBA alcanzado: {self.max_respuestas_por_ejecucion} respuestas en {tiempo_transcurrido:.1f} minutos.")
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                if not self.es_comentario_valido(comentario['texto']):
                    print(f"⏭️  Comentario de '{comentario['autor_nombre']}' filtrado.")
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue

                autor_id = comentario['autor_id']
                autor_nombre = comentario['autor_nombre']
                texto_actual = comentario['texto']
                
                contexto_previo = self.obtener_contexto_usuario(autor_id)

                print("\n" + "-"*60)
                print(f"💬 PRUEBA #{respuestas_enviadas + 1}: '{autor_nombre}'")
                print(f"   📅 Fecha: {comentario['fecha'].strftime('%d/%m/%Y %H:%M')}")
                print(f"   💭 Texto: \"{texto_actual[:50]}...\"")
                print(f"   🧠 Contexto previo: {len(contexto_previo)} mensaje(s)")
                
                tipo = self.detectar_tipo_comentario(texto_actual)
                respuesta = self.generar_respuesta_ia(texto_actual, contexto_previo, tipo, comentario)

                if respuesta:
                    if self.responder_comentario(comentario['id'], respuesta, autor_nombre):
                        self.stats['resumen']['respuestas_exitosas'] += 1
                        respuestas_enviadas += 1
                        
                        self.actualizar_memoria_usuario(autor_id, autor_nombre, texto_actual)
                        print(f"   🧠 Memoria actualizada para '{autor_nombre}'")
        
        self.guardar_memoria_conversaciones()
        print(f"\n💾 Memoria de conversaciones guardada: {len(self.memoria_conversacion_usuario)} usuarios")
        
        self.generar_reporte_final()

if __name__ == "__main__":
    try:
        bot = ProsperidadDivinaBotPrueba()
        bot.ejecutar()
    except Exception as e:
        print("\n❌ ERROR CRÍTICO EN PRUEBA:")
        print(traceback.format_exc())
