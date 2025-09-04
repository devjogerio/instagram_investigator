import re
import nltk
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Baixa recursos necessários do NLTK de forma segura
def download_nltk_resources():
    """Baixa recursos do NLTK de forma segura."""
    try:
        nltk.data.find('tokenizers/punkt')
    except (LookupError, Exception):
        try:
            nltk.download('punkt', quiet=True)
        except Exception:
            pass  # Ignora erros de download
    
    try:
        nltk.data.find('corpora/stopwords')
    except (LookupError, Exception):
        try:
            nltk.download('stopwords', quiet=True)
        except Exception:
            pass  # Ignora erros de download

# Tenta baixar recursos do NLTK
download_nltk_resources()

class CrossPlatformAnalyzer:
    """
    Classe para analisar dados entre múltiplas plataformas de redes sociais.
    Fornece análise cruzada de identidade, conteúdo e padrões de atividade.
    """
    
    def __init__(self):
        """
        Inicializa o analisador de plataformas cruzadas.
        """
        self.supported_platforms = ["instagram", "facebook", "twitter", "linkedin", "tiktok"]
        
        # Inicializa stopwords de forma segura
        try:
            self.stop_words = set(stopwords.words('english') + stopwords.words('portuguese'))
        except Exception:
            # Fallback para stopwords básicas se o NLTK não estiver disponível
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'])
    
    def analyze_cross_platform_data(self, data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analisa dados de múltiplas plataformas para encontrar correlações e insights.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            Dict: Resultados da análise cruzada
        """
        # Verifica quais plataformas estão disponíveis nos dados
        available_platforms = [p for p in self.supported_platforms if p in data]
        
        if len(available_platforms) < 2:
            return {"error": "Pelo menos duas plataformas são necessárias para análise cruzada"}
        
        # Realiza análises cruzadas
        identity_match = self.analyze_identity_match(data, available_platforms)
        content_similarity = self.analyze_content_similarity(data, available_platforms)
        activity_patterns = self.analyze_activity_patterns(data, available_platforms)
        audience_overlap = self.estimate_audience_overlap(data, available_platforms)
        
        # Combina os resultados
        cross_analysis = {
            "identity_match": identity_match,
            "content_similarity": content_similarity,
            "activity_patterns": activity_patterns,
            "audience_overlap": audience_overlap,
            "summary": self.generate_analysis_summary(identity_match, content_similarity, activity_patterns, audience_overlap)
        }
        
        return cross_analysis
    
    def analyze_identity_match(self, data: Dict[str, Dict], platforms: List[str]) -> Dict[str, Any]:
        """
        Analisa a correspondência de identidade entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            platforms: Lista de plataformas disponíveis
            
        Returns:
            Dict: Resultados da análise de identidade
        """
        identity_scores = []
        username_matches = []
        name_matches = []
        bio_matches = []
        website_matches = []
        
        # Compara cada par de plataformas
        for i, p1 in enumerate(platforms):
            for j, p2 in enumerate(platforms):
                if i >= j:  # Evita comparações duplicadas e auto-comparações
                    continue
                
                p1_data = data[p1]
                p2_data = data[p2]
                
                # Compara usernames
                username1 = p1_data.get("username", "").lower()
                username2 = p2_data.get("username", "").lower()
                username_similarity = self._calculate_string_similarity(username1, username2)
                
                if username_similarity > 0.7:
                    username_matches.append({
                        "platform1": p1,
                        "platform2": p2,
                        "username1": username1,
                        "username2": username2,
                        "similarity": username_similarity
                    })
                
                # Compara nomes completos
                name1 = p1_data.get("full_name", "").lower()
                name2 = p2_data.get("full_name", "").lower()
                name_similarity = self._calculate_string_similarity(name1, name2)
                
                if name_similarity > 0.7:
                    name_matches.append({
                        "platform1": p1,
                        "platform2": p2,
                        "name1": name1,
                        "name2": name2,
                        "similarity": name_similarity
                    })
                
                # Compara biografias
                bio1 = p1_data.get("biography", "").lower()
                bio2 = p2_data.get("biography", "").lower()
                bio_similarity = self._calculate_text_similarity([bio1], [bio2])
                
                if bio_similarity > 0.3:  # Limiar menor para biografias
                    bio_matches.append({
                        "platform1": p1,
                        "platform2": p2,
                        "similarity": bio_similarity
                    })
                
                # Compara websites
                website1 = self._normalize_url(p1_data.get("external_url", ""))
                website2 = self._normalize_url(p2_data.get("external_url", ""))
                website_match = website1 == website2 and website1 != ""
                
                if website_match:
                    website_matches.append({
                        "platform1": p1,
                        "platform2": p2,
                        "website": website1
                    })
                
                # Calcula pontuação geral de identidade
                identity_score = (
                    username_similarity * 0.35 +
                    name_similarity * 0.35 +
                    bio_similarity * 0.2 +
                    (1.0 if website_match else 0.0) * 0.1
                )
                
                identity_scores.append({
                    "platform1": p1,
                    "platform2": p2,
                    "score": identity_score,
                    "confidence": self._calculate_confidence(identity_score)
                })
        
        # Organiza os resultados
        return {
            "platform_pairs": identity_scores,
            "username_matches": username_matches,
            "name_matches": name_matches,
            "bio_matches": bio_matches,
            "website_matches": website_matches,
            "overall_confidence": self._calculate_overall_confidence(identity_scores)
        }
    
    def analyze_content_similarity(self, data: Dict[str, Dict], platforms: List[str]) -> Dict[str, Any]:
        """
        Analisa a similaridade de conteúdo entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            platforms: Lista de plataformas disponíveis
            
        Returns:
            Dict: Resultados da análise de conteúdo
        """
        platform_content = {}
        hashtag_usage = {}
        
        # Extrai conteúdo de cada plataforma
        for platform in platforms:
            if platform not in data:
                continue
            platform_data = data[platform]
            texts = []
            hashtags = []
            
            if platform == "instagram" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    caption = post.get("caption", "")
                    texts.append(caption)
                    hashtags.extend(self._extract_hashtags(caption))
            
            elif platform == "twitter" and "recent_tweets" in platform_data:
                for tweet in platform_data["recent_tweets"]:
                    text = tweet.get("text", "")
                    texts.append(text)
                    hashtags.extend(self._extract_hashtags(text))
            
            elif platform == "facebook" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    message = post.get("message", "")
                    texts.append(message)
                    hashtags.extend(self._extract_hashtags(message))
            
            elif platform == "linkedin" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    text = post.get("text", "")
                    texts.append(text)
                    hashtags.extend(self._extract_hashtags(text))
            
            elif platform == "tiktok" and "recent_videos" in platform_data:
                for video in platform_data["recent_videos"]:
                    desc = video.get("desc", "")
                    texts.append(desc)
                    hashtags.extend(self._extract_hashtags(desc))
            
            platform_content[platform] = texts
            hashtag_usage[platform] = Counter(hashtags)
        
        # Calcula similaridade de conteúdo entre plataformas
        similarity_scores = []
        for i, p1 in enumerate(platforms):
            for j, p2 in enumerate(platforms):
                if i >= j:  # Evita comparações duplicadas e auto-comparações
                    continue
                
                if p1 not in platform_content or p2 not in platform_content or not platform_content[p1] or not platform_content[p2]:
                    continue
                
                similarity = self._calculate_text_similarity(platform_content[p1], platform_content[p2])
                
                similarity_scores.append({
                    "platform1": p1,
                    "platform2": p2,
                    "similarity_score": similarity,
                    "confidence": self._calculate_confidence(similarity)
                })
        
        # Encontra hashtags comuns entre plataformas
        common_hashtags = []
        for i, p1 in enumerate(platforms):
            for j, p2 in enumerate(platforms):
                if i >= j:  # Evita comparações duplicadas e auto-comparações
                    continue
                
                if p1 not in hashtag_usage or p2 not in hashtag_usage:
                    continue
                p1_tags = set(hashtag_usage[p1].keys())
                p2_tags = set(hashtag_usage[p2].keys())
                common = p1_tags.intersection(p2_tags)
                
                if common:
                    common_hashtags.append({
                        "platform1": p1,
                        "platform2": p2,
                        "common_hashtags": list(common)
                    })
        
        # Extrai tópicos comuns
        all_texts = []
        for texts in platform_content.values():
            all_texts.extend(texts)
        
        common_topics = self._extract_common_topics(all_texts)
        
        # Organiza os resultados
        return {
            "platform_pairs": similarity_scores,
            "common_hashtags": common_hashtags,
            "common_topics": common_topics,
            "overall_similarity": self._calculate_overall_confidence(similarity_scores)
        }
    
    def analyze_activity_patterns(self, data: Dict[str, Dict], platforms: List[str]) -> Dict[str, Any]:
        """
        Analisa padrões de atividade entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            platforms: Lista de plataformas disponíveis
            
        Returns:
            Dict: Resultados da análise de padrões de atividade
        """
        platform_activity = {}
        hourly_activity = {}
        weekly_activity = {}
        
        # Extrai timestamps de atividade de cada plataforma
        for platform in platforms:
            platform_data = data[platform]
            timestamps = []
            
            if platform == "instagram" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    if "taken_at" in post:
                        timestamps.append(post["taken_at"])
            
            elif platform == "twitter" and "recent_tweets" in platform_data:
                for tweet in platform_data["recent_tweets"]:
                    if "created_at" in tweet:
                        timestamps.append(tweet["created_at"])
            
            elif platform == "facebook" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    if "created_time" in post:
                        timestamps.append(post["created_time"])
            
            elif platform == "linkedin" and "recent_posts" in platform_data:
                for post in platform_data["recent_posts"]:
                    if "created_time" in post:
                        timestamps.append(post["created_time"])
            
            elif platform == "tiktok" and "recent_videos" in platform_data:
                for video in platform_data["recent_videos"]:
                    if "create_time" in video:
                        timestamps.append(video["create_time"])
            
            platform_activity[platform] = timestamps
            
            # Calcula atividade por hora do dia
            hours = [0] * 24
            for ts in timestamps:
                hours[ts.hour] += 1
            hourly_activity[platform] = hours
            
            # Calcula atividade por dia da semana (0 = segunda, 6 = domingo)
            days = [0] * 7
            for ts in timestamps:
                days[ts.weekday()] += 1
            weekly_activity[platform] = days
        
        # Calcula correlação de padrões de atividade entre plataformas
        activity_correlations = []
        for i, p1 in enumerate(platforms):
            for j, p2 in enumerate(platforms):
                if i >= j:  # Evita comparações duplicadas e auto-comparações
                    continue
                
                # Correlação de atividade por hora
                hourly_corr = self._calculate_correlation(hourly_activity[p1], hourly_activity[p2])
                
                # Correlação de atividade por dia da semana
                weekly_corr = self._calculate_correlation(weekly_activity[p1], weekly_activity[p2])
                
                # Média ponderada das correlações
                overall_corr = hourly_corr * 0.6 + weekly_corr * 0.4
                
                activity_correlations.append({
                    "platform1": p1,
                    "platform2": p2,
                    "hourly_correlation": hourly_corr,
                    "weekly_correlation": weekly_corr,
                    "overall_correlation": overall_corr,
                    "confidence": self._calculate_confidence(overall_corr)
                })
        
        # Organiza os resultados
        return {
            "platform_correlations": activity_correlations,
            "hourly_patterns": hourly_activity,
            "weekly_patterns": weekly_activity,
            "overall_correlation": self._calculate_overall_confidence(activity_correlations, key="overall_correlation")
        }
    
    def estimate_audience_overlap(self, data: Dict[str, Dict], platforms: List[str]) -> Dict[str, Any]:
        """
        Estima a sobreposição de audiência entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            platforms: Lista de plataformas disponíveis
            
        Returns:
            Dict: Resultados da estimativa de sobreposição de audiência
        """
        # Extrai métricas de audiência
        audience_metrics = {}
        for platform in platforms:
            platform_data = data[platform]
            
            followers = platform_data.get("follower_count", 0)
            following = platform_data.get("following_count", 0)
            
            engagement = 0
            if platform == "instagram" and "recent_posts" in platform_data:
                likes = sum([post.get("like_count", 0) for post in platform_data["recent_posts"]])
                comments = sum([post.get("comment_count", 0) for post in platform_data["recent_posts"]])
                post_count = len(platform_data["recent_posts"])
                engagement = (likes + comments) / post_count if post_count > 0 else 0
            
            elif platform == "twitter" and "recent_tweets" in platform_data:
                likes = sum([tweet.get("favorite_count", 0) for tweet in platform_data["recent_tweets"]])
                retweets = sum([tweet.get("retweet_count", 0) for tweet in platform_data["recent_tweets"]])
                tweet_count = len(platform_data["recent_tweets"])
                engagement = (likes + retweets) / tweet_count if tweet_count > 0 else 0
            
            elif platform == "facebook" and "recent_posts" in platform_data:
                likes = sum([post.get("likes", {}).get("summary", {}).get("total_count", 0) for post in platform_data["recent_posts"]])
                comments = sum([post.get("comments", {}).get("summary", {}).get("total_count", 0) for post in platform_data["recent_posts"]])
                post_count = len(platform_data["recent_posts"])
                engagement = (likes + comments) / post_count if post_count > 0 else 0
            
            elif platform == "linkedin" and "recent_posts" in platform_data:
                likes = sum([post.get("likes_count", 0) for post in platform_data["recent_posts"]])
                comments = sum([post.get("comments_count", 0) for post in platform_data["recent_posts"]])
                post_count = len(platform_data["recent_posts"])
                engagement = (likes + comments) / post_count if post_count > 0 else 0
            
            elif platform == "tiktok" and "recent_videos" in platform_data:
                likes = sum([video.get("like_count", 0) for video in platform_data["recent_videos"]])
                comments = sum([video.get("comment_count", 0) for video in platform_data["recent_videos"]])
                shares = sum([video.get("share_count", 0) for video in platform_data["recent_videos"]])
                video_count = len(platform_data["recent_videos"])
                engagement = (likes + comments + shares) / video_count if video_count > 0 else 0
            
            audience_metrics[platform] = {
                "followers": followers,
                "following": following,
                "engagement": engagement
            }
        
        # Estima sobreposição de audiência com base em similaridade de conteúdo e identidade
        audience_connections = []
        for i, p1 in enumerate(platforms):
            for j, p2 in enumerate(platforms):
                if i >= j:  # Evita comparações duplicadas e auto-comparações
                    continue
                
                # Fatores para estimativa de sobreposição
                identity_factor = self._get_identity_match_score(data, p1, p2)
                content_factor = self._get_content_similarity_score(data, p1, p2)
                
                # Estima porcentagem de sobreposição
                # Fórmula: média ponderada dos fatores * min(followers1, followers2) / max(followers1, followers2)
                followers1 = audience_metrics[p1]["followers"]
                followers2 = audience_metrics[p2]["followers"]
                
                if followers1 == 0 or followers2 == 0:
                    overlap_percentage = 0
                else:
                    follower_ratio = min(followers1, followers2) / max(followers1, followers2)
                    overlap_factor = (identity_factor * 0.6 + content_factor * 0.4) * follower_ratio
                    overlap_percentage = min(overlap_factor, 1.0)  # Limita a 100%
                
                audience_connections.append({
                    "source": p1,
                    "target": p2,
                    "overlap_percentage": overlap_percentage,
                    "estimated_overlap_count": int(overlap_percentage * min(followers1, followers2)),
                    "confidence": self._calculate_confidence(overlap_percentage)
                })
        
        # Organiza os resultados
        return {
            "metrics": audience_metrics,
            "connections": audience_connections,
            "overall_overlap": self._calculate_overall_confidence(audience_connections, key="overlap_percentage")
        }
    
    def generate_analysis_summary(self, identity_match: Dict, content_similarity: Dict, 
                               activity_patterns: Dict, audience_overlap: Dict) -> Dict[str, Any]:
        """
        Gera um resumo da análise cruzada.
        
        Args:
            identity_match: Resultados da análise de identidade
            content_similarity: Resultados da análise de conteúdo
            activity_patterns: Resultados da análise de padrões de atividade
            audience_overlap: Resultados da estimativa de sobreposição de audiência
            
        Returns:
            Dict: Resumo da análise
        """
        # Calcula pontuação geral de correspondência entre plataformas
        overall_score = (
            identity_match.get("overall_confidence", 0) * 0.35 +
            content_similarity.get("overall_similarity", 0) * 0.25 +
            activity_patterns.get("overall_correlation", 0) * 0.2 +
            audience_overlap.get("overall_overlap", 0) * 0.2
        )
        
        # Determina o nível de confiança
        confidence_level = self._calculate_confidence_level(overall_score)
        
        # Gera insights principais
        key_insights = []
        
        # Insights de identidade
        if identity_match.get("overall_confidence", 0) > 0.8:
            key_insights.append("Alta correspondência de identidade entre plataformas")
        elif identity_match.get("overall_confidence", 0) > 0.5:
            key_insights.append("Correspondência moderada de identidade entre plataformas")
        
        # Insights de conteúdo
        if content_similarity.get("overall_similarity", 0) > 0.7:
            key_insights.append("Conteúdo muito similar entre plataformas")
        elif content_similarity.get("overall_similarity", 0) < 0.3:
            key_insights.append("Conteúdo significativamente diferente entre plataformas")
        
        # Insights de padrões de atividade
        if activity_patterns.get("overall_correlation", 0) > 0.7:
            key_insights.append("Padrões de atividade altamente correlacionados entre plataformas")
        
        # Insights de audiência
        if audience_overlap.get("overall_overlap", 0) > 0.5:
            key_insights.append("Alta sobreposição estimada de audiência entre plataformas")
        
        # Organiza o resumo
        return {
            "overall_score": overall_score,
            "confidence_level": confidence_level,
            "key_insights": key_insights,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    # Métodos auxiliares
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calcula a similaridade entre duas strings"""
        if not str1 and not str2:
            return 1.0
        if not str1 or not str2:
            return 0.0
        
        # Implementação simples da distância de Levenshtein
        len1, len2 = len(str1), len(str2)
        matrix = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # Deleção
                    matrix[i][j-1] + 1,      # Inserção
                    matrix[i-1][j-1] + cost  # Substituição
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        
        # Normaliza para obter similaridade entre 0 e 1
        return 1.0 - (distance / max_len) if max_len > 0 else 1.0
    
    def _calculate_text_similarity(self, texts1: List[str], texts2: List[str]) -> float:
        """Calcula a similaridade entre dois conjuntos de textos"""
        if not texts1 or not texts2:
            return 0.0
        
        # Combina todos os textos
        all_texts = texts1 + texts2
        
        # Pré-processa os textos
        processed_texts = [self._preprocess_text(text) for text in all_texts]
        
        # Cria vetores TF-IDF
        vectorizer = TfidfVectorizer(min_df=1, stop_words=list(self.stop_words))
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
        except ValueError:  # Se todos os textos estiverem vazios após pré-processamento
            return 0.0
        
        # Calcula a similaridade média entre todos os pares de textos entre os dois conjuntos
        n1, n2 = len(texts1), len(texts2)
        total_similarity = 0.0
        count = 0
        
        for i in range(n1):
            for j in range(n2):
                idx1, idx2 = i, n1 + j
                sim = cosine_similarity(tfidf_matrix[idx1:idx1+1], tfidf_matrix[idx2:idx2+1])[0][0]
                total_similarity += sim
                count += 1
        
        return total_similarity / count if count > 0 else 0.0
    
    def _preprocess_text(self, text: str) -> str:
        """Pré-processa texto para análise"""
        if not text:
            return ""
        
        # Converte para minúsculas
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove menções (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags (#hashtag)
        text = re.sub(r'#\w+', '', text)
        
        # Tokeniza
        tokens = word_tokenize(text)
        
        # Remove stopwords e pontuação
        tokens = [token for token in tokens if token.isalnum() and token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extrai hashtags de um texto"""
        if not text:
            return []
        
        # Encontra todas as hashtags no texto
        hashtags = re.findall(r'#(\w+)', text.lower())
        
        return hashtags
    
    def _normalize_url(self, url: str) -> str:
        """Normaliza uma URL para comparação"""
        if not url:
            return ""
        
        # Remove protocolo (http://, https://)
        url = re.sub(r'^https?://', '', url.lower())
        
        # Remove www.
        url = re.sub(r'^www\.', '', url)
        
        # Remove barra final
        url = url.rstrip('/')
        
        return url
    
    def _calculate_correlation(self, list1: List[float], list2: List[float]) -> float:
        """Calcula a correlação entre duas listas de números"""
        if len(list1) != len(list2) or len(list1) == 0:
            return 0.0
        
        # Converte para arrays numpy
        arr1 = np.array(list1)
        arr2 = np.array(list2)
        
        # Calcula médias
        mean1 = np.mean(arr1)
        mean2 = np.mean(arr2)
        
        # Calcula desvios
        dev1 = arr1 - mean1
        dev2 = arr2 - mean2
        
        # Calcula correlação
        numerator = np.sum(dev1 * dev2)
        denominator = np.sqrt(np.sum(dev1**2) * np.sum(dev2**2))
        
        if denominator == 0:
            return 0.0
        
        correlation = numerator / denominator
        
        # Normaliza para [0, 1] para consistência com outras métricas
        return (correlation + 1) / 2
    
    def _extract_common_topics(self, texts: List[str], top_n: int = 10) -> List[str]:
        """Extrai tópicos comuns de um conjunto de textos"""
        if not texts:
            return []
        
        # Pré-processa os textos
        processed_texts = [self._preprocess_text(text) for text in texts]
        
        # Extrai todas as palavras
        all_words = []
        for text in processed_texts:
            all_words.extend(text.split())
        
        # Conta frequência das palavras
        word_counts = Counter(all_words)
        
        # Retorna as palavras mais comuns
        return [word for word, _ in word_counts.most_common(top_n)]
    
    def _calculate_confidence(self, score: float) -> str:
        """Calcula o nível de confiança com base em uma pontuação"""
        if score < 0.3:
            return "baixo"
        elif score < 0.6:
            return "médio"
        elif score < 0.8:
            return "alto"
        else:
            return "muito alto"
    
    def _calculate_confidence_level(self, score: float) -> str:
        """Versão mais detalhada do cálculo de confiança"""
        if score < 0.2:
            return "muito baixo"
        elif score < 0.4:
            return "baixo"
        elif score < 0.6:
            return "médio"
        elif score < 0.8:
            return "alto"
        else:
            return "muito alto"
    
    def _calculate_overall_confidence(self, items: List[Dict], key: str = "score") -> float:
        """Calcula a confiança geral com base em uma lista de itens"""
        if not items:
            return 0.0
        
        total_score = sum(item.get(key, 0) for item in items)
        return total_score / len(items)
    
    def _get_identity_match_score(self, data: Dict[str, Dict], p1: str, p2: str) -> float:
        """Obtém a pontuação de correspondência de identidade entre duas plataformas"""
        if "cross_analysis" not in data or "identity_match" not in data["cross_analysis"]:
            return 0.5  # Valor padrão se não houver análise disponível
        
        identity_match = data["cross_analysis"]["identity_match"]
        
        for pair in identity_match.get("platform_pairs", []):
            if (pair.get("platform1") == p1 and pair.get("platform2") == p2) or \
               (pair.get("platform1") == p2 and pair.get("platform2") == p1):
                return pair.get("score", 0.5)
        
        return 0.5  # Valor padrão se não encontrar o par específico
    
    def _get_content_similarity_score(self, data: Dict[str, Dict], p1: str, p2: str) -> float:
        """Obtém a pontuação de similaridade de conteúdo entre duas plataformas"""
        if "cross_analysis" not in data or "content_similarity" not in data["cross_analysis"]:
            return 0.5  # Valor padrão se não houver análise disponível
        
        content_similarity = data["cross_analysis"]["content_similarity"]
        
        for pair in content_similarity.get("platform_pairs", []):
            if (pair.get("platform1") == p1 and pair.get("platform2") == p2) or \
               (pair.get("platform1") == p2 and pair.get("platform2") == p1):
                return pair.get("similarity_score", 0.5)
        
        return 0.5  # Valor padrão se não encontrar o par específico