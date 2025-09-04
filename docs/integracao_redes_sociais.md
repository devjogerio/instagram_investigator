# Integração com Outras Redes Sociais

Este documento descreve o processo de integração do Instagram Investigator com outras plataformas de redes sociais para análise cruzada de dados.

## Plataformas Suportadas

- Instagram (já implementado)
- Twitter/X (em implementação)
- Facebook (planejado)
- LinkedIn (planejado)
- TikTok (planejado)

## Arquitetura da Integração

A integração com múltiplas redes sociais segue uma arquitetura modular:

1. **Módulos de API**: Classes específicas para cada plataforma que gerenciam a comunicação com as APIs.
   - `instagram_api.py` (existente)
   - `twitter_api.py` (implementado)
   - `facebook_api.py` (planejado)
   - `linkedin_api.py` (planejado)
   - `tiktok_api.py` (planejado)

2. **Extratores de Dados**: Classes que processam os dados brutos das APIs e os transformam em um formato padronizado.
   - `instagram_extractor.py` (existente)
   - `twitter_extractor.py` (implementado)
   - `facebook_extractor.py` (planejado)
   - `linkedin_extractor.py` (planejado)
   - `tiktok_extractor.py` (planejado)

3. **Analisador de Plataformas Cruzadas**: Módulo que correlaciona dados entre diferentes plataformas.
   - `cross_platform_analyzer.py` (implementado)

4. **Interface Gráfica**: Componentes da UI para visualização e interação com dados de múltiplas plataformas.

## Configuração

Para utilizar a integração com outras redes sociais, é necessário configurar as credenciais de API para cada plataforma no arquivo `.env`. Um modelo está disponível em `.env.example`.

```
# Exemplo de configuração para Twitter/X
TWITTER_BEARER_TOKEN=seu_bearer_token_aqui
```

## Fluxo de Trabalho

1. **Autenticação**: Configure as credenciais para cada plataforma no arquivo `.env`.
2. **Investigação**: Utilize a interface para investigar perfis em diferentes plataformas.
3. **Análise Cruzada**: Visualize correlações e padrões entre os perfis nas diferentes redes sociais.
4. **Exportação**: Exporte os dados combinados para análise externa.

## Implementação da Análise Cruzada

A análise cruzada entre plataformas inclui:

- **Correspondência de Identidade**: Similaridade entre nomes de usuário, nomes reais e biografias.
- **Similaridade de Conteúdo**: Sobreposição de hashtags, URLs e temas de conteúdo.
- **Padrões de Atividade**: Comparação de frequência e horários de postagem.
- **Sobreposição de Audiência**: Análise de seguidores comuns entre plataformas.
- **Links entre Plataformas**: Detecção de referências cruzadas entre perfis.

## Próximos Passos

1. Finalizar a implementação da integração com Twitter/X.
2. Desenvolver os módulos para Facebook.
3. Implementar a integração com LinkedIn.
4. Adicionar suporte para TikTok.
5. Aprimorar a visualização de dados cruzados na interface.

## Limitações

- A disponibilidade e escopo dos dados dependem das restrições de cada API.
- Algumas plataformas podem exigir aprovação de aplicativo ou níveis de acesso específicos.
- A correlação entre plataformas é baseada em heurísticas e pode não ser 100% precisa.

## Dependências

As dependências necessárias estão listadas no arquivo `requirements.txt` e incluem:

- tweepy (para Twitter/X)
- facebook-sdk (para Facebook)
- linkedin-api (para LinkedIn)
- tiktokapi (para TikTok)
- pandas e networkx (para análise de dados)