import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import io
import base64
from typing import Dict, List, Any, Optional

class CrossPlatformVisualization:
    """
    Classe para criar visualizações avançadas para análise cruzada entre plataformas.
    Fornece gráficos comparativos, mapas de calor e redes de conexões.
    """
    
    def __init__(self):
        """
        Inicializa a classe de visualização cruzada.
        """
        self.platform_colors = {
            "instagram": "#E1306C",
            "facebook": "#1877F2",
            "twitter": "#1DA1F2",
            "linkedin": "#0A66C2",
            "tiktok": "#000000"
        }
    
    def create_engagement_comparison_chart(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de barras comparando métricas de engajamento entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        platforms = []
        followers = []
        engagement = []
        colors = []
        
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                platforms.append(platform.capitalize())
                followers.append(platform_data.get("follower_count", 0))
                
                # Calcula taxa de engajamento com base nos dados disponíveis
                if platform == "instagram":
                    likes = sum([post.get("like_count", 0) for post in platform_data.get("recent_posts", [])])
                    comments = sum([post.get("comment_count", 0) for post in platform_data.get("recent_posts", [])])
                    post_count = len(platform_data.get("recent_posts", []))
                    eng_rate = (likes + comments) / (platform_data.get("follower_count", 1) * post_count) if post_count > 0 else 0
                    engagement.append(eng_rate * 100)  # Converte para porcentagem
                
                elif platform == "twitter":
                    likes = sum([tweet.get("favorite_count", 0) for tweet in platform_data.get("recent_tweets", [])])
                    retweets = sum([tweet.get("retweet_count", 0) for tweet in platform_data.get("recent_tweets", [])])
                    tweet_count = len(platform_data.get("recent_tweets", []))
                    eng_rate = (likes + retweets) / (platform_data.get("follower_count", 1) * tweet_count) if tweet_count > 0 else 0
                    engagement.append(eng_rate * 100)
                
                elif platform == "facebook":
                    likes = sum([post.get("likes", {}).get("summary", {}).get("total_count", 0) for post in platform_data.get("recent_posts", [])])
                    comments = sum([post.get("comments", {}).get("summary", {}).get("total_count", 0) for post in platform_data.get("recent_posts", [])])
                    post_count = len(platform_data.get("recent_posts", []))
                    eng_rate = (likes + comments) / (platform_data.get("follower_count", 1) * post_count) if post_count > 0 else 0
                    engagement.append(eng_rate * 100)
                
                elif platform == "linkedin":
                    likes = sum([post.get("likes_count", 0) for post in platform_data.get("recent_posts", [])])
                    comments = sum([post.get("comments_count", 0) for post in platform_data.get("recent_posts", [])])
                    post_count = len(platform_data.get("recent_posts", []))
                    eng_rate = (likes + comments) / (platform_data.get("follower_count", 1) * post_count) if post_count > 0 else 0
                    engagement.append(eng_rate * 100)
                
                elif platform == "tiktok":
                    likes = sum([video.get("like_count", 0) for video in platform_data.get("recent_videos", [])])
                    comments = sum([video.get("comment_count", 0) for video in platform_data.get("recent_videos", [])])
                    shares = sum([video.get("share_count", 0) for video in platform_data.get("recent_videos", [])])
                    video_count = len(platform_data.get("recent_videos", []))
                    eng_rate = (likes + comments + shares) / (platform_data.get("follower_count", 1) * video_count) if video_count > 0 else 0
                    engagement.append(eng_rate * 100)
                
                else:
                    engagement.append(0)
                
                colors.append(self.platform_colors.get(platform.lower(), "#808080"))
        
        # Cria o gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(platforms))
        width = 0.35
        
        # Normaliza os seguidores para melhor visualização
        max_followers = max(followers) if followers and max(followers) > 0 else 1
        normalized_followers = [f / max_followers * 100 for f in followers]
        
        # Cria as barras
        bar1 = ax.bar([i - width/2 for i in x], normalized_followers, width, label="Seguidores (normalizado)", color=[c + "80" for c in colors])
        bar2 = ax.bar([i + width/2 for i in x], engagement, width, label="Taxa de Engajamento (%)", color=colors)
        
        # Adiciona rótulos e título
        ax.set_xlabel("Plataforma")
        ax.set_ylabel("Porcentagem")
        ax.set_title("Comparação de Seguidores e Engajamento entre Plataformas")
        ax.set_xticks(x)
        ax.set_xticklabels(platforms)
        ax.legend()
        
        # Adiciona valores nas barras
        for i, v in enumerate(normalized_followers):
            ax.text(i - width/2, v + 1, f"{followers[i]:,}", ha="center", va="bottom", fontsize=8)
        
        for i, v in enumerate(engagement):
            ax.text(i + width/2, v + 1, f"{v:.2f}%", ha="center", va="bottom", fontsize=8)
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_temporal_trends_chart(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de tendências temporais de engajamento entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Coleta dados temporais de cada plataforma
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                dates = []
                engagement_values = []
                
                # Extrai dados temporais baseado na plataforma
                if platform == "instagram" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "taken_at" in post:
                            dates.append(post["taken_at"])
                            likes = post.get("like_count", 0)
                            comments = post.get("comment_count", 0)
                            engagement_values.append(likes + comments)
                
                elif platform == "twitter" and "recent_tweets" in platform_data:
                    for tweet in platform_data["recent_tweets"]:
                        if "created_at" in tweet:
                            dates.append(tweet["created_at"])
                            likes = tweet.get("favorite_count", 0)
                            retweets = tweet.get("retweet_count", 0)
                            engagement_values.append(likes + retweets)
                
                elif platform == "facebook" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "created_time" in post:
                            dates.append(post["created_time"])
                            likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                            comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                            engagement_values.append(likes + comments)
                
                elif platform == "linkedin" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "created_time" in post:
                            dates.append(post["created_time"])
                            likes = post.get("likes_count", 0)
                            comments = post.get("comments_count", 0)
                            engagement_values.append(likes + comments)
                
                elif platform == "tiktok" and "recent_videos" in platform_data:
                    for video in platform_data["recent_videos"]:
                        if "create_time" in video:
                            dates.append(video["create_time"])
                            likes = video.get("like_count", 0)
                            comments = video.get("comment_count", 0)
                            shares = video.get("share_count", 0)
                            engagement_values.append(likes + comments + shares)
                
                # Plota a linha de tendência se houver dados
                if dates and engagement_values:
                    # Ordena por data
                    sorted_data = sorted(zip(dates, engagement_values))
                    dates, engagement_values = zip(*sorted_data)
                    
                    ax.plot(dates, engagement_values, 
                           color=self.platform_colors.get(platform.lower(), "#808080"),
                           marker='o', linewidth=2, markersize=4,
                           label=f"{platform.capitalize()}")
        
        # Configura o gráfico
        ax.set_xlabel("Data")
        ax.set_ylabel("Engajamento Total")
        ax.set_title("Tendências Temporais de Engajamento por Plataforma")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotaciona rótulos do eixo x para melhor legibilidade
        plt.xticks(rotation=45)
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_content_type_distribution(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de pizza mostrando a distribuição de tipos de conteúdo.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        content_types = {}
        
        # Analisa tipos de conteúdo por plataforma
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                
                if platform == "instagram" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        media_type = post.get("media_type", "unknown")
                        if media_type == 1:
                            content_type = "Foto"
                        elif media_type == 2:
                            content_type = "Vídeo"
                        elif media_type == 8:
                            content_type = "Carrossel"
                        else:
                            content_type = "Outro"
                        
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                
                elif platform == "twitter" and "recent_tweets" in platform_data:
                    for tweet in platform_data["recent_tweets"]:
                        if "media" in tweet and tweet["media"]:
                            media = tweet["media"][0]
                            if media.get("type") == "photo":
                                content_type = "Foto"
                            elif media.get("type") == "video":
                                content_type = "Vídeo"
                            else:
                                content_type = "Mídia"
                        else:
                            content_type = "Texto"
                        
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                
                elif platform == "facebook" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "attachments" in post and post["attachments"]:
                            attachment = post["attachments"][0]
                            if attachment.get("type") == "photo":
                                content_type = "Foto"
                            elif attachment.get("type") == "video":
                                content_type = "Vídeo"
                            else:
                                content_type = "Link/Outro"
                        else:
                            content_type = "Texto"
                        
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                
                elif platform == "linkedin" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "media" in post and post["media"]:
                            content_type = "Mídia"
                        elif "article" in post:
                            content_type = "Artigo"
                        else:
                            content_type = "Texto"
                        
                        content_types[content_type] = content_types.get(content_type, 0) + 1
                
                elif platform == "tiktok" and "recent_videos" in platform_data:
                    # TikTok é principalmente vídeos
                    video_count = len(platform_data["recent_videos"])
                    content_types["Vídeo Curto"] = content_types.get("Vídeo Curto", 0) + video_count
        
        # Se não houver dados, retorna None
        if not content_types:
            return None
        
        # Cria o gráfico de pizza
        fig, ax = plt.subplots(figsize=(10, 8))
        
        labels = list(content_types.keys())
        sizes = list(content_types.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        # Cria o gráfico de pizza
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 10})
        
        # Configura o gráfico
        ax.set_title("Distribuição de Tipos de Conteúdo", fontsize=14, fontweight='bold')
        
        # Adiciona legenda
        ax.legend(wedges, [f"{label}: {size} posts" for label, size in zip(labels, sizes)],
                 title="Tipos de Conteúdo", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_growth_metrics_chart(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de métricas de crescimento comparativo entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        platforms = []
        follower_counts = []
        post_counts = []
        avg_engagement = []
        colors = []
        
        # Coleta métricas de cada plataforma
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                platforms.append(platform.capitalize())
                follower_counts.append(platform_data.get("follower_count", 0))
                colors.append(self.platform_colors.get(platform.lower(), "#808080"))
                
                # Conta posts e calcula engajamento médio
                total_posts = 0
                total_engagement = 0
                
                if platform == "instagram" and "recent_posts" in platform_data:
                    posts = platform_data["recent_posts"]
                    total_posts = len(posts)
                    for post in posts:
                        likes = post.get("like_count", 0)
                        comments = post.get("comment_count", 0)
                        total_engagement += likes + comments
                
                elif platform == "twitter" and "recent_tweets" in platform_data:
                    tweets = platform_data["recent_tweets"]
                    total_posts = len(tweets)
                    for tweet in tweets:
                        likes = tweet.get("favorite_count", 0)
                        retweets = tweet.get("retweet_count", 0)
                        total_engagement += likes + retweets
                
                elif platform == "facebook" and "recent_posts" in platform_data:
                    posts = platform_data["recent_posts"]
                    total_posts = len(posts)
                    for post in posts:
                        likes = post.get("likes", {}).get("summary", {}).get("total_count", 0)
                        comments = post.get("comments", {}).get("summary", {}).get("total_count", 0)
                        total_engagement += likes + comments
                
                elif platform == "linkedin" and "recent_posts" in platform_data:
                    posts = platform_data["recent_posts"]
                    total_posts = len(posts)
                    for post in posts:
                        likes = post.get("likes_count", 0)
                        comments = post.get("comments_count", 0)
                        total_engagement += likes + comments
                
                elif platform == "tiktok" and "recent_videos" in platform_data:
                    videos = platform_data["recent_videos"]
                    total_posts = len(videos)
                    for video in videos:
                        likes = video.get("like_count", 0)
                        comments = video.get("comment_count", 0)
                        shares = video.get("share_count", 0)
                        total_engagement += likes + comments + shares
                
                post_counts.append(total_posts)
                avg_engagement.append(total_engagement / total_posts if total_posts > 0 else 0)
        
        # Cria subplots para múltiplas métricas
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Gráfico 1: Seguidores
        bars1 = ax1.bar(platforms, follower_counts, color=colors, alpha=0.8)
        ax1.set_title("Número de Seguidores por Plataforma")
        ax1.set_ylabel("Seguidores")
        for i, v in enumerate(follower_counts):
            ax1.text(i, v + max(follower_counts) * 0.01, f"{v:,}", ha="center", va="bottom")
        
        # Gráfico 2: Posts Recentes
        bars2 = ax2.bar(platforms, post_counts, color=colors, alpha=0.8)
        ax2.set_title("Número de Posts Recentes")
        ax2.set_ylabel("Posts")
        for i, v in enumerate(post_counts):
            ax2.text(i, v + max(post_counts) * 0.01, str(v), ha="center", va="bottom")
        
        # Gráfico 3: Engajamento Médio
        bars3 = ax3.bar(platforms, avg_engagement, color=colors, alpha=0.8)
        ax3.set_title("Engajamento Médio por Post")
        ax3.set_ylabel("Engajamento")
        for i, v in enumerate(avg_engagement):
            ax3.text(i, v + max(avg_engagement) * 0.01, f"{v:.0f}", ha="center", va="bottom")
        
        # Gráfico 4: Taxa de Engajamento
        engagement_rates = []
        for i, platform in enumerate(platforms):
            rate = (avg_engagement[i] / follower_counts[i] * 100) if follower_counts[i] > 0 else 0
            engagement_rates.append(rate)
        
        bars4 = ax4.bar(platforms, engagement_rates, color=colors, alpha=0.8)
        ax4.set_title("Taxa de Engajamento (%)")
        ax4.set_ylabel("Taxa (%)")
        for i, v in enumerate(engagement_rates):
            ax4.text(i, v + max(engagement_rates) * 0.01, f"{v:.2f}%", ha="center", va="bottom")
        
        # Ajusta layout
        plt.tight_layout()
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_sentiment_analysis_chart(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de análise de sentimentos dos comentários por plataforma.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        platforms = []
        positive_counts = []
        neutral_counts = []
        negative_counts = []
        colors = []
        
        # Analisa sentimentos por plataforma (simulado para demonstração)
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                platforms.append(platform.capitalize())
                colors.append(self.platform_colors.get(platform.lower(), "#808080"))
                
                # Simula análise de sentimentos baseada em métricas de engajamento
                total_comments = 0
                total_likes = 0
                
                if platform == "instagram" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        total_comments += post.get("comment_count", 0)
                        total_likes += post.get("like_count", 0)
                
                elif platform == "twitter" and "recent_tweets" in platform_data:
                    for tweet in platform_data["recent_tweets"]:
                        total_comments += tweet.get("reply_count", 0)
                        total_likes += tweet.get("favorite_count", 0)
                
                elif platform == "facebook" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        total_comments += post.get("comments", {}).get("summary", {}).get("total_count", 0)
                        total_likes += post.get("likes", {}).get("summary", {}).get("total_count", 0)
                
                elif platform == "linkedin" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        total_comments += post.get("comments_count", 0)
                        total_likes += post.get("likes_count", 0)
                
                elif platform == "tiktok" and "recent_videos" in platform_data:
                    for video in platform_data["recent_videos"]:
                        total_comments += video.get("comment_count", 0)
                        total_likes += video.get("like_count", 0)
                
                # Simula distribuição de sentimentos baseada na proporção likes/comentários
                total_interactions = total_likes + total_comments
                if total_interactions > 0:
                    like_ratio = total_likes / total_interactions
                    # Assume que mais likes = mais sentimento positivo
                    positive = int(total_interactions * like_ratio * 0.8)
                    negative = int(total_interactions * (1 - like_ratio) * 0.3)
                    neutral = total_interactions - positive - negative
                else:
                    positive = neutral = negative = 0
                
                positive_counts.append(positive)
                neutral_counts.append(neutral)
                negative_counts.append(negative)
        
        # Se não houver dados, retorna None
        if not any(positive_counts + neutral_counts + negative_counts):
            return None
        
        # Cria o gráfico de barras empilhadas
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = range(len(platforms))
        width = 0.6
        
        # Cria barras empilhadas
        p1 = ax.bar(x, positive_counts, width, label='Positivo', color='#2ECC71', alpha=0.8)
        p2 = ax.bar(x, neutral_counts, width, bottom=positive_counts, label='Neutro', color='#F39C12', alpha=0.8)
        p3 = ax.bar(x, negative_counts, width, 
                   bottom=[p + n for p, n in zip(positive_counts, neutral_counts)], 
                   label='Negativo', color='#E74C3C', alpha=0.8)
        
        # Configura o gráfico
        ax.set_xlabel('Plataforma')
        ax.set_ylabel('Número de Interações')
        ax.set_title('Análise de Sentimentos por Plataforma')
        ax.set_xticks(x)
        ax.set_xticklabels(platforms)
        ax.legend()
        
        # Adiciona valores nas barras
        for i in range(len(platforms)):
            total = positive_counts[i] + neutral_counts[i] + negative_counts[i]
            if total > 0:
                # Porcentagens
                pos_pct = (positive_counts[i] / total) * 100
                neu_pct = (neutral_counts[i] / total) * 100
                neg_pct = (negative_counts[i] / total) * 100
                
                # Adiciona texto no centro de cada seção
                if positive_counts[i] > 0:
                    ax.text(i, positive_counts[i]/2, f'{pos_pct:.1f}%', 
                           ha='center', va='center', fontweight='bold')
                
                if neutral_counts[i] > 0:
                    ax.text(i, positive_counts[i] + neutral_counts[i]/2, f'{neu_pct:.1f}%', 
                           ha='center', va='center', fontweight='bold')
                
                if negative_counts[i] > 0:
                    ax.text(i, positive_counts[i] + neutral_counts[i] + negative_counts[i]/2, f'{neg_pct:.1f}%', 
                           ha='center', va='center', fontweight='bold')
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def generate_comprehensive_report(self, data: Dict[str, Dict]) -> Dict[str, str]:
        """
        Gera um relatório completo com todas as visualizações disponíveis.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            Dict[str, str]: Dicionário com todas as visualizações em base64
        """
        report = {}
        
        try:
            # Gráfico de comparação de engajamento (existente)
            report['engagement_comparison'] = self.create_engagement_comparison_chart(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de comparação de engajamento: {e}")
            report['engagement_comparison'] = None
        
        try:
            # Gráfico de tendências temporais
            report['temporal_trends'] = self.create_temporal_trends_chart(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de tendências temporais: {e}")
            report['temporal_trends'] = None
        
        try:
            # Gráfico de distribuição de tipos de conteúdo
            report['content_distribution'] = self.create_content_type_distribution(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de distribuição de conteúdo: {e}")
            report['content_distribution'] = None
        
        try:
            # Gráfico de métricas de crescimento
            report['growth_metrics'] = self.create_growth_metrics_chart(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de métricas de crescimento: {e}")
            report['growth_metrics'] = None
        
        try:
            # Gráfico de análise de sentimentos
            report['sentiment_analysis'] = self.create_sentiment_analysis_chart(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de análise de sentimentos: {e}")
            report['sentiment_analysis'] = None
        
        try:
            # Mapa de calor de atividade (existente)
            report['activity_heatmap'] = self.create_activity_heatmap(data)
        except Exception as e:
            print(f"Erro ao gerar mapa de calor de atividade: {e}")
            report['activity_heatmap'] = None
        
        try:
            # Rede de conexões (existente)
            report['connection_network'] = self.create_connection_network(data)
        except Exception as e:
            print(f"Erro ao gerar rede de conexões: {e}")
            report['connection_network'] = None
        
        try:
            # Similaridade de conteúdo (existente)
            report['content_similarity'] = self.create_content_similarity_chart(data)
        except Exception as e:
            print(f"Erro ao gerar gráfico de similaridade de conteúdo: {e}")
            report['content_similarity'] = None
        
        return report
    
    def create_activity_heatmap(self, data: Dict[str, Dict]) -> str:
        """
        Cria um mapa de calor para padrões de atividade entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma
            
        Returns:
            str: Imagem codificada em base64
        """
        # Prepara os dados para o mapa de calor
        platforms = []
        activity_data = {}
        
        # Horas do dia (0-23)
        hours = list(range(24))
        
        for platform, platform_data in data.items():
            if platform not in ["cross_platform", "cross_analysis"]:
                platforms.append(platform.capitalize())
                
                # Inicializa contagem de atividade por hora
                hourly_activity = [0] * 24
                
                # Conta atividade por hora com base nos dados disponíveis
                if platform == "instagram" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "taken_at" in post:
                            hour = post["taken_at"].hour
                            hourly_activity[hour] += 1
                
                elif platform == "twitter" and "recent_tweets" in platform_data:
                    for tweet in platform_data["recent_tweets"]:
                        if "created_at" in tweet:
                            hour = tweet["created_at"].hour
                            hourly_activity[hour] += 1
                
                elif platform == "facebook" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "created_time" in post:
                            hour = post["created_time"].hour
                            hourly_activity[hour] += 1
                
                elif platform == "linkedin" and "recent_posts" in platform_data:
                    for post in platform_data["recent_posts"]:
                        if "created_time" in post:
                            hour = post["created_time"].hour
                            hourly_activity[hour] += 1
                
                elif platform == "tiktok" and "recent_videos" in platform_data:
                    for video in platform_data["recent_videos"]:
                        if "create_time" in video:
                            hour = video["create_time"].hour
                            hourly_activity[hour] += 1
                
                activity_data[platform.lower()] = hourly_activity
        
        # Se não houver dados suficientes, retorna None
        if not activity_data:
            return None
        
        # Cria DataFrame para o mapa de calor
        df = pd.DataFrame(activity_data, index=hours)
        
        # Cria o mapa de calor
        fig, ax = plt.subplots(figsize=(12, 8))
        im = ax.imshow(df.T, cmap="YlOrRd")
        
        # Adiciona rótulos e título
        ax.set_xticks(range(len(hours)))
        ax.set_xticklabels([f"{h}:00" for h in hours])
        ax.set_yticks(range(len(platforms)))
        ax.set_yticklabels(platforms)
        ax.set_xlabel("Hora do Dia")
        ax.set_title("Padrões de Atividade por Hora do Dia")
        
        # Adiciona barra de cores
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Número de Publicações", rotation=-90, va="bottom")
        
        # Adiciona valores nas células
        for i in range(len(platforms)):
            for j in range(len(hours)):
                platform = platforms[i].lower()
                if platform in activity_data and activity_data[platform][j] > 0:
                    ax.text(j, i, activity_data[platform][j], ha="center", va="center", color="black")
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_connection_network(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de rede mostrando conexões entre seguidores em diferentes plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma e análise cruzada
            
        Returns:
            str: Imagem codificada em base64
        """
        # Verifica se há dados de análise cruzada
        if "cross_analysis" not in data or "audience_overlap" not in data["cross_analysis"]:
            return None
        
        # Cria o grafo
        G = nx.Graph()
        
        # Adiciona nós para cada plataforma
        platforms = [p for p in data.keys() if p not in ["cross_platform", "cross_analysis"]]
        for platform in platforms:
            G.add_node(platform.capitalize(), size=data[platform].get("follower_count", 100), 
                      color=self.platform_colors.get(platform.lower(), "#808080"))
        
        # Adiciona arestas para sobreposição de audiência
        audience_overlap = data["cross_analysis"]["audience_overlap"]
        for connection in audience_overlap.get("connections", []):
            source = connection.get("source", "").capitalize()
            target = connection.get("target", "").capitalize()
            weight = connection.get("overlap_percentage", 0)
            
            if source in [p.capitalize() for p in platforms] and target in [p.capitalize() for p in platforms]:
                G.add_edge(source, target, weight=weight)
        
        # Cria o layout do grafo
        pos = nx.spring_layout(G)
        
        # Prepara tamanhos e cores dos nós
        node_sizes = [G.nodes[node].get("size", 100) / 100 for node in G.nodes()]
        node_colors = [G.nodes[node].get("color", "#808080") for node in G.nodes()]
        
        # Prepara larguras e rótulos das arestas
        edge_widths = [G.edges[edge].get("weight", 1) / 10 for edge in G.edges()]
        edge_labels = {(u, v): f"{G.edges[u, v].get('weight', 0):.1f}%" for u, v in G.edges()}
        
        # Cria o gráfico
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Desenha os nós
        nx.draw_networkx_nodes(G, pos, node_size=[s * 1000 for s in node_sizes], node_color=node_colors, alpha=0.8, ax=ax)
        
        # Desenha as arestas
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5, edge_color="gray", ax=ax)
        
        # Adiciona rótulos aos nós
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold", ax=ax)
        
        # Adiciona rótulos às arestas
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, ax=ax)
        
        # Configura o gráfico
        ax.set_title("Rede de Conexões entre Plataformas")
        ax.axis("off")
        
        # Adiciona legenda
        for platform in platforms:
            plt.plot([], [], "o", color=self.platform_colors.get(platform.lower(), "#808080"), 
                    label=f"{platform.capitalize()} ({data[platform].get('follower_count', 0):,} seguidores)")
        
        plt.legend(loc="upper right")
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str
    
    def create_content_similarity_chart(self, data: Dict[str, Dict]) -> str:
        """
        Cria um gráfico de similaridade de conteúdo entre plataformas.
        
        Args:
            data: Dicionário com dados de cada plataforma e análise cruzada
            
        Returns:
            str: Imagem codificada em base64
        """
        # Verifica se há dados de análise cruzada
        if "cross_analysis" not in data or "content_similarity" not in data["cross_analysis"]:
            return None
        
        content_similarity = data["cross_analysis"]["content_similarity"]
        
        # Prepara os dados para o gráfico
        platforms = [p for p in data.keys() if p not in ["cross_platform", "cross_analysis"]]
        similarity_matrix = []
        
        # Cria matriz de similaridade
        for p1 in platforms:
            row = []
            for p2 in platforms:
                # Encontra a similaridade entre p1 e p2
                sim_value = 0
                for pair in content_similarity.get("platform_pairs", []):
                    if (pair.get("platform1", "") == p1 and pair.get("platform2", "") == p2) or \
                       (pair.get("platform1", "") == p2 and pair.get("platform2", "") == p1):
                        sim_value = pair.get("similarity_score", 0) * 100  # Converte para porcentagem
                        break
                
                # Se for a mesma plataforma, a similaridade é 100%
                if p1 == p2:
                    sim_value = 100
                    
                row.append(sim_value)
            
            similarity_matrix.append(row)
        
        # Cria DataFrame para o mapa de calor
        df = pd.DataFrame(similarity_matrix, index=[p.capitalize() for p in platforms], 
                         columns=[p.capitalize() for p in platforms])
        
        # Cria o mapa de calor
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(df, cmap="YlGnBu")
        
        # Adiciona rótulos e título
        ax.set_xticks(range(len(platforms)))
        ax.set_xticklabels([p.capitalize() for p in platforms])
        ax.set_yticks(range(len(platforms)))
        ax.set_yticklabels([p.capitalize() for p in platforms])
        ax.set_title("Similaridade de Conteúdo entre Plataformas (%)")
        
        # Adiciona barra de cores
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Similaridade (%)", rotation=-90, va="bottom")
        
        # Adiciona valores nas células
        for i in range(len(platforms)):
            for j in range(len(platforms)):
                ax.text(j, i, f"{similarity_matrix[i][j]:.1f}%", ha="center", va="center", 
                       color="black" if similarity_matrix[i][j] < 70 else "white")
        
        # Converte o gráfico para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        
        return img_str