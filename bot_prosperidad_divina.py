#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN SIMPLE 6000 PUNTOS
Archivo: bot_prosperidad_divina.py
Fecha: 10 de Septiembre de 2025

CONFIGURACIÓN SIMPLE:
- 20 ejecuciones x 5 comentarios = 6000 puntos exactos
- Sin JSON de cuota (innecesario con matemática simple)
- Sin detección de miembros (API no lo permite confiablemente)
- Exactamente 5 comentarios por ejecución
- Respuestas por orden cronológico (más recientes primero)
- Horarios aleatorios generados diariamente
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

class ProsperidadDivina_Simple:
    def __init__(self):
        self.run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        print("="*60)
        print(f"Bot Prosperidad Divina - VERSIÓN SIMPLE")
        print(f"ID: {self.run_id}")
        print("="*60)

        # CONFIGURACIÓN SIMPLE
        self.comentarios_exactos = 5  # Siempre exactamente 5
        self.channel_id = 'UCgRg_G9C4-_AHBETHcc7cQQ'
        self.rate_limit_seconds = 12

        # CREDENCIALES
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.youtube_credentials_comments = os.environ.get('YOUTUBE_CREDENTIALS_COMMENTS')
        self.youtube_api_key = "AIzaSyBXwOqq2OoC9TpO22OfbUogFaOqIFxF85A"
        
        if not all([self.gemini_api_key, self.youtube_credentials_comments]):
            raise ValueError("ERROR: Faltan credenciales.")

        # INICIALIZACIÓN
        self.model = self.configurar_gemini()
        self.youtube_lectura = self.configurar_youtube_lectura()
        self.youtube_escritura = self.configurar_youtube_oauth()

        # PERSISTENCIA
        self.db_respondidos_path = "comentarios_respondidos.txt"
        self.db_conversaciones_path = "memoria_conversaciones.json"
        self.comentarios_ya_respondidos = self.cargar_db_respondidos()
        self.memoria_conversacion_usuario = self.cargar_memoria_conversaciones()
        self.stats = self.inicializar_estadisticas()
        
        print(f"CONFIGURACIÓN:")
        print(f"  - Comentarios por ejecución: {self.comentarios_exactos}")
        print(f"  - Ejecuciones por día: 20")
        print(f"  - Puntos por día: {20 * self.comentarios_exactos * 60}")
        print(f"  - Pausa entre requests: {self.rate_limit_seconds}s")
        print("="*60)

    def configurar_gemini(self) -> genai.GenerativeModel:
        try:
            print("Configurando Gemini 2.5 Flash-Lite...")
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            time.sleep(self.rate_limit_seconds)
            test_response = model.generate_content("Responde: 'Simple configurado'")
            
            if "simple" in test_response.text.strip().lower():
                print("  Gemini configurado correctamente.")
            return model
        except Exception as e:
            print(f"  ERROR Gemini: {e}")
            raise

    def configurar_youtube_lectura(self):
        try:
            print("Configurando YouTube API lectura...")
            service = build('youtube', 'v3', developerKey=self.youtube_api_key)
            print("  YouTube API configurada.")
            return service
        except Exception as e:
            print(f"  ERROR YouTube: {e}")
            raise

    def configurar_youtube_oauth(self):
        try:
            print("Configurando YouTube OAuth escritura...")
            creds_data = json.loads(self.youtube_credentials_comments)
            creds = Credentials.from_authorized_user_info(creds_data)
            service = build('youtube', 'v3', credentials=creds)
            print("  YouTube OAuth configurado.")
            return service
        except Exception as e:
            print(f"  ERROR OAuth: {e}")
            raise

    def cargar_db_respondidos(self) -> Set[str]:
        if not os.path.exists(self.db_respondidos_path):
            return set()
        
        with open(self.db_respondidos_path, 'r', encoding='utf-8') as f:
            respondidos = {line.strip() for line in f if line.strip()}
        print(f"  {len(respondidos)} comentarios ya respondidos.")
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
        print(f"  Memoria de {len(memoria)} usuarios cargada.")
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
        
        # Mantener solo últimos 3 mensajes
        self.memoria_conversacion_usuario[autor_id]["mensajes"] = \
            self.memoria_conversacion_usuario[autor_id]["mensajes"][-3:]

    def obtener_contexto_usuario(self, autor_id: str) -> List[str]:
        if autor_id not in self.memoria_conversacion_usuario:
            return []
        return [msg["texto"] for msg in self.memoria_conversacion_usuario[autor_id]["mensajes"]]

    def obtener_videos_recientes(self) -> List[Dict]:
        try:
            print("Obteniendo videos recientes...")
            
            channel_response = self.youtube_lectura.channels().list(
                part='contentDetails',
                id=self.channel_id
            ).execute()
            
            if not channel_response.get('items'):
                print("  Canal no encontrado.")
                return []
            
            uploads_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            playlist_items = self.youtube_lectura.playlistItems().list(
                part='snippet',
                playlistId=uploads_id,
                maxResults=3  # Solo 3 videos más recientes
            ).execute()
            
            videos = [{'id': item['snippet']['resourceId']['videoId'],
                       'titulo': item['snippet']['title'],
                       'fecha': item['snippet']['publishedAt']}
                      for item in playlist_items.get('items', [])]
            
            print(f"  {len(videos)} videos encontrados.")
            return videos
            
        except Exception as e:
            print(f"  ERROR obteniendo videos: {e}")
            return []

    def obtener_comentarios_de_video(self, video_id: str, video_titulo: str) -> List[Dict]:
        comentarios_nuevos = []
        try:
            print(f"  Procesando: {video_titulo[:40]}...")
            
            response = self.youtube_lectura.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',  # Más recientes primero
                maxResults=50
            ).execute()
            
            for item in response.get('items', []):
                comment_id = item['snippet']['topLevelComment']['id']
                
                # Filtrar ya respondidos y con respuestas
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
            
            print(f"    {len(comentarios_nuevos)} comentarios nuevos encontrados.")
            return comentarios_nuevos
            
        except Exception as e:
            print(f"    ERROR: {e}")
            return []

    def es_comentario_valido(self, texto: str) -> bool:
        if not texto or len(texto.strip()) <= 3 or len(texto.strip()) > 500:
            return False
        if re.search(r'http[s]?://', texto, re.IGNORECASE):
            return False
        return True

    def detectar_tipo_comentario(self, texto: str, titulo_video: str = "") -> Dict:
        texto_lower = texto.lower()
        
        resultado = {
            'tipo': 'general',
            'tono': 'neutro',
            'es_pregunta': '?' in texto,
            'requiere_respuesta_suave': False
        }
        
        # Detectar crisis (omitir estos comentarios)
        palabras_crisis = ['no aguanto', 'suicidio', 'morir', 'matarme', 'acabar con todo']
        if any(word in texto_lower for word in palabras_crisis):
            resultado['tipo'] = 'crisis'
            return resultado
        
        # Detectar escepticismo suave
        negaciones = ['no', 'nunca', 'jamás']
        patrones_sarcasmo = [r'\bja+\b', r'\bjeje\b', r'no creo', r'mentira', r'falso']
        
        if (any(neg in texto_lower for neg in negaciones) or 
            any(re.search(patron, texto_lower) for patron in patrones_sarcasmo)):
            resultado['tono'] = 'esceptico_suave'
            resultado['requiere_respuesta_suave'] = True
        
        # Categorizar tipos
        if any(word in texto_lower for word in ['dinero', 'trabajo', 'abundancia', 'prosperidad']):
            resultado['tipo'] = 'abundancia'
        elif any(word in texto_lower for word in ['dolor', 'triste', 'depresión', 'ansiedad']):
            resultado['tipo'] = 'dolor_confusion'
        elif any(word in texto_lower for word in ['gracias', 'bendiciones', 'amén']):
            resultado['tipo'] = 'gratitud'
        elif len(texto.split()) <= 5:
            resultado['tipo'] = 'saludo'
        
        return resultado

    def generar_respuesta_contextual(self, comentario_actual: str, contexto_previo: List[str], 
                                   analisis: Dict, info_comentario: Dict) -> str:
        
        if analisis['tipo'] == 'crisis':
            print("    CRISIS - Comentario omitido.")
            self.stats['crisis_ignoradas'] += 1
            return None
        
        try:
            contexto_str = ""
            if contexto_previo:
                contexto_str = ("Conversación previa:\n" + 
                               "\n".join(f"- {msg}" for msg in contexto_previo[-2:]) + "\n\n")
            
            instrucciones_especiales = ""
            if analisis.get('requiere_respuesta_suave'):
                instrucciones_especiales = "IMPORTANTE: Este usuario puede estar escéptico. Responde con amor genuino y bendiciones directas, sin confrontar."
            
            prompt = f"""Eres un asistente espiritual cordial del canal "Prosperidad Divina".

{contexto_str}CONTEXTO:
- Usuario: {info_comentario['autor_nombre']}
- Comentario: "{comentario_actual}"

{instrucciones_especiales}

INSTRUCCIONES:
1. Sé siempre cordial, cálido y amoroso.
2. Ofrece bendiciones sinceras a TODOS.
3. NO uses frases como "respeto tu perspectiva" (suena distante).
4. Usa bendiciones directas: "Dios te bendiga", "Bendiciones para ti".
5. Mantén tono de amor incondicional.

FORMATO:
- Máximo 2 líneas cortas.
- Usa 1-2 emojis positivos.
- Sé genuino y transmite amor.

Respuesta cordial:"""

            print(f"    Generando respuesta... (pausa {self.rate_limit_seconds}s)")
            time.sleep(self.rate_limit_seconds)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.7, max_output_tokens=100),
                safety_settings=safety_settings
            )
            
            if not response or not response.text:
                raise ValueError("Respuesta vacía de la IA")
            
            respuesta = response.text.strip()
            
            # Validar que no use frases distantes
            frases_evitar = ['respeto tu perspectiva', 'respeto tu opinión']
            for frase in frases_evitar:
                if frase in respuesta.lower():
                    return self._generar_fallback(analisis)
            
            if len(respuesta) < 20:
                return self._generar_fallback(analisis)
            
            print(f"    Respuesta: \"{respuesta[:50]}...\"")
            self.stats['respuestas_ia_exitosas'] += 1
            return respuesta
            
        except Exception as e:
            print(f"    ERROR IA: {e}")
            self.stats['errores_gemini'] += 1
            return self._generar_fallback(analisis)
    
    def _generar_fallback(self, analisis: Dict) -> str:
        bendiciones = [
            "Dios te bendiga abundantemente",
            "Que tengas un día maravilloso lleno de bendiciones",
            "Bendiciones infinitas para ti y tu familia",
            "Que la paz y el amor llenen tu corazón",
            "Que Dios ilumine siempre tu camino"
        ]
        
        fallbacks_tipo = {
            'saludo': ["Bendiciones para ti también", "Hola! Muchas bendiciones"],
            'abundancia': ["Que la prosperidad fluya en tu vida", "Dios multiplique tus bendiciones"],
            'dolor_confusion': ["Dios te abraza con su amor infinito", "Enviándote mucha fuerza y paz"],
            'gratitud': ["Que tus bendiciones se multipliquen", "Gracias por tu hermoso corazón"]
        }
        
        tipo = analisis.get('tipo', 'general')
        opciones = fallbacks_tipo.get(tipo, []) + bendiciones
        return random.choice(opciones)

    def responder_comentario(self, comentario_id: str, respuesta: str, autor_nombre: str) -> bool:
        try:
            print(f"    Enviando respuesta...")
            
            self.youtube_escritura.comments().insert(
                part='snippet',
                body={'snippet': {'parentId': comentario_id, 'textOriginal': respuesta}}
            ).execute()
            
            print(f"    Enviada a '{autor_nombre}'.")
            self.guardar_en_db_respondidos(comentario_id)
            return True
            
        except HttpError as e:
            error_msg = e.content.decode('utf-8') if e.content else str(e)
            print(f"    ERROR HTTP: {error_msg}")
            self.stats['errores_youtube'] += 1
            return False
        except Exception as e:
            print(f"    ERROR: {e}")
            self.stats['errores_youtube'] += 1
            return False

    def inicializar_estadisticas(self):
        return {
            'id': self.run_id,
            'inicio': datetime.now().isoformat(),
            'comentarios_procesados': 0,
            'respuestas_exitosas': 0,
            'respuestas_ia_exitosas': 0,
            'errores_gemini': 0,
            'errores_youtube': 0,
            'crisis_ignoradas': 0,
            'comentarios_filtrados': 0
        }

    def ejecutar_simple(self):
        """Ejecuta el bot simple: exactamente 5 comentarios."""
        print(f"INICIANDO EJECUCIÓN SIMPLE...")
        print(f"Objetivo: {self.comentarios_exactos} comentarios exactos")
        
        inicio = datetime.now()
        respuestas_enviadas = 0
        
        videos = self.obtener_videos_recientes()
        if not videos:
            print("No hay videos disponibles.")
            return
        
        print(f"PROCESANDO COMENTARIOS:")
        print("-" * 50)
        
        # Recopilar TODOS los comentarios de todos los videos
        todos_comentarios = []
        for video in videos:
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            todos_comentarios.extend(comentarios)
        
        # Ordenar por fecha (más recientes primero)
        todos_comentarios.sort(key=lambda x: x['fecha'], reverse=True)
        
        print(f"Total comentarios encontrados: {len(todos_comentarios)}")
        print(f"Procesando los {self.comentarios_exactos} más recientes:")
        
        # Procesar exactamente los comentarios requeridos
        for i, comentario in enumerate(todos_comentarios):
            if respuestas_enviadas >= self.comentarios_exactos:
                break
            
            self.stats['comentarios_procesados'] += 1
            
            if not self.es_comentario_valido(comentario['texto']):
                self.stats['comentarios_filtrados'] += 1
                print(f"  Comentario {i+1}: FILTRADO (inválido)")
                continue
            
            print(f"\nCOMENTARIO #{respuestas_enviadas + 1}")
            print(f"  Usuario: {comentario['autor_nombre']}")
            print(f"  Texto: \"{comentario['texto']}\"")
            
            analisis = self.detectar_tipo_comentario(comentario['texto'], comentario['video_titulo'])
            
            if analisis['tipo'] == 'crisis':
                print(f"  Estado: OMITIDO (crisis)")
                continue
            
            print(f"  Tipo: {analisis['tipo']} | Tono: {analisis['tono']}")
            
            contexto_previo = self.obtener_contexto_usuario(comentario['autor_id'])
            
            respuesta = self.generar_respuesta_contextual(
                comentario['texto'], contexto_previo, analisis, comentario
            )
            
            if respuesta is None:
                continue
            
            if self.responder_comentario(comentario['id'], respuesta, comentario['autor_nombre']):
                respuestas_enviadas += 1
                self.stats['respuestas_exitosas'] += 1
                
                self.actualizar_memoria_usuario(
                    comentario['autor_id'], comentario['autor_nombre'], comentario['texto']
                )
                
                print(f"  Estado: ENVIADO ({respuestas_enviadas}/{self.comentarios_exactos})")
        
        # Guardar memoria y generar reporte
        self.guardar_memoria_conversaciones()
        duracion_total = (datetime.now() - inicio).total_seconds()
        self.generar_reporte(duracion_total)

    def generar_reporte(self, duracion_segundos: float):
        self.stats['fin'] = datetime.now().isoformat()
        self.stats['duracion_minutos'] = round(duracion_segundos / 60, 2)
        
        nombre_reporte = f"reporte_{self.run_id}.json"
        with open(nombre_reporte, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("REPORTE EJECUCIÓN SIMPLE COMPLETADA")
        print("="*60)
        
        print(f"Duración: {self.stats['duracion_minutos']} min")
        print(f"Enviados: {self.stats['respuestas_exitosas']} / Procesados: {self.stats['comentarios_procesados']}")
        print(f"IA exitosa: {self.stats['respuestas_ia_exitosas']} | Fallbacks: {self.stats['respuestas_exitosas'] - self.stats['respuestas_ia_exitosas']}")
        print(f"Errores (IA/YouTube): {self.stats['errores_gemini']} / {self.stats['errores_youtube']}")
        print(f"Crisis omitidas: {self.stats['crisis_ignoradas']}")
        print(f"Filtrados: {self.stats['comentarios_filtrados']}")
        
        if self.stats['respuestas_exitosas'] == self.comentarios_exactos:
            print("DIAGNÓSTICO: PERFECTO - 5 comentarios procesados exactamente.")
        elif self.stats['respuestas_exitosas'] > 0:
            print(f"DIAGNÓSTICO: PARCIAL - Solo {self.stats['respuestas_exitosas']} de {self.comentarios_exactos} procesados.")
        else:
            print("DIAGNÓSTICO: ERROR - No se procesaron comentarios.")

        print(f"Reporte guardado: {nombre_reporte}")
        print("="*60)

if __name__ == "__main__":
    try:
        bot = ProsperidadDivina_Simple()
        bot.ejecutar_simple()
        print("EJECUCIÓN SIMPLE COMPLETADA")
    except KeyboardInterrupt:
        print("Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        print(traceback.format_exc())
