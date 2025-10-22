"""
Module d'intégration Ollama pour le bot Discord
Permet d'utiliser des modèles d'IA locaux via Ollama
"""

import asyncio
import json
import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Test d'import d'Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ollama = None

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "deepseek-r1:8b")
MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "2000"))

logger = logging.getLogger(__name__)

class OllamaManager:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host
        self.api_key = OLLAMA_API_KEY
        self.default_model = DEFAULT_MODEL
        
        if not OLLAMA_AVAILABLE:
            self.client = None
            self.available_models = []
            return
            
        # Configuration du client avec clé API si disponible
        if OLLAMA_API_KEY:
            self.client = ollama.Client(host=host, headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"})
        else:
            self.client = ollama.Client(host=host)
        self.available_models = []
        
    async def initialize(self):
        """Initialise la connexion Ollama et charge les modèles disponibles"""
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama non disponible - module non installé")
            return False
            
        try:
            await self.refresh_models()
            logger.info(f"Ollama initialisé avec {len(self.available_models)} modèles")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation d'Ollama : {e}")
            return False
    
    async def refresh_models(self):
        """Actualise la liste des modèles disponibles"""
        if not OLLAMA_AVAILABLE or not self.client:
            self.available_models = []
            return
            
        try:
            # Utiliser asyncio.to_thread pour rendre l'appel synchrone asynchrone
            models_response = await asyncio.to_thread(self.client.list)
            self.available_models = [model['name'] for model in models_response['models']]
            logger.info(f"Modèles disponibles : {self.available_models}")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles : {e}")
            self.available_models = []
    
    async def chat(self, message: str, model: str = DEFAULT_MODEL, system_prompt: str = None) -> Optional[str]:
        """
        Envoie un message au modèle Ollama
        
        Args:
            message: Le message de l'utilisateur
            model: Le modèle à utiliser
            system_prompt: Prompt système optionnel
            
        Returns:
            La réponse du modèle ou None en cas d'erreur
        """
        if not OLLAMA_AVAILABLE or not self.client:
            return "❌ Ollama non disponible sur ce système"
            
        if model not in self.available_models:
            return f"❌ Modèle '{model}' non disponible. Modèles disponibles : {', '.join(self.available_models)}"
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user', 
                'content': message
            })
            
            # Appel asynchrone à Ollama
            response = await asyncio.to_thread(
                self.client.chat,
                model=model,
                messages=messages,
                options={
                    'num_predict': MAX_TOKENS,
                    'temperature': 0.7
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel Ollama : {e}")
            return f"❌ Erreur lors de la génération : {str(e)}"
    
    async def stream_chat(self, message: str, model: str = DEFAULT_MODEL, system_prompt: str = None):
        """
        Chat en streaming (pour de longues réponses)
        
        Yields:
            Chunks de la réponse au fur et à mesure
        """
        if model not in self.available_models:
            yield f"❌ Modèle '{model}' non disponible."
            return
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': message
            })
            
            # Stream response
            stream = await asyncio.to_thread(
                self.client.chat,
                model=model,
                messages=messages,
                stream=True,
                options={
                    'num_predict': MAX_TOKENS,
                    'temperature': 0.7
                }
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Erreur lors du streaming Ollama : {e}")
            yield f"❌ Erreur lors de la génération : {str(e)}"
    
    async def pull_model(self, model_name: str) -> bool:
        """
        Télécharge un nouveau modèle
        
        Args:
            model_name: Nom du modèle à télécharger
            
        Returns:
            True si succès, False sinon
        """
        try:
            await asyncio.to_thread(self.client.pull, model_name)
            await self.refresh_models()
            return True
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du modèle {model_name} : {e}")
            return False
    
    def get_model_info(self, model: str) -> Optional[Dict]:
        """Récupère les informations d'un modèle"""
        try:
            return self.client.show(model)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du modèle {model} : {e}")
            return None

# Instance globale
ollama_manager = OllamaManager()

# Prompts système prédéfinis pour différents contextes
SYSTEM_PROMPTS = {
    "assistant": "Tu es un assistant Discord utile et amical. Réponds de manière concise et claire. Si la réponse est longue, structure-la avec des emojis et des puces.",
    "rp": "Tu es un assistant spécialisé dans le rôleplay géopolitique. Aide les joueurs avec leurs stratégies, leurs histoires et leurs questions sur le monde de Pax Ruinae.",
    "moderation": "Tu es un assistant de modération Discord. Aide à analyser les messages et suggère des actions de modération appropriées.",
    "creative": "Tu es un assistant créatif. Aide à générer des idées, des histoires, des descriptions et du contenu créatif pour le serveur Discord.",
    "technical": "Tu es un assistant technique spécialisé dans Discord.py et le développement de bots. Aide avec le code et les questions techniques."
}

async def initialize_ollama():
    """Initialise Ollama au démarrage du bot"""
    if not OLLAMA_AVAILABLE:
        return False
    return await ollama_manager.initialize()

async def get_ai_response(message: str, context: str = "assistant", model: str = DEFAULT_MODEL) -> str:
    """
    Interface simplifiée pour obtenir une réponse IA
    
    Args:
        message: Message de l'utilisateur
        context: Contexte du prompt système (assistant, rp, moderation, etc.)
        model: Modèle à utiliser
        
    Returns:
        Réponse de l'IA
    """
    if not OLLAMA_AVAILABLE:
        return "❌ Ollama non disponible sur ce système"
        
    system_prompt = SYSTEM_PROMPTS.get(context, SYSTEM_PROMPTS["assistant"])
    return await ollama_manager.chat(message, model, system_prompt)
