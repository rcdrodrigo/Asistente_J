"""
Herramienta avanzada de búsqueda de documentación técnica.
"""
import re
import aiohttp
import asyncio
from urllib.parse import quote, urljoin
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from ..utils.logger import get_logger
from ..exceptions import ToolError
from .base import BaseTool

logger = get_logger(__name__)


class DocumentationTool:
    """Herramienta completa de búsqueda de documentación técnica."""
    
    def __init__(self, settings):
        self.settings = settings
        self.session = None
        
        # URLs base para diferentes fuentes de documentación
        self.doc_sources = {
            'python': {
                'name': 'Python Official Docs',
                'search_url': 'https://docs.python.org/3/search.html?q={}',
                'base_url': 'https://docs.python.org/3/',
            },
            'javascript': {
                'name': 'MDN Web Docs',
                'search_url': 'https://developer.mozilla.org/en-US/search?q={}',
                'base_url': 'https://developer.mozilla.org/',
            },
            'react': {
                'name': 'React Documentation',
                'search_url': 'https://react.dev/search?q={}',
                'base_url': 'https://react.dev/',
            },
            'node': {
                'name': 'Node.js Documentation',
                'search_url': 'https://nodejs.org/api/',
                'base_url': 'https://nodejs.org/',
            },
            'stackoverflow': {
                'name': 'Stack Overflow',
                'search_url': 'https://stackoverflow.com/search?q={}',
                'base_url': 'https://stackoverflow.com/',
            },
            'github': {
                'name': 'GitHub',
                'search_url': 'https://github.com/search?q={}&type=repositories',
                'base_url': 'https://github.com/',
            },
        }
        
        # Documentación específica por tecnología
        self.tech_docs = {
            'django': 'https://docs.djangoproject.com/en/stable/search/?q={}',
            'flask': 'https://flask.palletsprojects.com/en/stable/search/?q={}',
            'fastapi': 'https://fastapi.tiangolo.com/',
            'pandas': 'https://pandas.pydata.org/docs/search.html?q={}',
            'numpy': 'https://numpy.org/doc/stable/search.html?q={}',
            'tensorflow': 'https://www.tensorflow.org/api_docs/python/search?q={}',
            'pytorch': 'https://pytorch.org/docs/stable/search.html?q={}',
            'vue': 'https://vuejs.org/guide/',
            'angular': 'https://angular.io/docs',
            'express': 'https://expressjs.com/',
        }
    
    async def initialize(self):
        """Inicializa la sesión HTTP."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'JARVIS Documentation Bot 2.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
    
    async def execute(self, query: str, source: str = "python", max_results: int = 5, **kwargs) -> str:
        """Ejecuta búsqueda de documentación."""
        await self.initialize()
        
        try:
            # Validar parámetros
            if not query or len(query.strip()) < 2:
                return "❌ Query de búsqueda demasiado corta"
            
            if source not in self.doc_sources and source not in self.tech_docs:
                available = ', '.join(list(self.doc_sources.keys()) + list(self.tech_docs.keys()))
                return f"❌ Fuente no disponible: {source}\n\n💡 Disponibles: {available}"
            
            # Realizar búsqueda según la fuente
            if source in self.doc_sources:
                return await self._search_main_source(query, source, max_results)
            else:
                return await self._search_tech_specific(query, source, max_results)
                
        except Exception as e:
            logger.error(f"Error buscando documentación: {e}")
            return f"❌ Error buscando documentación: {str(e)}"
    
    async def _search_main_source(self, query: str, source: str, max_results: int) -> str:
        """Busca en fuentes principales de documentación."""
        doc_info = self.doc_sources[source]
        search_url = doc_info['search_url'].format(quote(query))
        
        result = f"""🔍 **Búsqueda en {doc_info['name']}**

📝 **Query:** {query}
🔗 **URL de búsqueda:** {search_url}

"""
        
        if source == 'python':
            result += await self._get_python_suggestions(query)
        elif source == 'javascript':
            result += await self._get_javascript_suggestions(query)
        elif source == 'react':
            result += await self._get_react_suggestions(query)
        elif source == 'stackoverflow':
            result += await self._get_stackoverflow_suggestions(query)
        else:
            result += self._get_generic_suggestions(query, source)
        
        return result
    
    async def _get_python_suggestions(self, query: str) -> str:
        """Sugerencias específicas para Python."""
        suggestions = {
            # Tipos de datos
            'list': {
                'desc': 'Listas en Python - estructuras mutables ordenadas',
                'examples': ['append()', 'extend()', 'pop()', 'remove()', 'sort()'],
                'docs': 'https://docs.python.org/3/tutorial/datastructures.html#more-on-lists'
            },
            'dict': {
                'desc': 'Diccionarios - estructuras clave-valor',
                'examples': ['get()', 'keys()', 'values()', 'items()', 'update()'],
                'docs': 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries'
            },
            'string': {
                'desc': 'Cadenas de texto y métodos de string',
                'examples': ['split()', 'join()', 'replace()', 'strip()', 'format()'],
                'docs': 'https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str'
            },
            
            # Conceptos
            'function': {
                'desc': 'Funciones en Python - definición y uso',
                'examples': ['def función()', 'parámetros', 'return', 'lambda', 'decoradores'],
                'docs': 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions'
            },
            'class': {
                'desc': 'Clases y programación orientada a objetos',
                'examples': ['__init__()', 'métodos', 'herencia', 'propiedades'],
                'docs': 'https://docs.python.org/3/tutorial/classes.html'
            },
            'async': {
                'desc': 'Programación asíncrona con async/await',
                'examples': ['async def', 'await', 'asyncio', 'corrutinas'],
                'docs': 'https://docs.python.org/3/library/asyncio.html'
            },
            
            # Bibliotecas
            'pandas': {
                'desc': 'Análisis de datos con Pandas',
                'examples': ['DataFrame', 'Series', 'read_csv()', 'groupby()'],
                'docs': 'https://pandas.pydata.org/docs/'
            },
            'numpy': {
                'desc': 'Computación científica con NumPy',
                'examples': ['arrays', 'reshape()', 'dot()', 'linspace()'],
                'docs': 'https://numpy.org/doc/stable/'
            },
            'requests': {
                'desc': 'Realizar peticiones HTTP',
                'examples': ['get()', 'post()', 'json()', 'headers', 'params'],
                'docs': 'https://requests.readthedocs.io/en/latest/'
            }
        }
        
        query_lower = query.lower()
        
        # Buscar coincidencias exactas
        for key, info in suggestions.items():
            if key in query_lower:
                result = f"📚 **{key.title()}**\n"
                result += f"💡 {info['desc']}\n\n"
                result += f"🔧 **Métodos/Conceptos relacionados:**\n"
                result += f"  • {', '.join(info['examples'])}\n\n"
                result += f"📖 **Documentación oficial:**\n"
                result += f"  🔗 {info['docs']}\n\n"
                return result
        
        # Sugerencias generales si no hay coincidencia exacta
        return f"""💡 **Recursos recomendados para "{query}":**

📖 **Documentación oficial Python:**
  🔗 https://docs.python.org/3/search.html?q={quote(query)}

🎓 **Tutoriales recomendados:**
  • Tutorial oficial: https://docs.python.org/3/tutorial/
  • Real Python: https://realpython.com/search/?q={quote(query)}
  • Python.org: https://wiki.python.org/moin/

📚 **Recursos adicionales:**
  • PyPI (paquetes): https://pypi.org/search/?q={quote(query)}
  • Stack Overflow: https://stackoverflow.com/questions/tagged/python+{quote(query)}
  • GitHub: https://github.com/search?q={quote(query)}+language:python

💻 **Ejemplos de código:**
  • Buscar en GitHub con: `{query} python example`
  • Consultar documentación interactiva con: `help({query})`
"""
    
    async def _get_javascript_suggestions(self, query: str) -> str:
        """Sugerencias específicas para JavaScript."""
        js_topics = {
            'array': {
                'desc': 'Arrays en JavaScript - métodos y manipulación',
                'examples': ['map()', 'filter()', 'reduce()', 'forEach()', 'find()'],
                'docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array'
            },
            'object': {
                'desc': 'Objetos en JavaScript',
                'examples': ['Object.keys()', 'Object.values()', 'destructuring', 'spread operator'],
                'docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object'
            },
            'function': {
                'desc': 'Funciones en JavaScript',
                'examples': ['arrow functions', 'closures', 'callback', 'async/await'],
                'docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions'
            },
            'promise': {
                'desc': 'Promesas para programación asíncrona',
                'examples': ['then()', 'catch()', 'async/await', 'Promise.all()'],
                'docs': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise'
            },
            'dom': {
                'desc': 'Manipulación del DOM',
                'examples': ['getElementById()', 'querySelector()', 'addEventListener()'],
                'docs': 'https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model'
            }
        }
        
        query_lower = query.lower()
        
        for key, info in js_topics.items():
            if key in query_lower:
                result = f"🟨 **JavaScript: {key.title()}**\n"
                result += f"💡 {info['desc']}\n\n"
                result += f"⚡ **Métodos/Conceptos clave:**\n"
                result += f"  • {', '.join(info['examples'])}\n\n"
                result += f"📖 **MDN Documentation:**\n"
                result += f"  🔗 {info['docs']}\n\n"
                return result
        
        return f"""💡 **Recursos JavaScript para "{query}":**

📖 **MDN Web Docs (recomendado):**
  🔗 https://developer.mozilla.org/en-US/search?q={quote(query)}

🎓 **Recursos de aprendizaje:**
  • JavaScript.info: https://javascript.info/
  • W3Schools: https://www.w3schools.com/js/
  • Eloquent JavaScript: https://eloquentjavascript.net/

🛠️ **Herramientas y frameworks:**
  • Node.js docs: https://nodejs.org/en/docs/
  • React docs: https://react.dev/
  • Vue.js: https://vuejs.org/

💻 **Ejemplos prácticos:**
  • CodePen: https://codepen.io/search/pens?q={quote(query)}
  • JSFiddle: https://jsfiddle.net/
  • Stack Overflow: https://stackoverflow.com/questions/tagged/javascript+{quote(query)}
"""
    
    async def _get_react_suggestions(self, query: str) -> str:
        """Sugerencias específicas para React."""
        react_concepts = {
            'hook': {
                'desc': 'React Hooks - lógica de estado en componentes funcionales',
                'examples': ['useState', 'useEffect', 'useContext', 'useReducer', 'custom hooks'],
                'docs': 'https://react.dev/reference/react'
            },
            'component': {
                'desc': 'Componentes React - bloques de construcción de UI',
                'examples': ['functional components', 'props', 'JSX', 'composition'],
                'docs': 'https://react.dev/learn/your-first-component'
            },
            'state': {
                'desc': 'Manejo de estado en React',
                'examples': ['useState', 'setState', 'state management', 'Redux'],
                'docs': 'https://react.dev/learn/managing-state'
            },
            'effect': {
                'desc': 'Efectos secundarios con useEffect',
                'examples': ['componentDidMount', 'cleanup', 'dependencies', 'side effects'],
                'docs': 'https://react.dev/reference/react/useEffect'
            }
        }
        
        query_lower = query.lower()
        
        for key, info in react_concepts.items():
            if key in query_lower:
                result = f"⚛️ **React: {key.title()}**\n"
                result += f"💡 {info['desc']}\n\n"
                result += f"🔧 **Conceptos relacionados:**\n"
                result += f"  • {', '.join(info['examples'])}\n\n"
                result += f"📖 **Documentación oficial:**\n"
                result += f"  🔗 {info['docs']}\n\n"
                return result
        
        return f"""⚛️ **Recursos React para "{query}":**

📖 **Documentación oficial React:**
  🔗 https://react.dev/learn

🎓 **Guías de aprendizaje:**
  • React Tutorial: https://react.dev/learn/tutorial-tic-tac-toe
  • React Hooks: https://react.dev/reference/react
  • React Patterns: https://reactpatterns.com/

🛠️ **Herramientas del ecosistema:**
  • Create React App: https://create-react-app.dev/
  • Next.js: https://nextjs.org/docs
  • React Router: https://reactrouter.com/

💻 **Ejemplos y práctica:**
  • CodeSandbox: https://codesandbox.io/search?query={quote(query)}
  • React Examples: https://reactjsexample.com/
"""
    
    async def _get_stackoverflow_suggestions(self, query: str) -> str:
        """Sugerencias para búsquedas en Stack Overflow."""
        return f"""🟠 **Stack Overflow - "{query}"**

🔍 **Estrategias de búsqueda efectiva:**

🎯 **Términos recomendados:**
  • `{query} tutorial`
  • `{query} example`
  • `{query} best practices`
  • `how to {query}`
  • `{query} error fix`

📋 **Tags útiles para filtrar:**
  • `[python]` - Para preguntas de Python
  • `[javascript]` - Para JavaScript
  • `[react]` - Para React
  • `[node.js]` - Para Node.js
  • `[html]` `[css]` - Para web frontend

🔗 **Enlaces directos:**
  • Búsqueda general: https://stackoverflow.com/search?q={quote(query)}
  • Preguntas más votadas: https://stackoverflow.com/search?tab=votes&q={quote(query)}
  • Preguntas recientes: https://stackoverflow.com/search?tab=newest&q={quote(query)}

💡 **Consejos para mejores resultados:**
  • Incluye el lenguaje de programación en tu búsqueda
  • Busca error messages exactos entre comillas
  • Revisa preguntas con muchos votos positivos
  • Lee tanto la pregunta como las respuestas aceptadas
"""
    
    def _get_generic_suggestions(self, query: str, source: str) -> str:
        """Sugerencias genéricas para otras fuentes."""
        source_info = self.doc_sources.get(source, {'name': source, 'search_url': '#'})
        
        return f"""🔍 **Búsqueda en {source_info['name']}**

📝 **Término de búsqueda:** {query}

💡 **Sugerencias para mejorar tu búsqueda:**
  • Usa términos específicos en inglés
  • Incluye el contexto (ej: "python {query}")
  • Busca ejemplos de código con "{query} example"
  • Consulta documentación oficial primero

🔗 **Recursos adicionales:**
  • Documentación oficial del proyecto
  • GitHub repositories relacionados
  • Tutoriales y guías de la comunidad
  • Stack Overflow para problemas específicos

🎯 **Refinamientos sugeridos:**
  • `{query} tutorial`
  • `{query} documentation`
  • `{query} getting started`
  • `{query} best practices`
"""
    
    async def _search_tech_specific(self, query: str, tech: str, max_results: int) -> str:
        """Busca en documentación específica de tecnologías."""
        if tech not in self.tech_docs:
            return f"❌ Documentación no disponible para: {tech}"
        
        base_url = self.tech_docs[tech]
        
        return f"""📚 **Documentación de {tech.title()}**

🔍 **Búsqueda:** {query}
🔗 **Documentación:** {base_url}

{await self._get_tech_specific_info(tech, query)}
"""
    
    async def _get_tech_specific_info(self, tech: str, query: str) -> str:
        """Información específica por tecnología."""
        tech_info = {
            'django': {
                'desc': 'Framework web de alto nivel para Python',
                'common_topics': ['models', 'views', 'urls', 'templates', 'forms', 'admin'],
                'docs': 'https://docs.djangoproject.com/',
                'tutorial': 'https://docs.djangoproject.com/en/stable/intro/tutorial01/'
            },
            'flask': {
                'desc': 'Micro framework web para Python',
                'common_topics': ['routes', 'templates', 'forms', 'database', 'blueprints'],
                'docs': 'https://flask.palletsprojects.com/',
                'tutorial': 'https://flask.palletsprojects.com/en/stable/tutorial/'
            },
            'fastapi': {
                'desc': 'Framework moderno y rápido para APIs con Python',
                'common_topics': ['path parameters', 'query parameters', 'request body', 'response model'],
                'docs': 'https://fastapi.tiangolo.com/',
                'tutorial': 'https://fastapi.tiangolo.com/tutorial/'
            },
            'pandas': {
                'desc': 'Biblioteca de análisis de datos para Python',
                'common_topics': ['DataFrame', 'Series', 'read_csv', 'groupby', 'merge'],
                'docs': 'https://pandas.pydata.org/docs/',
                'tutorial': 'https://pandas.pydata.org/docs/getting_started/intro_tutorials/'
            }
        }
        
        if tech in tech_info:
            info = tech_info[tech]
            result = f"💡 **{tech.title()}:** {info['desc']}\n\n"
            result += f"🔧 **Temas comunes:**\n"
            result += f"  • {', '.join(info['common_topics'])}\n\n"
            result += f"📖 **Recursos principales:**\n"
            result += f"  • Documentación: {info['docs']}\n"
            result += f"  • Tutorial: {info['tutorial']}\n\n"
            return result
        
        return f"💡 Consulta la documentación oficial de {tech} para información detallada.\n\n"
    
    async def cleanup(self):
        """Limpia la sesión HTTP."""
        if self.session:
            await self.session.close()
    
    async def parse_message_params(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea parámetros desde el mensaje del usuario."""
        import re
        
        # Extraer query de búsqueda
        search_patterns = [
            r'busca\s+(?:información\s+(?:sobre|de)\s+)?(.+)',
            r'search\s+(?:for\s+)?(.+)',
            r'documentación\s+(?:de|sobre)\s+(.+)',
            r'docs?\s+(.+)',
            r'ayuda\s+con\s+(.+)',
            r'cómo\s+(.+)',
            r'how\s+to\s+(.+)',
            r'what\s+is\s+(.+)',
            r'qué\s+es\s+(.+)'
        ]
        
        query = ""
        for pattern in search_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                break
        
        # Si no se encontró patrón, usar mensaje completo
        if not query:
            query = message.strip()
        
        # Determinar fuente según contexto
        source = "python"  # por defecto
        message_lower = message.lower()
        
        # Mapeo de palabras clave a fuentes
        source_keywords = {
            'python': ['python', 'py', 'pandas', 'numpy', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'npm'],
            'react': ['react', 'jsx', 'hooks', 'component'],
            'stackoverflow': ['stackoverflow', 'stack', 'error', 'problema', 'bug'],
            'github': ['github', 'repo', 'repository', 'código'],
        }
        
        for src, keywords in source_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                source = src
                break
        
        # Tecnologías específicas
        tech_keywords = {
            'django': ['django', 'orm', 'models'],
            'flask': ['flask', 'jinja'],
            'fastapi': ['fastapi', 'api', 'rest'],
            'pandas': ['pandas', 'dataframe', 'series'],
            'numpy': ['numpy', 'array', 'matrix'],
            'tensorflow': ['tensorflow', 'tensor', 'keras'],
            'pytorch': ['pytorch', 'torch'],
            'vue': ['vue', 'vuejs'],
            'angular': ['angular'],
            'express': ['express', 'expressjs']
        }
        
        for tech, keywords in tech_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                source = tech
                break
        
        return {
            'query': query,
            'source': source,
            'max_results': 5
        }


class DocTool(BaseTool):
    name = "docs"
    description = "Busca documentación técnica: !docs python list | !docs javascript array"
    
    def __init__(self, settings):
        super().__init__(settings)
        self.doc_tool = DocumentationTool(settings)
    
    async def run(self, *args) -> str:
        if not args:
            return self.help()
            
        # Unir los argumentos en un solo string
        query = ' '.join(args)
        
        # Parsear parámetros del mensaje
        params = await self.doc_tool.parse_message_params(query, {})
        
        # Ejecutar la búsqueda
        return await self.doc_tool.execute(**params)
    
    def help(self) -> str:
        return """📚 **Ayuda de Documentación**

Busca documentación técnica en varias fuentes.

**Uso:**
  • `!docs <término>` - Busca en la documentación de Python por defecto
  • `!docs <lenguaje> <término>` - Busca en la documentación específica
  • `!docs react hooks` - Busca sobre React Hooks
  • `!docs javascript array` - Busca sobre arrays en JavaScript

**Fuentes disponibles:**
  • python, javascript, react, node, django, flask, pandas, numpy, etc.
  • stackoverflow - Para buscar en Stack Overflow
  • github - Para buscar en GitHub

**Ejemplos:**
  • `!docs list comprehension`
  • `!docs javascript fetch api`
  • `!docs django models`
  • `!docs stackoverflow error 404`
"""
        return """📚 **Ayuda de Documentación**

Busca documentación técnica en varias fuentes.

**Uso:**
  • `!docs <término>` - Busca en la documentación de Python por defecto
  • `!docs <lenguaje> <término>` - Busca en la documentación específica
  • `!docs react hooks` - Busca sobre React Hooks
  • `!docs javascript array` - Busca sobre arrays en JavaScript

**Fuentes disponibles:**
  • python, javascript, react, node, django, flask, pandas, numpy, etc.
  • stackoverflow - Para buscar en Stack Overflow
  • github - Para buscar en GitHub

**Ejemplos:**
  • `!docs list comprehension`
  • `!docs javascript fetch api`
  • `!docs django models`
  • `!docs stackoverflow error 404`
"""
