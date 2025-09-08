# bot_prosperidad_divina_automatico.py - Sistema Completo
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
        
        # 🤖 Configurar modelos Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.pro_model = genai.GenerativeModel('gemini-1.5-pro')
        self.flash_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 📺 Configurar YouTube
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        
        # 📊 Límites optimizados (según tu estrategia)
        self.FLASH_LIMIT_DAILY = 1450  # Respuestas rápidas
        self.PRO_LIMIT_DAILY = 46      # Calidad premium
        self.TOTAL_LIMIT = 1496        # Total con margen de seguridad
        
        # 📅 Cargar estado del día
        self.cargar_estado_diario()
        
        # 📊 Estadísticas del ministerio
        self.stats = {
            'respuestas_exitosas': 0,
            'pro_usado': self.estado_diario.get('pro_usado', 0),
            'flash_usado': self.estado_diario.get('flash_usado', 0),
            'peticiones_oracion': 0,
            'testimonios_prosperidad': 0,
            'respuestas_abundancia': 0,
            'videos_procesados': 0,
            'backlog_procesado': 0,
            'errores': 0,
            'ultima_ejecucion': datetime.now().isoformat()
        }
        
        # 🎯 Configuración ministerial
        self.config_ministerio = {
            'nombre_canal': 'Prosperidad Divina',
            'filtros_videos': [
                'PROSPERIDAD', 'DIVINA', 'ABUNDANCIA', 'BENDICION', 'DIOS',
                'MENSAJE', 'ARCANGEL', 'MILAGRO', 'FE', 'JESUS', 'URGENTE',
                'ORACION', 'CIELO', 'ANGEL', 'ESPIRITUAL'
            ],
            'max_videos_monitorear': 15,
            'max_comentarios_por_video': 50,
            'dias_antiguedad_maxima': 7
        }

    def cargar_estado_diario(self):
        """📅 Cargar estado del día actual"""
        try:
            with open('estado_prosperidad_divina.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            fecha_guardada = data.get('fecha', '')
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            
            if fecha_guardada == fecha_hoy:
                self.estado_diario = data
                print(f"📅 Estado del ministerio cargado: Pro {data.get('pro_usado', 0)}/46, Flash {data.get('flash_usado', 0)}/1450")
            else:
                self.estado_diario = self.crear_estado_nuevo_dia()
                print(f"🌅 Nuevo día de ministerio: {fecha_hoy}")
                
        except FileNotFoundError:
            self.estado_diario = self.crear_estado_nuevo_dia()
            print("🚀 Primer día del ministerio digital - estado inicial creado")

    def crear_estado_nuevo_dia(self):
        """🌅 Crear estado para nuevo día de ministerio"""
        return {
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'pro_usado': 0,
            'flash_usado': 0,
            'comentarios_bendecidos_hoy': [],
            'videos_visitados_hoy': [],
            'inicio_ministerio': datetime.now().isoformat()
        }

    def guardar_estado_diario(self):
        """💾 Guardar estado actual del ministerio"""
        self.estado_diario.update({
            'pro_usado': self.stats['pro_usado'],
            'flash_usado': self.stats['flash_usado'],
            'ultima_actualizacion': datetime.now().isoformat()
        })
        
        with open('estado_prosperidad_divina.json', 'w', encoding='utf-8') as f:
            json.dump(self.estado_diario, f, indent=2, ensure_ascii=False)

    def obtener_videos_ministerio(self) -> List[Dict]:
        """📺 Detectar videos del ministerio automáticamente"""
        
        print(f"\n🔍 DETECTANDO VIDEOS DEL MINISTERIO")
        print("-" * 40)
        
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=self.channel_id,
                type='video',
                order='date',
                maxResults=50
            )
            
            response = request.execute()
            videos_ministerio = []
            
            for item in response['items']:
                video_data = {
                    'id': item['id']['videoId'],
                    'titulo': item['snippet']['title'],
                    'fecha_publicacion': item['snippet']['publishedAt'],
                    'descripcion': item['snippet']['description'][:200],
                }
                
                # Verificar relevancia ministerial
                if self.es_video_del_ministerio(video_data):
                    video_data['tipo_detectado'] = self.detectar_tipo_video_ministerial(video_data['titulo'])
                    videos_ministerio.append(video_data)
                    
                    print(f"✅ {video_data['titulo'][:60]}...")
                    print(f"   📅 {video_data['fecha_publicacion'][:10]} | 🏷️ {video_data['tipo_detectado']}")
                    
                    if len(videos_ministerio) >= self.config_ministerio['max_videos_monitorear']:
                        break
            
            self.stats['videos_procesados'] = len(videos_ministerio)
            print(f"\n📺 Videos del ministerio detectados: {len(videos_ministerio)}")
            
            return videos_ministerio
            
        except HttpError as e:
            print(f"❌ Error detectando videos del ministerio: {e}")
            self.stats['errores'] += 1
            return []

    def es_video_del_ministerio(self, video_data: Dict) -> bool:
        """🎯 Determinar si un video pertenece al ministerio"""
        
        titulo_upper = video_data['titulo'].upper()
        
        # Filtro por palabras clave ministeriales
        es_relevante = any(palabra in titulo_upper for palabra in self.config_ministerio['filtros_videos'])
        
        # Filtro por antigüedad
        fecha_video = datetime.fromisoformat(video_data['fecha_publicacion'].replace('Z', '+00:00'))
        dias_antiguedad = (datetime.now(fecha_video.tzinfo) - fecha_video).days
        no_muy_antiguo = dias_antiguedad <= self.config_ministerio['dias_antiguedad_maxima']
        
        return es_relevante and no_muy_antiguo

    def detectar_tipo_video_ministerial(self, titulo: str) -> str:
        """🏷️ Detectar tipo de video ministerial"""
        
        titulo_upper = titulo.upper()
        
        if any(palabra in titulo_upper for palabra in ['URGENTE', 'EMERGENCIA', 'POCAS HORAS']):
            return 'urgente'
        elif any(palabra in titulo_upper for palabra in ['ARCANGEL MIGUEL', 'MIGUEL']):
            return 'arcangel_miguel'
        elif any(palabra in titulo_upper for palabra in ['JESUS', 'CRISTO']):
            return 'jesus'
        elif any(palabra in titulo_upper for palabra in ['PROSPERIDAD', 'ABUNDANCIA', 'RIQUEZA']):
            return 'prosperidad'
        elif any(palabra in titulo_upper for palabra in ['BENDICION', 'BENDICIONES']):
            return 'bendiciones'
        elif any(palabra in titulo_upper for palabra in ['ORACION', 'ORAR']):
            return 'oracion'
        elif any(palabra in titulo_upper for palabra in ['CIELO', 'SER QUERIDO', 'PARTIO']):
            return 'seres_queridos'
        else:
            return 'mensaje_general'

    def obtener_comentarios_para_bendecir(self, video_id: str, max_comentarios: int = 50) -> List[Dict]:
        """💬 Obtener comentarios que necesitan bendición"""
        
        try:
            # Calcular tiempo límite (comentarios de últimas 6 horas)
            tiempo_limite = datetime.now() - timedelta(hours=6)
            
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                order='time',
                maxResults=min(max_comentarios, 100)
            )
            
            response = request.execute()
            comentarios = []
            
            for item in response['items']:
                comment_snippet = item['snippet']['topLevelComment']['snippet']
                
                # Verificar si es comentario reciente
                published_str = comment_snippet['publishedAt']
                published_time = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                
                # Solo comentarios recientes y que no hayamos bendecido
                if (published_time.replace(tzinfo=None) > tiempo_limite and 
                    item['id'] not in self.estado_diario.get('comentarios_bendecidos_hoy', [])):
                    
                    comentario_data = {
                        'id': item['id'],
                        'video_id': video_id,
                        'texto': comment_snippet['textDisplay'],
                        'autor': comment_snippet['authorDisplayName'],
                        'fecha_publicacion': published_str,
                        'likes': comment_snippet.get('likeCount', 0),
                        'tipo': self.detectar_tipo_comentario_ministerial(comment_snippet['textDisplay'])
                    }
                    
                    comentarios.append(comentario_data)
            
            return comentarios
            
        except HttpError as e:
            print(f"❌ Error obteniendo comentarios: {e}")
            return []

    def detectar_tipo_comentario_ministerial(self, texto: str) -> str:
        """🏷️ Detectar tipo de comentario para respuesta ministerial apropiada"""
        
        texto_lower = texto.lower()
        
        # Peticiones de oración y ayuda
        if any(palabra in texto_lower for palabra in 
               ['por favor', 'ayuda', 'necesito', 'oración', 'ruego', 'favor', 'orar']):
            return 'peticion_oracion'
            
        # Testimonios de prosperidad y bendición
        elif any(palabra in texto_lower for palabra in 
                 ['gracias', 'bendición', 'milagro', 'testmonio', 'prosperidad', 'abundancia', 'cambio mi vida']):
            return 'testimonio_prosperidad'
            
        # Preguntas espirituales
        elif any(palabra in texto_lower for palabra in 
                 ['?', 'cómo', 'por qué', 'cuándo', 'dónde', 'qué significa']):
            return 'pregunta_espiritual'
            
        # Agradecimientos
        elif any(palabra in texto_lower for palabra in 
                 ['amen', 'amén', 'hermoso', 'bendecido', 'me gusta']):
            return 'agradecimiento'
            
        # Expresiones de fe
        elif any(palabra in texto_lower for palabra in 
                 ['fe', 'creo', 'confío', 'espero', 'dios']):
            return 'expresion_fe'
            
        # Comentarios hirientes (para bendecir con amor extra)
        elif any(palabra in texto_lower for palabra in 
                 ['no creo', 'falso', 'mentira', 'no funciona']):
            return 'comentario_hiriente'
            
        else:
            return 'comentario_general'

    def elegir_modelo_para_bendicion(self, tipo_comentario: str) -> str:
        """🤖 Elegir modelo óptimo según tipo de comentario y disponibilidad"""
        
        # Tipos que merecen respuesta premium con Pro
        tipos_premium = ['peticion_oracion', 'comentario_hiriente', 'pregunta_espiritual']
        
        usar_pro = (tipo_comentario in tipos_premium and 
                   self.stats['pro_usado'] < self.PRO_LIMIT_DAILY)
        
        if usar_pro:
            return 'pro'
        elif self.stats['flash_usado'] < self.FLASH_LIMIT_DAILY:
            return 'flash'
        elif self.stats['pro_usado'] < self.PRO_LIMIT_DAILY:
            return 'pro'  # Usar Pro si Flash agotado pero Pro disponible
        else:
            return None  # Sin límites disponibles

    def generar_bendicion_ministerial(self, comentario: Dict, tipo_video: str) -> Optional[str]:
        """💎 Generar bendición personalizada del ministerio"""
        
        tipo_comentario = comentario['tipo']
        modelo = self.elegir_modelo_para_bendicion(tipo_comentario)
        
        if not modelo:
            return None
        
        # Contextos por tipo de video
        contextos_video = {
            'urgente': 'mensaje urgente de Dios que requiere atención inmediata',
            'arcangel_miguel': 'mensaje especial del Arcángel Miguel sobre protección divina',
            'jesus': 'palabra directa de Jesús para Su pueblo en estos tiempos',
            'prosperidad': 'decreto de prosperidad y abundancia divina',
            'bendiciones': 'bendiciones especiales del cielo',
            'oracion': 'guía para oración y comunión con Dios',
            'seres_queridos': 'mensaje de seres queridos en el cielo',
            'mensaje_general': 'mensaje de Dios para prosperidad divina'
        }
        
        contexto = contextos_video.get(tipo_video, contextos_video['mensaje_general'])
        
        # Prompts específicos para cada tipo
        prompts_ministeriales = {
            'peticion_oracion': f"""
Eres un pastor del ministerio "Prosperidad Divina" intercediendo con poder.

CONTEXTO: {contexto}
PETICIÓN DE ORACIÓN: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES MINISTERIALES:
- Ofrece oración poderosa y específica
- Declara provisión y milagros divinos
- Profetiza prosperidad sobre su situación
- Usa autoridad espiritual
- Incluye emojis de poder: 🙏⚡👑
- Máximo 3 líneas

ORACIÓN PROFÉTICA:
""",
            
            'testimonio_prosperidad': f"""
Eres un ministro celebrando testimonios en "Prosperidad Divina".

CONTEXTO: {contexto}
TESTIMONIO: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES DE CELEBRACIÓN:
- Celebra la bendición de Dios en su vida
- Declara más prosperidad y abundancia
- Profetiza multiplicación de bendiciones
- Da gloria a Dios por el testimonio
- Emojis de celebración: 🎉👑💎
- Máximo 2 líneas

CELEBRACIÓN PROFÉTICA:
""",
            
            'pregunta_espiritual': f"""
Eres un maestro espiritual del ministerio "Prosperidad Divina".

CONTEXTO: {contexto}
PREGUNTA: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES DE ENSEÑANZA:
- Da respuesta bíblica sobre prosperidad divina
- Incluye principio de abundancia del Reino
- Edifica la fe y esperanza
- Declara sabiduría divina sobre su vida
- Emojis de sabiduría: 📖✨💫
- Máximo 3 líneas

ENSEÑANZA PROFÉTICA:
""",
            
            'comentario_hiriente': f"""
Eres un ministro lleno de amor del ministerio "Prosperidad Divina".

CONTEXTO: {contexto}
COMENTARIO HIRIENTE: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES DE AMOR:
- Responde con amor sobrenatural de Cristo
- No argumentes, bendice abundantemente
- Declara prosperidad sobre quien critica
- Rompe toda maldición con bendición
- Emojis de amor: 💖🕊️✨
- Máximo 3 líneas

BENDICIÓN TRANSFORMADORA:
""",
            
            'expresion_fe': f"""
Eres un ministro edificante del ministerio "Prosperidad Divina".

CONTEXTO: {contexto}
EXPRESIÓN DE FE: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES DE EDIFICACIÓN:
- Fortalece y confirma su fe
- Declara crecimiento espiritual
- Profetiza manifestaciones de su fe
- Anima a seguir creyendo
- Emojis de fe: ⭐🙏💪
- Máximo 2 líneas

EDIFICACIÓN PROFÉTICA:
""",
            
            'agradecimiento': f"""
Eres un ministro gozoso del ministerio "Prosperidad Divina".

CONTEXTO: {contexto}
AGRADECIMIENTO: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES DE GOZO:
- Comparte el gozo por su gratitud
- Declara más razones para agradecer
- Profetiza abundancia por su corazón agradecido
- Bendice su actitud de gratitud
- Emojis de gozo: 😊🌟💝
- Máximo 2 líneas

BENDICIÓN DE GRATITUD:
""",
            
            'comentario_general': f"""
Eres un pastor amoroso del ministerio "Prosperidad Divina".

CONTEXTO: {contexto}
COMENTARIO: "{comentario['texto']}"
PERSONA: {comentario['autor']}

INSTRUCCIONES GENERALES:
- Bendice con prosperidad divina
- Declara favor y abundancia
- Usa tono cálido y edificante
- Relaciona con el mensaje del video
- Emojis de bendición: 🌟💎✨
- Máximo 2 líneas

BENDICIÓN GENERAL:
"""
        }
        
        prompt = prompts_ministeriales.get(tipo_comentario, prompts_ministeriales['comentario_general'])
        
        try:
            # Generar respuesta con modelo elegido
            if modelo == 'pro':
                response = self.pro_model.generate_content(prompt)
                self.stats['pro_usado'] += 1
                modelo_usado = "Pro (Premium)"
            else:
                response = self.flash_model.generate_content(prompt)
                self.stats['flash_usado'] += 1
                modelo_usado = "Flash (Rápida)"
            
            bendicion = response.text.strip()
            
            # Estadísticas por tipo
            if tipo_comentario == 'peticion_oracion':
                self.stats['peticiones_oracion'] += 1
            elif tipo_comentario == 'testimonio_prosperidad':
                self.stats['testimonios_prosperidad'] += 1
            
            if any(palabra in bendicion.lower() for palabra in ['prosperidad', 'abundancia', 'riqueza']):
                self.stats['respuestas_abundancia'] += 1
            
            # Marcar como bendecido
            self.estado_diario['comentarios_bendecidos_hoy'].append(comentario['id'])
            
            print(f"💎 {modelo_usado}: {comentario['autor']} - {tipo_comentario}")
            
            return bendicion
            
        except Exception as e:
            print(f"❌ Error generando bendición: {e}")
            self.stats['errores'] += 1
            
            # Bendición de respaldo
            return f"🙏 {comentario['autor']}, que la prosperidad divina del Altísimo sea derramada abundantemente sobre tu vida. ¡Bendiciones! 👑✨"

    def procesar_video_para_bendiciones(self, video: Dict) -> Dict:
        """📺 Procesar un video específico para enviar bendiciones"""
        
        video_id = video['id']
        titulo = video['titulo']
        tipo_video = video['tipo_detectado']
        
        print(f"\n📺 PROCESANDO: {titulo[:50]}...")
        print(f"🏷️ Tipo: {tipo_video}")
        
        # Obtener comentarios para bendecir
        comentarios = self.obtener_comentarios_para_bendecir(
            video_id, 
            self.config_ministerio['max_comentarios_por_video']
        )
        
        resultado = {
            'video_id': video_id,
            'titulo': titulo,
            'tipo_detectado': tipo_video,
            'comentarios_nuevos': len(comentarios),
            'respuestas_generadas': 0,
            'errores': 0,
            'ultima_revision': datetime.now().isoformat()
        }
        
        if not comentarios:
            print("   💤 Sin comentarios nuevos para bendecir")
            return resultado
        
        print(f"   💬 {len(comentarios)} comentarios para bendecir")
        
        # Procesar cada comentario
        for comentario in comentarios:
            # Verificar límites disponibles
            total_usado = self.stats['pro_usado'] + self.stats['flash_usado']
            if total_usado >= self.TOTAL_LIMIT:
                print(f"   ⚠️ Límite diario alcanzado ({self.TOTAL_LIMIT})")
                break
            
            # Generar bendición
            bendicion = self.generar_bendicion_ministerial(comentario, tipo_video)
            
            if bendicion:
                comentario['bendicion_generada'] = bendicion
                resultado['respuestas_generadas'] += 1
                self.stats['respuestas_exitosas'] += 1
            else:
                resultado['errores'] += 1
            
            # Pausa breve para no sobrecargar APIs
            time.sleep(0.1)
        
        return resultado

    def cargar_y_procesar_backlog(self) -> int:
        """📂 Procesar comentarios pendientes de días anteriores"""
        
        try:
            with open('backlog_prosperidad_divina.json', 'r', encoding='utf-8') as f:
                backlog = json.load(f)
        except FileNotFoundError:
            return 0
        
        if not backlog:
            return 0
        
        print(f"\n📂 PROCESANDO BACKLOG: {len(backlog)} comentarios pendientes")
        
        procesados = 0
        comentarios_restantes = []
        
        for comentario in backlog:
            # Verificar límites
            total_usado = self.stats['pro_usado'] + self.stats['flash_usado']
            if total_usado >= self.TOTAL_LIMIT:
                comentarios_restantes.append(comentario)
                continue
            
            # Procesar comentario del backlog
            bendicion = self.generar_bendicion_ministerial(comentario, 'mensaje_general')
            
            if bendicion:
                procesados += 1
                self.stats['respuestas_exitosas'] += 1
                self.stats['backlog_procesado'] += 1
            else:
                comentarios_restantes.append(comentario)
        
        # Guardar backlog restante
        with open('backlog_prosperidad_divina.json', 'w', encoding='utf-8') as f:
            json.dump(comentarios_restantes, f, indent=2, ensure_ascii=False)
        
        if procesados > 0:
            print(f"📂 Backlog procesado: {procesados} bendiciones enviadas")
        
        return procesados

    def ejecutar_ministerio_completo(self):
        """🚀 Ejecutar ciclo completo del ministerio digital"""
        
        print("👑 INICIANDO CICLO COMPLETO DEL MINISTERIO DIGITAL")
        print("="*70)
        
        hora_inicio = datetime.now()
        
        # 1. Detectar videos del ministerio
        videos_ministerio = self.obtener_videos_ministerio()
        
        if not videos_ministerio:
            print("⚠️ No se encontraron videos del ministerio para procesar")
            return
        
        # 2. Procesar backlog primero (alta prioridad)
        self.cargar_y_procesar_backlog()
        
        # 3. Procesar cada video para bendiciones
        resultados_videos = []
        
        for video in videos_ministerio:
            resultado = self.procesar_video_para_bendiciones(video)
            resultados_videos.append(resultado)
            
            # Verificar límites globales
            total_usado = self.stats['pro_usado'] + self.stats['flash_usado']
            if total_usado >= self.TOTAL_LIMIT:
                print(f"\n⚠️ Límite diario alcanzado: {total_usado}/{self.TOTAL_LIMIT}")
                break
        
        # 4. Guardar datos del ministerio
        self.guardar_resultados_ministerio(resultados_videos)
        self.guardar_estado_diario()
        
        # 5. Generar reporte final
        tiempo_total = datetime.now() - hora_inicio
        self.generar_reporte_final_ministerio(resultados_videos, tiempo_total)

    def guardar_resultados_ministerio(self, resultados: List[Dict]):
        """💾 Guardar todos los resultados del ministerio"""
        
        # Guardar estadísticas principales
        with open('stats_prosperidad_divina.json', 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        # Guardar información de videos procesados
        datos_videos = {
            'fecha': datetime.now().isoformat(),
            'total_videos': len(resultados),
            'videos': resultados
        }
        
        with open('videos_prosperidad_procesados.json', 'w', encoding='utf-8') as f:
            json.dump(datos_videos, f, indent=2, ensure_ascii=False)
        
        # Guardar resumen de tipos de respuesta
        tipos_respuesta = {}
        for resultado in resultados:
            for comentario in resultado.get('comentarios', []):
                tipo = comentario.get('tipo', 'general')
                tipos_respuesta[tipo] = tipos_respuesta.get(tipo, 0) + 1
        
        with open('resumen_tipos_respuesta.json', 'w', encoding='utf-8') as f:
            json.dump(tipos_respuesta, f, indent=2, ensure_ascii=False)

    def generar_reporte_final_ministerio(self, resultados: List[Dict], tiempo_ejecucion):
        """📊 Generar reporte final del ministerio"""
        
        total_bendiciones = sum(r['respuestas_generadas'] for r in resultados)
        total_comentarios = sum(r['comentarios_nuevos'] for r in resultados)
        total_usado = self.stats['pro_usado'] + self.stats['flash_usado']
        
        eficiencia = (total_usado / self.TOTAL_LIMIT) * 100 if total_usado > 0 else 0
        
        print(f"\n" + "="*70)
        print("👑 REPORTE FINAL DEL MINISTERIO DIGITAL")
        print("="*70)
        print(f"📊 ESTADÍSTICAS DE BENDICIONES:")
        print(f"   💎 Bendiciones enviadas: {total_bendiciones}")
        print(f"   💬 Comentarios analizados: {total_comentarios}")
        print(f"   🙏 Peticiones de oración: {self.stats['peticiones_oracion']}")
        print(f"   🎉 Testimonios celebrados: {self.stats['testimonios_prosperidad']}")
        print(f"   💫 Respuestas de abundancia: {self.stats['respuestas_abundancia']}")
        print(f"   📂 Backlog procesado: {self.stats['backlog_procesado']}")
        
        print(f"\n📊 USO DE RECURSOS MINISTERIALES:")
        print(f"   👑 Gemini Pro usado: {self.stats['pro_usado']}/{self.PRO_LIMIT_DAILY} (premium)")
        print(f"   ⚡ Gemini Flash usado: {self.stats['flash_usado']}/{self.FLASH_LIMIT_DAILY} (rápidas)")
        print(f"   📈 Total usado: {total_usado}/{self.TOTAL_LIMIT} ({eficiencia:.1f}%)")
        print(f"   💚 Margen disponible: {self.TOTAL_LIMIT - total_usado} bendiciones")
        
        print(f"\n🕐 EFICIENCIA MINISTERIAL:")
        print(f"   ⏱️ Tiempo de ejecución: {tiempo_ejecucion}")
        print(f"   📺 Videos procesados: {len(resultados)}")
        print(f"   ❌ Errores: {self.stats['errores']}")
        
        print(f"\n🎯 ESTADO DEL MINISTERIO:")
        if eficiencia >= 90:
            print("   🔥 MINISTERIO A MÁXIMA CAPACIDAD - Impacto total")
        elif eficiencia >= 70:
            print("   💪 MINISTERIO ACTIVO - Gran impacto")
        elif eficiencia >= 50:
            print("   ⚡ MINISTERIO EFICIENTE - Buen impacto")
        else:
            print("   📈 MINISTERIO CRECIENDO - Construyendo impacto")
        
        print(f"\n🔄 PRÓXIMA EJECUCIÓN:")
        print("   ⏰ En 4 horas automáticamente")
        print("   🎯 Continuando la expansión del Reino digital")
        print("   💎 Prosperidad Divina 24/7")
        print("="*70)

def main():
    """🚀 Función principal del ministerio"""
    
    try:
        bot = ProsperidadDivinaBot()
        bot.ejecutar_ministerio_completo()
        
        print("\n✅ CICLO MINISTERIAL COMPLETADO EXITOSAMENTE")
        print("👑 Prosperidad Divina expandiéndose automáticamente")
        
    except Exception as e:
        print(f"\n❌ Error en el ministerio digital: {e}")
        print("🙏 El ministerio continuará en la próxima ejecución")
        raise

if __name__ == "__main__":
    main()
