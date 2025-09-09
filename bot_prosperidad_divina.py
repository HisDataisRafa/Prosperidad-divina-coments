#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN CORDIAL Y POSITIVA (V3 COMPLETA)
Fecha: 09 de Septiembre de 2025

MEJORAS PRINCIPALES:
- ✅ Respuestas siempre cordiales y positivas
- ✅ Bendiciones genuinas sin confrontación
- ✅ Tono cálido incluso con escépticos
- ✅ Evita frases que suenen condescendientes
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
        print(f"🎯 BOT PROSPERIDAD DIVINA - VERSIÓN CORDIAL Y POSITIVA (V3)")
        print(f"🆔 ID de Ejecución: {self.run_id}")
        print("="*80)

        # --- 1. VERIFICACIÓN DE CREDENCIALES ---
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A" # Se recomienda usar una variable de entorno también
        
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
        self.max_respuestas_por_ejecucion = 17
        self.rate_limit_seconds = 15

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
        print("="*80)

    def configurar_gemini_flash_lite(self) -> genai.GenerativeModel:
        try:
            print("\n🤖 CONFIGURANDO GEMINI 2.5 FLASH-LITE...")
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            print("   🧪 Realizando prueba de conexión...")
            print(f"   ⏱️  Aplicando pausa inicial de {self.rate_limit_seconds}s...")
            time.sleep(self.rate_limit_seconds)
            
            test_response = model.generate_content("Responde exactamente: 'Configuración cordial lista'")
            
            if "cordial lista" in test_response.text.strip().lower():
                print("   🎉 ¡ÉXITO! Gemini Flash-Lite configurado.")
            else:
                print(f"   ⚠️  ADVERTENCIA: Respuesta inesperada: '{test_response.text.strip()}'")
            return model
        except Exception as e:
            print(f"   ❌ ERROR FATAL: {type(e).__name__} - {str(e)}")
            raise

    def configurar_youtube_lectura(self):
        try:
            print("\n📖 CONFIGURANDO YOUTUBE API (Lectura)...")
            service = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("   ✅ YouTube API configurada correctamente.")
            return service
        except Exception as e:
            print(f"   ❌ Error: {e}")
            raise e

    def configurar_youtube_oauth(self):
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
        if not os.path.exists(self.db_respondidos_path):
            return set()
        
        with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
            respondidos = {line.strip() for line in f if line.strip()}
        print(f"   📊 {len(respondidos)} comentarios ya respondidos.")
        return respondidos

    def guardar_en_db_respondidos(self, comment_id: str):
        with open(self.db_respondidos_path, 'a', encoding='utf-8') as f:
            f.write(f"{comment_id}\n")
        self.comentarios_ya_respondidos.add(comment_id)

    def cargar_memoria_conversaciones(self) -> Dict[str, Dict]:
        if not os.path.exists(self.db_conversaciones_path):
            return {}
        
        with open(self.db_conversaciones_path, 'r', encoding='utf-8') as f:
            memoria = json.load(f)
        print(f"   🧠 Memoria de {len(memoria)} usuarios cargada.")
        return memoria

    def guardar_memoria_conversaciones(self):
        with open(self.db_conversaciones_path, 'w', encoding='utf-8') as f:
            json.dump(self.memoria_conversacion_usuario, f, indent=2, ensure_ascii=False)

    def actualizar_memoria_usuario(self, autor_id: str, autor_nombre: str, nuevo_mensaje: str):
        if autor_id not in self.memoria_conversacion_usuario:
            self.memoria_conversacion_usuario[autor_id] = {
                "nombre": autor_nombre,
                "mensajes": []
            }
        
        self.memoria_conversacion_usuario[autor_id]["mensajes"].append({
            "texto": nuevo_mensaje,
            "fecha": datetime.now().isoformat()
        })
        
        self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
            self.memoria_conversacion_usuario[autor_id]["mensajes"][-3:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        if autor_id not in self.memoria_conversacion_usuario:
            return []
        return [msg["texto"] for msg in self.memoria_conversacion_usuario[autor_id]["mensajes"]]

    def obtener_videos_recientes(self) -> List[Dict]:
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
            
            videos = [{'id': item['snippet']['resourceId']['videoId'],
                       'titulo': item['snippet']['title'],
                       'fecha': item['snippet']['publishedAt']}
                      for item in playlist_items.get('items', [])]
            
            print(f"   ✅ {len(videos)} videos encontrados.")
            return videos
            
        except Exception as e:
            print(f"   ❌ Error obteniendo videos: {e}")
            return []

    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
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
                
                if comment_id in self.comentarios_ya_respondidos or item['snippet']['totalReplyCount'] > 0:
                    continue
                
                snippet = item['snippet']['topLevelComment']['snippet']
                autor_id = snippet.get('authorChannelId', {}).get('value', f"fallback_{snippet['authorDisplayName']}")
                
                comentarios_nuevos.append({
                    'id': comment_id,
                    'texto': snippet['textDisplay'],
                    'autor_nombre': snippet['authorDisplayName'],
                    'autor_id': autor_id,
                    'video_titulo': video_titulo,
                    'fecha': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                })
            
            print(f"      📊 {len(comentarios_nuevos)} comentarios nuevos.")
            return comentarios_nuevos
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []
            
    def es_comentario_valido(self, texto: str) -> bool:
        if not texto or len(texto.strip()) <= 3 or len(texto.strip()) > 500:
            return False
        if re.search(r'http[s]?://', texto, re.IGNORECASE):
            return False
        return True

    # --- INICIO DE LÓGICA V3 MEJORADA ---

    def detectar_tipo_comentario_mejorado(self, texto: str, titulo_video: str = "") -> Dict:
        """
        Detecta el tipo y tono del comentario con análisis mejorado.
        Retorna un diccionario con tipo, tono y elementos detectados.
        """
        texto_lower = texto.lower()
        titulo_lower = titulo_video.lower() if titulo_video else ""
        
        resultado = {
            'tipo': 'general',
            'tono': 'neutro',
            'menciona_titulo': False,
            'menciona_figura_religiosa': False,
            'es_pregunta': '?' in texto,
            'es_respuesta_a_titulo': False,
            'requiere_respuesta_suave': False,
            'elementos_detectados': []
        }
        
        palabras_titulo = set(re.findall(r'\w+', titulo_lower))
        palabras_comentario = set(re.findall(r'\w+', texto_lower))
        coincidencias = palabras_titulo & palabras_comentario
        
        negaciones = ['no', 'nunca', 'jamás', 'ni', 'tampoco', 'nada']
        if any(neg in texto_lower for neg in negaciones) and len(coincidencias) > 1:
            resultado['es_respuesta_a_titulo'] = True
            resultado['requiere_respuesta_suave'] = True
            resultado['tono'] = 'esceptico_suave'
        
        patrones_sarcasmo = [
            r'\bja+\b', r'\bjeje\b', r'\blol\b', r'\bxd\b',
            r'no creo', r'mentira', r'falso', r'estafa',
            r'otro planeta', r'marciano', r'extraterrestre'
        ]
        if any(re.search(patron, texto_lower) for patron in patrones_sarcasmo):
            resultado['tono'] = 'esceptico_suave'
            resultado['requiere_respuesta_suave'] = True
        
        palabras_crisis = ['no aguanto', 'suicidio', 'morir', 'matarme', 'acabar con todo']
        if any(word in texto_lower for word in palabras_crisis):
            resultado['tipo'] = 'crisis'
            resultado['tono'] = 'crisis'
            return resultado
        
        figuras_religiosas = [
            'dios', 'jesús', 'cristo', 'virgen', 'maría', 'arcángel', 
            'miguel', 'gabriel', 'rafael', 'ángel', 'espíritu santo', 'señor'
        ]
        for figura in figuras_religiosas:
            if figura in texto_lower:
                resultado['menciona_figura_religiosa'] = True
                resultado['elementos_detectados'].append(figura)
        
        if len(texto.split()) <= 5:
            resultado['tipo'] = 'comentario_breve' if resultado['requiere_respuesta_suave'] else 'saludo'
        
        if any(word in texto_lower for word in ['dinero', 'trabajo', 'abundancia', 'prosperidad', 'riqueza']):
            resultado['tipo'] = 'abundancia'
        
        if any(word in texto_lower for word in ['dolor', 'triste', 'depresión', 'ansiedad', 'solo', 'sufr']):
            resultado['tipo'] = 'dolor_confusion'
            resultado['tono'] = 'vulnerable'
        
        if any(word in texto_lower for word in ['gracias', 'bendiciones', 'amén', 'sí acepto', 'recibo']):
            resultado['tipo'] = 'gratitud'
            resultado['tono'] = 'positivo'
        
        return resultado

    def generar_respuesta_contextual_mejorada(self, comentario_actual: str, contexto_previo: List[str], 
                                             analisis: Dict, info_comentario: Dict) -> str:
        """
        Genera respuesta cordial y positiva, adaptada al contexto.
        """
        
        if analisis['tipo'] == 'crisis':
            print("      ⚠️  CRISIS - Comentario omitido.")
            self.stats['acciones_de_moderacion']['crisis_ignorada'] += 1
            return None
        
        try:
            contexto_str = ""
            if contexto_previo:
                contexto_str = ("Conversación previa:\n" + 
                               "\n".join(f"- {msg}" for msg in contexto_previo[-2:]) + "\n\n")
            
            instrucciones_especificas = self._generar_instrucciones_cordiales(analisis)
            
            prompt = f"""Eres un asistente espiritual muy cordial y amoroso del canal "Prosperidad Divina".
Tu misión es bendecir y llenar de amor a todos, sin importar su actitud.

{contexto_str}CONTEXTO:
- Usuario: {info_comentario['autor_nombre']}
- Comentario actual: "{comentario_actual}"

INSTRUCCIONES FUNDAMENTALES:
1. Sé SIEMPRE cordial, cálido y genuinamente amoroso.
2. Ofrece bendiciones sinceras y positivas a TODOS.
3. NO uses frases como "respeto tu perspectiva" o "respeto tu opinión" (suenan distantes).
4. En su lugar, usa bendiciones directas como "Dios te bendiga", "Bendiciones para ti", "Que tengas un hermoso día".
5. NO menciones el título del video a menos que el usuario lo haga.
6. Mantén un tono de amor incondicional.

{instrucciones_especificas}

EJEMPLOS DE RESPUESTAS CORDIALES:
- "Dios te bendiga abundantemente 🙏✨"
- "Que tengas un día maravilloso lleno de bendiciones 💫"
- "Bendiciones infinitas para ti y tu familia 🌟🙏"
- "Que la paz y el amor llenen tu corazón 💖✨"

FORMATO:
- Máximo 2 líneas cortas.
- Usa 1-2 emojis positivos (🙏✨💫🌟💖🕊️).
- Sé cálido y genuino. Transmite amor sincero.

Respuesta (cordial y amorosa):"""

            print(f"      🧠 Generando respuesta cordial... (pausa {self.rate_limit_seconds}s)")
            time.sleep(self.rate_limit_seconds)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=100, top_p=0.9),
                safety_settings=safety_settings
            )
            
            if not response or not response.text:
                raise ValueError("Respuesta vacía de la IA")
            
            respuesta_validada = self._validar_cordialidad(response.text.strip(), analisis)
            
            print(f"      ✅ Respuesta: \"{respuesta_validada[:50]}...\"")
            self.stats['resumen']['respuestas_ia_exitosas'] += 1
            return respuesta_validada
            
        except Exception as e:
            print(f"      ❌ Error IA: {type(e).__name__} - {e}")
            self.stats['resumen']['errores_gemini'] += 1
            return self._generar_fallback_cordial(analisis)
    
    def _generar_instrucciones_cordiales(self, analisis: Dict) -> str:
        instrucciones = []
        
        if analisis.get('requiere_respuesta_suave') or analisis['tono'] == 'esceptico_suave':
            instrucciones.append("RESPUESTA ESPECIALMENTE AMOROSA:\n- Este usuario puede estar escéptico. Dale una bendición extra cálida y sincera. NO confrontes. Simplemente bendícelo con amor genuino.\n- Ejemplos: \"Dios te bendiga grandemente 🙏✨\", \"Que tengas un día hermoso lleno de paz 💫\"")
        
        elif analisis['tono'] == 'vulnerable':
            instrucciones.append("USUARIO NECESITA CONSUELO:\n- Muestra compasión profunda y ofrece esperanza. Bendiciones reconfortantes.\n- Ejemplos: \"Dios te abraza en este momento 💖🙏\", \"Enviándote mucha fuerza y amor 💫\"")
        
        if analisis['menciona_figura_religiosa']:
            figuras = ', '.join(analisis['elementos_detectados'])
            instrucciones.append(f"FIGURAS MENCIONADAS: {figuras}\n- Puedes incluir estas figuras en tu bendición, manteniendo el tono amoroso.")

        if analisis['tipo'] == 'gratitud':
            instrucciones.append("USUARIO AGRADECIDO:\n- Multiplica sus bendiciones y agradece su hermoso corazón.")

        return '\n'.join(instrucciones)
    
    def _validar_cordialidad(self, respuesta: str, analisis: Dict) -> str:
        frases_evitar = ['respeto tu perspectiva', 'respeto tu opinión', 'entiendo tu punto']
        
        for frase in frases_evitar:
            if frase in respuesta.lower():
                return self._generar_fallback_cordial(analisis)
        
        if len(respuesta) < 20:
            return self._generar_fallback_cordial(analisis)
        
        return respuesta
    
    def _generar_fallback_cordial(self, analisis: Dict) -> str:
        bendiciones_universales = [
            "Dios te bendiga abundantemente 🙏✨",
            "Que tengas un día maravilloso lleno de bendiciones 💫",
            "Bendiciones infinitas para ti y tu familia 🌟🙏",
            "Que la paz y el amor llenen tu corazón 💖✨",
            "Que Dios ilumine siempre tu camino 🌟🙏"
        ]
        
        fallbacks_especificos = {
            'comentario_breve': ["Dios te bendiga grandemente 🙏✨", "Muchas bendiciones para ti 💫🙏"],
            'saludo': ["¡Bendiciones para ti también! 🙏✨", "¡Hola! Muchas bendiciones 🙏💖"],
            'abundancia': ["Que la prosperidad fluya abundantemente en tu vida 💫🙏", "Dios multiplique tus bendiciones 🌟✨"],
            'dolor_confusion': ["Dios te abraza con su amor infinito 💖🙏", "Enviándote mucha fuerza y paz 🕊️✨"],
            'gratitud': ["¡Que tus bendiciones se multipliquen! 🌟🙏", "Gracias a ti por tu hermoso corazón ✨💖"]
        }
        
        if analisis.get('requiere_respuesta_suave'):
            return random.choice(bendiciones_universales)
        
        tipo = analisis.get('tipo', 'general')
        opciones = fallbacks_especificos.get(tipo, []) + bendiciones_universales
        return random.choice(opciones)

    # --- FIN DE LÓGICA V3 MEJORADA ---

    def responder_comentario_800rpd(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        try:
            print(f"      📤 Enviando respuesta...")
            
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={'snippet': {'parentId': comentario_id, 'textOriginal': respuesta}}
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
        return {
            'info_ejecucion': {
                'id': self.run_id, 'inicio': datetime.now().isoformat(), 'modo': 'CORDIAL_Y_POSITIVO_V3',
                'modelo': 'gemini-2.5-flash-lite', 'max_comentarios': self.max_respuestas_por_ejecucion,
            },
            'resumen': {
                'comentarios_procesados': 0, 'respuestas_exitosas': 0, 'respuestas_ia_exitosas': 0,
                'errores_gemini': 0, 'errores_youtube': 0, 'comentarios_filtrados': 0
            },
            'tipos_procesados': {},
            'acciones_de_moderacion': {'crisis_ignorada': 0}
        }

    def ejecutar_800rpd(self):
        """Ejecución principal con respuestas cordiales."""
        print(f"\n🚀 INICIANDO EJECUCIÓN - MODO CORDIAL Y POSITIVO...")
        print(f"   💖 Todas las respuestas serán bendiciones genuinas")
        inicio = datetime.now()
        respuestas_enviadas = 0
        
        videos = self.obtener_videos_recientes()
        if not videos:
            print("❌ No hay videos disponibles.")
            return
        
        print(f"\n🎯 PROCESANDO HASTA {self.max_respuestas_por_ejecucion} COMENTARIOS:")
        print("-" * 60)
        
        comentarios_a_procesar = []
        for video in videos:
            comentarios_a_procesar.extend(self.obtener_comentarios_de_video(video['id'], video['titulo']))
        
        # Ordenar todos los comentarios por fecha para responder a los más nuevos primero
        comentarios_a_procesar.sort(key=lambda x: x['fecha'], reverse=True)

        for comentario in comentarios_a_procesar:
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
            
            self.stats['resumen']['comentarios_procesados'] += 1
            
            if not self.es_comentario_valido(comentario['texto']):
                self.stats['resumen']['comentarios_filtrados'] += 1
                continue
            
            print(f"\n   💬 COMENTARIO #{respuestas_enviadas + 1}")
            print(f"      👤 {comentario['autor_nombre']}")
            print(f"      📝 \"{comentario['texto']}\"")
            
            analisis = self.detectar_tipo_comentario_mejorado(comentario['texto'], comentario['video_titulo'])
            
            print(f"      🏷️  Tipo: {analisis['tipo']} | Tono: {analisis['tono']}")
            if analisis.get('requiere_respuesta_suave'):
                print(f"      💖 Aplicando respuesta extra cordial")
            
            contexto_previo = self.obtener_contexto_usuario(comentario['autor_id'])
            
            respuesta = self.generar_respuesta_contextual_mejorada(
                comentario['texto'], contexto_previo, analisis, comentario
            )
            
            if respuesta is None:
                continue
            
            if self.responder_comentario_800rpd(comentario['id'], respuesta, comentario['autor_nombre']):
                respuestas_enviadas += 1
                self.stats['resumen']['respuestas_exitosas'] += 1
                self.stats['tipos_procesados'][analisis['tipo']] = self.stats['tipos_procesados'].get(analisis['tipo'], 0) + 1
                
                self.actualizar_memoria_usuario(
                    comentario['autor_id'], comentario['autor_nombre'], comentario['texto']
                )
                
                print(f"      🎉 Progreso: {respuestas_enviadas}/{self.max_respuestas_por_ejecucion}")
        
        self.guardar_memoria_conversaciones()
        duracion_total = (datetime.now() - inicio).total_seconds()
        self.generar_reporte_800rpd(duracion_total)

    def generar_reporte_800rpd(self, duracion_segundos: float):
        stats = self.stats
        stats['info_ejecucion']['fin'] = datetime.now().isoformat()
        stats['info_ejecucion']['duracion_minutos'] = round(duracion_segundos / 60, 2)
        
        nombre_reporte = f"reporte_{self.run_id}.json"
        with open(nombre_reporte, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*80)
        print("📊 REPORTE MODO CORDIAL (V3) - EJECUCIÓN COMPLETADA")
        print("="*80)
        
        print(f"   - Duración: {stats['info_ejecucion']['duracion_minutos']} min")
        print(f"   - Enviados: {stats['resumen']['respuestas_exitosas']} / Procesados: {stats['resumen']['comentarios_procesados']}")
        print(f"   - IA: {stats['resumen']['respuestas_ia_exitosas']} | Fallbacks: {stats['resumen']['respuestas_exitosas'] - stats['resumen']['respuestas_ia_exitosas']}")
        print(f"   - Errores (IA/YouTube): {stats['resumen']['errores_gemini']} / {stats['resumen']['errores_youtube']}")
        
        if stats['resumen']['respuestas_exitosas'] >= 15:
            print("   - DIAGNÓSTICO: 🎉 EXCELENTE! Configuración funcionando perfectamente.")
        elif stats['resumen']['respuestas_exitosas'] > 0:
            print("   - DIAGNÓSTICO: ✅ BUENO. Se enviaron respuestas, revisar disponibilidad de comentarios si no se alcanzó el objetivo.")
        else:
            print("   - DIAGNÓSTICO: ❌ REVISAR. No se procesaron comentarios. Revisar filtros o errores.")

        print(f"\n📄 Reporte guardado: {nombre_reporte}")
        print("="*80)

if __name__ == "__main__":
    try:
        bot = ProsperidadDivina_800RPD()
        bot.ejecutar_800rpd()
        print("\n🎯 EJECUCIÓN CORDIAL (V3) COMPLETADA")
    except KeyboardInterrupt:
        print("\n⏹️  Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN LA EJECUCIÓN PRINCIPAL: {e}")
        print(traceback.format_exc())
