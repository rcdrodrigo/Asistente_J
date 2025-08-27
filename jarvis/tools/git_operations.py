"""
Herramienta avanzada de operaciones Git.
"""
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..exceptions import ToolError
from .base import BaseTool

logger = get_logger(__name__)

class GitTool:
    """Herramienta avanzada para operaciones Git."""
    
    def __init__(self, settings):
        self.settings = settings
        self.repo_path = os.getcwd()
        self.repo = None
        self._initialize_git()
    
    def _initialize_git(self):
        """Inicializa el repositorio Git."""
        try:
            from git import Repo, InvalidGitRepositoryError, NoSuchPathError
            
            try:
                self.repo = Repo(self.repo_path, search_parent_directories=True)
                self.repo_path = self.repo.working_dir
                logger.info(f"Repositorio Git inicializado en: {self.repo_path}")
            except (InvalidGitRepositoryError, NoSuchPathError):
                logger.warning("No se encontró un repositorio Git en el directorio actual")
                self.repo = None
                
        except ImportError:
            logger.warning("GitPython no está instalado. Algunas funcionalidades estarán limitadas.")
            self.repo = None
    
    async def execute(self, command: str, **kwargs) -> str:
        """Ejecuta un comando Git y devuelve el resultado."""
        if not command:
            return await self._get_status()
            
        # Mapeo de comandos a métodos
        command_map = {
            'status': self._get_status,
            'log': self._get_log,
            'diff': self._get_diff,
            'branch': self._get_branches,
            'info': self._get_repo_info,
            'remote': self._get_remotes,
            'contributors': self._get_contributors,
            'activity': self._get_activity,
            'summary': self._get_summary,
        }
        
        # Parsear el comando
        parts = command.strip().split()
        operation = parts[0].lower()
        
        # Si es un comando directo de Git
        if operation.startswith('!'):
            return await self._run_git_command(operation[1:], ' '.join(parts[1:]))
        
        # Si es una operación mapeada
        if operation in command_map:
            params = await self.parse_message_params(' '.join(parts[1:]), {})
            return await command_map[operation](**params)
        
        # Si no se reconoce, intentar ejecutarlo como comando Git
        return await self._run_git_command(operation, ' '.join(parts[1:]))
    
    async def _run_git_command(self, command: str, args: str = '') -> str:
        """Ejecuta un comando Git directamente."""
        try:
            cmd = f"git {command} {args}".strip()
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return f"❌ Error al ejecutar 'git {command}':\n{result.stderr}"
                
            return "\n".join(result) or f"✅ Comando 'git {command}' ejecutado correctamente."
        
        except Exception as e:
            return f"❌ Error al ejecutar comando Git: {str(e)}"

class GitTool(BaseTool):
    
    async def _get_status(self, **kwargs) -> str:
        """Muestra el estado actual del repositorio."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Obtener estado
            status = []
            
            # Cambios rastreados
            if self.repo.is_dirty():
                status.append("📝 **Cambios sin confirmar:**")
                
                # Cambios en el área de staging
                diff_index = self.repo.index.diff(self.repo.head.commit)
                if diff_index:
                    status.append("\n🟢 **Cambios preparados (staged):**")
                    for item in diff_index:
                        status.append(f"  • {item.a_path} ({item.change_type})")
                
                # Cambios en el working directory
                untracked = self.repo.untracked_files
                diff_workdir = self.repo.index.diff(None)
                
                if diff_workdir or untracked:
                    status.append("\n🔴 **Cambios no preparados:**")
                    
                    # Modificados pero no en staging
                    for item in diff_workdir:
                        status.append(f"  • {item.a_path} (modificado)")
                    
                    # Archivos sin seguimiento
                    for file in untracked[:10]:  # Mostrar solo los primeros 10
                        status.append(f"  • {file} (nuevo archivo)")
                    
                    if len(untracked) > 10:
                        status.append(f"  • ... y {len(untracked) - 10} archivos más sin seguimiento")
            else:
                status.append("✅ El directorio de trabajo está limpio.")
            
            # Información de la rama actual
            try:
                branch = self.repo.active_branch
                status.append(f"\n🌿 **Rama actual:** {branch.name}")
                
                # Verificar si hay commits sin hacer push
                if self.repo.remotes:
                    remote = self.repo.remotes.origin
                    if remote.exists():
                        remote_ref = f"{remote.name}/{branch.name}"
                        if remote_ref in self.repo.references:
                            ahead = len(list(self.repo.iter_commits(f"{remote_ref}..{branch.name}")))
                            behind = len(list(self.repo.iter_commits(f"{branch.name}..{remote_ref}")))
                            
                            if ahead or behind:
                                status.append(f"   ⬆️ {ahead} commits por delante, ⬇️ {behind} commits por detrás de {remote_ref}")
                            else:
                                status.append("   ✅ Sincronizado con el remoto")
            except Exception as e:
                logger.warning(f"Error obteniendo información de la rama: {e}")
            
            return "\n".join(status)
            
        except Exception as e:
            return f"❌ Error obteniendo el estado: {str(e)}"
    
    async def _get_log(self, count: int = 5, **kwargs) -> str:
        """Muestra el historial de commits."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Obtener los últimos N commits
            commits = list(self.repo.iter_commits(max_count=count))
            
            if not commits:
                return "ℹ️ No hay commits en el repositorio."
            
            # Formatear la salida
            result = [f"📜 **Últimos {len(commits)} commits:**\n"]
            
            for i, commit in enumerate(commits, 1):
                # Formato: [hash] (autor) fecha - mensaje
                short_hash = commit.hexsha[:7]
                author = commit.author.name
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M")
                message = commit.message.split('\n')[0][:60]  # Primera línea, máximo 60 caracteres
                
                result.append(f"{i}. `{short_hash}` - **{author}** - *{date}*")
                result.append(f"   {message}")
                
                # Mostrar etiquetas si las hay
                tags = [tag for tag in self.repo.tags if tag.commit == commit]
                if tags:
                    result.append(f"   🏷️ Tags: {', '.join(tag.name for tag in tags[:3])}" + 
                                ("..." if len(tags) > 3 else ""))
                
                result.append("")
            
            # Agregar información adicional
            result.append(f"\n💡 Usa `!git log N` para ver los últimos N commits (ej: `!git log 10`).")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo el historial: {str(e)}"
    
    async def _get_diff(self, target: str = None, **kwargs) -> str:
        """Muestra las diferencias en los archivos."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Determinar qué diferencias mostrar
            if target == 'staged':
                # Diferencias en el área de staging
                diff_index = self.repo.index.diff(self.repo.head.commit)
                title = "📋 **Cambios preparados (staged):**"
            else:
                # Diferencias en el working directory
                diff_index = self.repo.index.diff(None)
                title = "📋 **Cambios no preparados (working directory):**"
            
            if not diff_index:
                return (f"ℹ️ No hay cambios {target if target else 'en el directorio de trabajo'}.\n" 
                        "💡 Usa `git add <archivo>` para preparar cambios.")
            
            # Contadores para estadísticas
            total_additions = 0
            total_deletions = 0
            
            # Procesar cada archivo modificado
            result = [f"{title}\n"]
            
            for diff in diff_index:
                file_path = diff.a_path
                change_type = self._get_change_type(diff)
                
                # Obtener estadísticas de líneas modificadas
                stats = diff.diff.decode('utf-8')
                insertions = stats.count('\n+') - stats.count('\n+++')
                deletions = stats.count('\n-') - stats.count('\n---')
                
                total_additions += insertions
                total_deletions += deletions
                
                # Agregar información del archivo
                result.append(f"📄 **{file_path}** ({change_type})")
                result.append(f"   +{insertions}/-{deletions} líneas")
                
                # Mostrar un fragmento del diff (primeras 5 líneas)
                diff_lines = [line for line in stats.split('\n') if line and not line.startswith('diff --git')]
                result.extend([f"   {line}" for line in diff_lines[:5]])
                
                if len(diff_lines) > 5:
                    result.append(f"   ... y {len(diff_lines) - 5} líneas más")
                
                result.append("")
            
            # Mostrar estadísticas totales
            result.append(f"📊 **Total:** +{total_additions}/-{total_deletions} líneas en {len(diff_index)} archivos")
            
            # Sugerencias
            if target == 'staged':
                result.append("\n💡 Usa `git commit -m 'mensaje'` para confirmar los cambios.")
            else:
                result.append("\n💡 Usa `git add <archivo>` para preparar cambios o `git add .` para todos.")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo diferencias: {str(e)}"
    
    def _get_change_type(self, diff) -> str:
        """Determina el tipo de cambio en un diff."""
        if diff.new_file:
            return 'nuevo archivo'
        elif diff.deleted_file:
            return 'archivo eliminado'
        elif diff.renamed:
            return f'renombrado de {diff.rename_from} a {diff.rename_to}'
        elif diff.a_mode != diff.b_mode:
            return 'permisos modificados'
        else:
            return 'modificado'
    
    async def _get_branches(self, **kwargs) -> str:
        """Muestra información sobre las ramas."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            current_branch = self.repo.active_branch.name
            all_branches = list(self.repo.branches)
            
            # Información de ramas remotas
            remote_branches = []
            for remote in self.repo.remotes:
                remote_branches.extend(remote.refs)
            
            # Construir el resultado
            result = [
                f"🌿 **Ramas en el repositorio**\n",
                f"📍 **Rama actual:** `{current_branch}`\n",
                f"🏠 **Ramas locales ({len(all_branches)}):"
            ]
            
            # Mostrar ramas locales
            for branch in all_branches:
                is_current = "⭐" if branch.name == current_branch else "  "
                
                # Obtener información adicional de la rama
                try:
                    last_commit = branch.commit
                    last_date = last_commit.committed_datetime.strftime("%Y-%m-%d")
                    
                    # Calcular commits adelante/atrás
                    commits_ahead = len(list(self.repo.iter_commits(f'{current_branch}..{branch.name}')))
                    commits_behind = len(list(self.repo.iter_commits(f'{branch.name}..{current_branch}')))
                    
                    ahead_behind = ""
                    if commits_ahead > 0:
                        ahead_behind += f" ↑{commits_ahead}"
                    if commits_behind > 0:
                        ahead_behind += f" ↓{commits_behind}"
                    
                    result.append(f"{is_current} `{branch.name}`{ahead_behind} • {last_date}")
                except Exception as e:
                    logger.warning(f"Error obteniendo info de rama {branch.name}: {e}")
                    result.append(f"{is_current} `{branch.name}`")
            
            # Mostrar ramas remotas (solo las primeras 10)
            if remote_branches:
                result.append(f"\n🌐 **Ramas remotas ({len(remote_branches)}):")
                for ref in remote_branches[:10]:
                    result.append(f"  • `{ref.name}`")
                
                if len(remote_branches) > 10:
                    result.append(f"  • ... y {len(remote_branches) - 10} más")
            
            # Agregar comandos útiles
            result.append("""
💡 **Comandos útiles:**
  • `git checkout <rama>` - Cambiar a una rama existente
  • `git checkout -b <nueva>` - Crear y cambiar a una nueva rama
  • `git branch -d <rama>` - Eliminar una rama local
  • `git push origin <rama>` - Subir una rama al repositorio remoto
  • `git branch -a` - Mostrar todas las ramas (locales y remotas)""")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo información de ramas: {str(e)}"
    
    async def _get_remotes(self, **kwargs) -> str:
        """Muestra información sobre los remotos configurados."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            remotes = list(self.repo.remotes)
            
            if not remotes:
                return ("ℹ️ No hay remotos configurados en este repositorio.\n" 
                        "💡 Usa `git remote add origin <url>` para agregar uno.")
            
            result = ["🌍 **Repositorios remotos configurados:**\n"]
            
            for remote in remotes:
                result.append(f"🔗 **{remote.name}**")
                for url in remote.urls:
                    result.append(f"   {url}")
                
                # Obtener información adicional del remoto
                try:
                    fetch_info = next(remote.fetch())
                    result.append(f"   📌 {fetch_info.ref}")
                except Exception:
                    pass
                
                result.append("")
            
            # Agregar comandos útiles
            result.append("""
💡 **Comandos útiles:**
  • `git remote -v` - Ver URLs de los remotos
  • `git remote add <nombre> <url>` - Agregar un nuevo remoto
  • `git remote remove <nombre>` - Eliminar un remoto
  • `git fetch <remoto>` - Obtener cambios del remoto sin fusionar
  • `git pull <remoto> <rama>` - Obtener y fusionar cambios""")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo información de remotos: {str(e)}"
    
    async def _get_contributors(self, **kwargs) -> str:
        """Muestra información sobre los contribuidores del repositorio."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Obtener todos los commits
            commits = list(self.repo.iter_commits())
            
            if not commits:
                return "ℹ️ No hay commits en el repositorio."
            
            # Analizar contribuidores
            contributors = {}
            
            for commit in commits:
                author = commit.author.name
                email = commit.author.email
                
                if author not in contributors:
                    contributors[author] = {
                        'email': email,
                        'commits': 0,
                        'first_commit': commit.committed_datetime,
                        'last_commit': commit.committed_datetime,
                        'insertions': 0,
                        'deletions': 0
                    }
                
                contributors[author]['commits'] += 1
                
                # Actualizar fechas
                if commit.committed_datetime < contributors[author]['first_commit']:
                    contributors[author]['first_commit'] = commit.committed_datetime
                if commit.committed_datetime > contributors[author]['last_commit']:
                    contributors[author]['last_commit'] = commit.committed_datetime
                
                # Contar líneas modificadas (si está disponible)
                try:
                    stats = commit.stats.total
                    contributors[author]['insertions'] += stats.get('insertions', 0)
                    contributors[author]['deletions'] += stats.get('deletions', 0)
                except Exception:
                    pass
            
            # Ordenar por número de commits (descendente)
            sorted_contribs = sorted(
                contributors.items(),
                key=lambda x: x[1]['commits'],
                reverse=True
            )
            
            # Construir el resultado
            result = [
                f"👥 **Contribuidores del repositorio**\n",
                f"📊 **Total de commits:** {len(commits):,}",
                f"👤 **Total de contribuidores:** {len(contributors)}\n"
            ]
            
            # Mostrar los principales contribuidores
            result.append("🏆 **Principales contribuidores:**\n")
            
            for i, (author, stats) in enumerate(sorted_contribs[:10], 1):
                # Calcular período de contribución
                days_active = (stats['last_commit'] - stats['first_commit']).days
                days_active = max(1, days_active)  # Evitar división por cero
                
                commits_per_day = stats['commits'] / days_active
                
                result.append(
                    f"{i}. **{author}** ({stats['email']})"
                    f"\n   📅 {stats['first_commit'].strftime('%Y-%m-%d')} → {stats['last_commit'].strftime('%Y-%m-%d')} "
                    f"({days_active} días, {commits_per_day:.1f} commits/día)"
                    f"\n   📊 {stats['commits']:,} commits "
                    f"({(stats['commits'] / len(commits) * 100):.1f}% del total)"
                    f"\n   📝 +{stats['insertions']:,}/-{stats['deletions']:,} líneas\n"
                )
            
            # Mostrar estadísticas adicionales
            if len(sorted_contribs) > 10:
                result.append(f"\n... y {len(sorted_contribs) - 10} contribuidores más.")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo información de contribuidores: {str(e)}"
    
    async def _get_activity(self, days: int = 30, **kwargs) -> str:
        """Muestra la actividad reciente en el repositorio."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Calcular fecha de inicio
            since_date = datetime.now() - timedelta(days=days)
            
            # Obtener commits recientes
            recent_commits = [
                commit for commit in self.repo.iter_commits(since=since_date)
            ]
            
            if not recent_commits:
                return f"ℹ️ No hay actividad en los últimos {days} días."
            
            # Analizar actividad por día y por autor
            activity_by_day = {}
            activity_by_author = {}
            
            for commit in recent_commits:
                # Agrupar por día
                day_key = commit.committed_datetime.strftime("%Y-%m-%d")
                if day_key not in activity_by_day:
                    activity_by_day[day_key] = 0
                activity_by_day[day_key] += 1
                
                # Agrupar por autor
                author = commit.author.name
                if author not in activity_by_author:
                    activity_by_author[author] = 0
                activity_by_author[author] += 1
            
            # Ordenar por fecha
            sorted_days = sorted(activity_by_day.items(), key=lambda x: x[0])
            
            # Construir el resultado
            result = [
                f"📈 **Actividad en los últimos {days} días**\n",
                f"📊 **Total de commits:** {len(recent_commits):,}",
                f"📅 **Días con actividad:** {len(activity_by_day)}/{days}",
                f"👥 **Contribuidores activos:** {len(activity_by_author)}\n"
            ]
            
            # Mostrar actividad por autor
            result.append("👥 **Actividad por autor:**\n")
            
            for author, count in sorted(
                activity_by_author.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                result.append(f"  • **{author}**: {count} commits ({(count / len(recent_commits) * 100):.1f}%)")
            
            # Mostrar actividad por día (últimos 14 días)
            result.append("\n📅 **Actividad diaria (últimos 14 días):**\n")
            
            # Generar gráfico ASCII
            max_commits = max(activity_by_day.values(), default=1)
            days_to_show = min(14, len(sorted_days))
            
            for day, count in sorted_days[-days_to_show:]:
                # Calcular porcentaje para la barra
                percentage = (count / max_commits) * 50  # 50 caracteres de ancho máximo
                bar = '█' * int(percentage) + '░' * (50 - int(percentage))
                
                result.append(f"  {day}: {bar} {count}")
            
            # Agregar estadísticas adicionales
            avg_commits_per_day = len(recent_commits) / days
            busiest_day, busiest_count = max(activity_by_day.items(), key=lambda x: x[1], default=('', 0))
            
            result.extend([
                "\n📊 **Estadísticas adicionales:**",
                f"  • Promedio de commits/día: {avg_commits_per_day:.1f}",
                f"  • Día más activo: {busiest_day} ({busiest_count} commits)",
                f"  • Último commit: {recent_commits[0].committed_datetime.strftime('%Y-%m-%d %H:%M')}"
            ])
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo actividad reciente: {str(e)}"
    
    async def _get_summary(self, **kwargs) -> str:
        """Muestra un resumen del estado del repositorio."""
        if not self.repo:
            return "❌ No se encontró un repositorio Git en el directorio actual."
        
        try:
            # Obtener información básica
            branch = self.repo.active_branch.name
            is_dirty = self.repo.is_dirty()
            untracked = len(self.repo.untracked_files)
            
            # Contar commits
            total_commits = len(list(self.repo.iter_commits()))
            
            # Obtener información de remotos
            remotes = [(r.name, list(r.urls)) for r in self.repo.remotes]
            
            # Obtener información de tags
            tags = [tag.name for tag in self.repo.tags]
            
            # Construir el resumen
            result = [
                "📋 **Resumen del repositorio**\n",
                f"🌿 **Rama actual:** `{branch}`",
                f"📊 **Total de commits:** {total_commits:,}",
                f"🏷️ **Tags:** {len(tags)}",
                f"🌍 **Remotos:** {len(remotes)}",
                "",
                "📂 **Estado actual:**"
            ]
            
            return "\n".join(result)
            
        except Exception as e:
            return f"❌ Error obteniendo resumen: {str(e)}"
    name = "git"
    description = "Ejecuta comandos git: !git status | !git log -1"

    def run(self, *args) -> str:
        if not args:
            return self.help()
        try:
            out = subprocess.check_output(["git", *args], stderr=subprocess.STDOUT)
            return out.decode("utf-8", errors="ignore")
        except subprocess.CalledProcessError as e:
            return e.output.decode("utf-8", errors="ignore")
        except FileNotFoundError:
            return "git no está instalado o no está en PATH."
