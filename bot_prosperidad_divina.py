#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🙏 Bot Prosperidad Divina - VERSIÓN CORDIAL Y POSITIVA
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
            'requiere_respuesta_suave': False,  # Nueva bandera para respuestas más suaves
            'elementos_detectados': []
        }
        
        # Detectar si es una respuesta directa al título
        palabras_titulo = set(titulo_lower.split())
        palabras_comentario = set(texto_lower.split())
        coincidencias = palabras_titulo & palabras_comentario
        
        # Si hay negación + elementos del título, requiere respuesta suave
        negaciones = ['no', 'nunca', 'jamás', 'ni', 'tampoco', 'nada']
        if any(neg in texto_lower for neg in negaciones) and len(coincidencias) > 1:
            resultado['es_respuesta_a_titulo'] = True
            resultado['requiere_respuesta_suave'] = True
            resultado['tono'] = 'esceptico_suave'  # Cambio de tono para manejo especial
        
        # Detectar sarcasmo/escepticismo (pero marcar como suave para respuesta cordial)
        patrones_sarcasmo = [
            r'\bja+\b', r'\bjeje\b', r'\blol\b', r'\bxd\b',
            r'no creo', r'mentira', r'falso', r'estafa',
            r'otro planeta', r'marciano', r'extraterrestre'
        ]
        if any(re.search(patron, texto_lower) for patron in patrones_sarcasmo):
            resultado['tono'] = 'esceptico_suave'
            resultado['requiere_respuesta_suave'] = True
        
        # Crisis - máxima prioridad
        palabras_crisis = ['no aguanto', 'suicidio', 'morir', 'matarme', 'acabar con todo']
        if any(word in texto_lower for word in palabras_crisis):
            resultado['tipo'] = 'crisis'
            resultado['tono'] = 'crisis'
            return resultado
        
        # Detectar menciones de figuras religiosas
        figuras_religiosas = [
            'dios', 'jesús', 'cristo', 'virgen', 'maría', 
            'arcángel', 'miguel', 'gabriel', 'rafael',
            'ángel', 'espíritu santo', 'señor'
        ]
        for figura in figuras_religiosas:
            if figura in texto_lower:
                resultado['menciona_figura_religiosa'] = True
                resultado['elementos_detectados'].append(figura)
        
        # Clasificación por tipo
        if len(texto.split()) <= 5:
            if resultado['requiere_respuesta_suave']:
                resultado['tipo'] = 'comentario_breve'
            else:
                resultado['tipo'] = 'saludo'
        
        # Abundancia/dinero
        palabras_abundancia = ['dinero', 'trabajo', 'abundancia', 'prosperidad', 'riqueza', 'empleo', 'negocio']
        if any(word in texto_lower for word in palabras_abundancia):
            resultado['tipo'] = 'abundancia'
        
        # Dolor emocional
        palabras_dolor = ['dolor', 'triste', 'depresión', 'ansiedad', 'solo', 'sufr', 'llorar', 'extrañ']
        if any(word in texto_lower for word in palabras_dolor):
            resultado['tipo'] = 'dolor_confusion'
            resultado['tono'] = 'vulnerable'
        
        # Gratitud
        palabras_gratitud = ['gracias', 'bendiciones', 'amén', 'sí acepto', 'recibo', 'agradezco']
        if any(word in texto_lower for word in palabras_gratitud):
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
            return None
        
        try:
            # Construir contexto previo si existe
            contexto_str = ""
            if contexto_previo:
                contexto_str = ("Conversación previa:\n" + 
                               "\n".join(f"- {msg}" for msg in contexto_previo[-2:]) + "\n\n")
            
            # Instrucciones específicas según el análisis
            instrucciones_especificas = self._generar_instrucciones_cordiales(analisis)
            
            # Prompt mejorado enfocado en cordialidad
            prompt = f"""Eres un asistente espiritual muy cordial y amoroso del canal "Prosperidad Divina".
Tu misión es bendecir y llenar de amor a todos, sin importar su actitud.

{contexto_str}CONTEXTO:
- Usuario: {info_comentario['autor_nombre']}
- Comentario actual: "{comentario_actual}"

INSTRUCCIONES FUNDAMENTALES:
1. Sé SIEMPRE cordial, cálido y genuinamente amoroso
2. Ofrece bendiciones sinceras y positivas a TODOS
3. NO uses frases como "respeto tu perspectiva" o "respeto tu opinión" (suenan distantes)
4. En su lugar, usa bendiciones directas como "Dios te bendiga", "Bendiciones para ti", "Que tengas un hermoso día"
5. NO menciones el título del video a menos que el usuario lo haga
6. Mantén un tono de amor incondicional

{instrucciones_especificas}

EJEMPLOS DE RESPUESTAS CORDIALES:
- "Dios te bendiga abundantemente 🙏✨"
- "Que tengas un día maravilloso lleno de bendiciones 💫"
- "Bendiciones infinitas para ti y tu familia 🌟🙏"
- "Que la paz y el amor llenen tu corazón 💖✨"
- "Muchas bendiciones en tu camino 🙏💫"

FORMATO:
- Máximo 2 líneas cortas
- Usa 1-2 emojis positivos (🙏✨💫🌟💖🕊️)
- Sé cálido y genuino
- Transmite amor sincero

Respuesta (cordial y amorosa):"""

            print(f"      🧠 Generando respuesta cordial...")
            time.sleep(self.rate_limit_seconds)
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Un poco más alta para variedad en bendiciones
                    max_output_tokens=100,
                    top_p=0.9
                ),
                safety_settings=safety_settings
            )
            
            if not response or not response.text:
                raise ValueError("Respuesta vacía")
            
            respuesta = response.text.strip()
            
            # Validación: asegurar que la respuesta sea cordial
            respuesta_validada = self._validar_cordialidad(respuesta, analisis, comentario_actual)
            
            print(f"      ✅ Respuesta: \"{respuesta_validada[:50]}...\"")
            return respuesta_validada
            
        except Exception as e:
            print(f"      ❌ Error: {type(e).__name__}")
            return self._generar_fallback_cordial(analisis)
    
    def _generar_instrucciones_cordiales(self, analisis: Dict) -> str:
        """Genera instrucciones específicas manteniendo siempre la cordialidad."""
        
        instrucciones = []
        
        if analisis.get('requiere_respuesta_suave') or analisis['tono'] == 'esceptico_suave':
            instrucciones.append("""
RESPUESTA ESPECIALMENTE AMOROSA:
- Este usuario puede estar escéptico o confundido
- Dale una bendición extra cálida y sincera
- NO confrontes ni argumentes
- Simplemente bendícelo con amor genuino
- Ejemplos: "Dios te bendiga grandemente 🙏✨", "Que tengas un día hermoso lleno de paz 💫"
""")
        
        elif analisis['tono'] == 'vulnerable':
            instrucciones.append("""
USUARIO NECESITA CONSUELO:
- Muestra compasión profunda
- Ofrece esperanza y fortaleza
- Bendiciones reconfortantes
- Ejemplos: "Dios te abraza en este momento 💖🙏", "Enviándote mucha fuerza y amor 💫"
""")
        
        if analisis['es_respuesta_a_titulo']:
            instrucciones.append("""
NO MENCIONES EL TÍTULO:
- Responde con una bendición general
- No hagas referencia al contenido del video
- Solo bendice al usuario con amor
""")
        
        if analisis['menciona_figura_religiosa']:
            figuras = ', '.join(analisis['elementos_detectados'])
            instrucciones.append(f"""
FIGURAS ESPIRITUALES MENCIONADAS: {figuras}
- Puedes incluir estas figuras en tu bendición
- Mantén el tono amoroso y cordial
""")
        
        if analisis['tipo'] == 'gratitud':
            instrucciones.append("""
USUARIO AGRADECIDO:
- Multiplica sus bendiciones
- Agradece su hermoso corazón
- Sé especialmente cálido
""")
        
        return '\n'.join(instrucciones)
    
    def _validar_cordialidad(self, respuesta: str, analisis: Dict, comentario: str) -> str:
        """Valida que la respuesta sea cordial y ajusta si es necesario."""
        
        respuesta_lower = respuesta.lower()
        
        # Frases no cordiales a evitar
        frases_evitar = [
            'respeto tu perspectiva',
            'respeto tu opinión',
            'entiendo tu punto',
            'comprendo tu posición',
            'cada quien',
            'está bien si'
        ]
        
        # Si contiene frases no cordiales, reemplazar con bendición directa
        for frase in frases_evitar:
            if frase in respuesta_lower:
                return self._generar_fallback_cordial(analisis)
        
        # Si es muy corta o parece seca, enriquecer
        if len(respuesta) < 20:
            return self._generar_fallback_cordial(analisis)
        
        return respuesta
    
    def _generar_fallback_cordial(self, analisis: Dict) -> str:
        """Genera fallbacks siempre cordiales y positivos."""
        
        # Bendiciones cordiales universales
        bendiciones_universales = [
            "Dios te bendiga abundantemente 🙏✨",
            "Que tengas un día maravilloso lleno de bendiciones 💫",
            "Bendiciones infinitas para ti y tu familia 🌟🙏",
            "Que la paz y el amor llenen tu corazón 💖✨",
            "Muchas bendiciones en tu camino 🙏💫",
            "Dios te llene de amor y prosperidad 🌟💖",
            "Que todas las bendiciones lleguen a tu vida 🙏✨",
            "Un abrazo de luz para ti 💫🤗",
            "Bendiciones y mucha paz para tu corazón 🕊️💖",
            "Que Dios ilumine siempre tu camino 🌟🙏"
        ]
        
        # Fallbacks específicos por tipo (todos cordiales)
        fallbacks_especificos = {
            'comentario_breve': [
                "Dios te bendiga grandemente 🙏✨",
                "Muchas bendiciones para ti 💫🙏",
                "Que tengas un hermoso día 🌟💖"
            ],
            'saludo': [
                "¡Bendiciones para ti también! 🙏✨",
                "Que Dios te bendiga siempre 💫🌟",
                "¡Hola! Muchas bendiciones 🙏💖"
            ],
            'abundancia': [
                "Que la prosperidad fluya abundantemente en tu vida 💫🙏",
                "Dios multiplique tus bendiciones y abundancia 🌟✨",
                "Que se abran todas las puertas de prosperidad para ti 🙏💖"
            ],
            'dolor_confusion': [
                "Dios te abraza con su amor infinito 💖🙏",
                "Enviándote mucha fuerza y paz 🕊️✨",
                "Que encuentres consuelo en el amor divino 🌟💫"
            ],
            'gratitud': [
                "¡Que tus bendiciones se multipliquen! 🌟🙏",
                "Gracias a ti por tu hermoso corazón ✨💖",
                "Dios te bendiga por tu gratitud 🙏💫"
            ]
        }
        
        tipo = analisis.get('tipo', 'general')
        
        # Si requiere respuesta suave o es escéptico, usar bendiciones universales
        if analisis.get('requiere_respuesta_suave') or analisis['tono'] in ['esceptico_suave', 'esceptico']:
            return random.choice(bendiciones_universales)
        
        # Si hay fallbacks específicos, mezclar con universales
        if tipo in fallbacks_especificos:
            todas_opciones = fallbacks_especificos[tipo] + bendiciones_universales[:3]
            return random.choice(todas_opciones)
        
        # Por defecto, bendición universal
        return random.choice(bendiciones_universales)
    
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
        
        print(f"\n🎯 PROCESANDO {self.max_respuestas_por_ejecucion} COMENTARIOS:")
        print("-" * 60)
        
        for video_idx, video in enumerate(videos, 1):
            if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                break
                
            print(f"\n📹 VIDEO {video_idx}/{len(videos)}: {video['titulo'][:50]}...")
            comentarios = self.obtener_comentarios_de_video(video['id'], video['titulo'])
            
            if not comentarios:
                continue
            
            comentarios.sort(key=lambda x: x['fecha'], reverse=True)
            
            for comentario in comentarios:
                if respuestas_enviadas >= self.max_respuestas_por_ejecucion:
                    break
                
                self.stats['resumen']['comentarios_procesados'] += 1
                
                if not self.es_comentario_valido(comentario['texto']):
                    self.stats['resumen']['comentarios_filtrados'] += 1
                    continue
                
                print(f"\n   💬 COMENTARIO #{respuestas_enviadas + 1}")
                print(f"      👤 {comentario['autor_nombre']}")
                print(f"      📝 \"{comentario['texto']}\"")
                
                # Análisis mejorado del comentario
                analisis = self.detectar_tipo_comentario_mejorado(
                    comentario['texto'], 
                    comentario['video_titulo']
                )
                
                print(f"      🏷️  Tipo: {analisis['tipo']} | Tono: {analisis['tono']}")
                if analisis.get('requiere_respuesta_suave'):
                    print(f"      💖 Aplicando respuesta extra cordial")
                
                # Obtener contexto previo
                contexto_previo = self.obtener_contexto_usuario(comentario['autor_id'])
                
                # Generar respuesta cordial
                respuesta = self.generar_respuesta_contextual_mejorada(
                    comentario['texto'],
                    contexto_previo,
                    analisis,
                    comentario
                )
                
                if respuesta is None:
                    continue
                
                # Enviar respuesta
                if self.responder_comentario_800rpd(comentario['id'], respuesta, comentario['autor_nombre']):
                    respuestas_enviadas += 1
                    self.stats['resumen']['respuestas_exitosas'] += 1
                    self.stats['tipos_procesados'][analisis['tipo']] = \
                        self.stats['tipos_procesados'].get(analisis['tipo'], 0) + 1
                    
                    self.actualizar_memoria_usuario(
                        comentario['autor_id'],
                        comentario['autor_nombre'],
                        comentario['texto']
                    )
                    
                    print(f"      🎉 Progreso: {respuestas_enviadas}/{self.max_respuestas_por_ejecucion}")
        
        self.guardar_memoria_conversaciones()
        duracion_total = (datetime.now() - inicio).total_seconds()
        self.generar_reporte_800rpd(duracion_total)
