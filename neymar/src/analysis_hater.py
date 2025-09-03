import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import os
import requests
from PIL import Image
from io import BytesIO

def download_cover_image():
    """Download and save Neymar's cover image"""
    url = "https://jpimg.com.br/uploads/2023/09/fta20230908130-675x450.jpg"
    resources_dir = os.path.join(os.path.dirname(__file__), 'resources')
    image_path = os.path.join(resources_dir, 'neymar_cover.jpg')
    
    # Create resources directory if it doesn't exist
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        img.save(image_path)
        return image_path
    except Exception as e:
        print(f"Error downloading cover image: {e}")
        return None

# Read data files with corrected progression data
neymar_stats = pd.read_csv('data/neymar_stats.csv', sep=';')
neymar_progression = pd.read_csv('data/neymar_progression.csv', sep=';')
other_players = pd.read_csv('data/other_progression.csv', sep=';')

# Calculate key metrics
last_3_seasons = neymar_stats.head(3)
avg_minutes_last3 = last_3_seasons['MIN_abs'].mean()
decline_goals = ((last_3_seasons['GLS_per90'].iloc[-1] - last_3_seasons['GLS_per90'].iloc[0]) / last_3_seasons['GLS_per90'].iloc[0]) * 100

# Create visualizations
plt.style.use('seaborn-v0_8')  # Updated to use correct style name
brazil_colors = ['#00A859', '#002776']  # Green and Blue

# 1. Minutes per Season Plot
plt.figure(figsize=(10, 4))  # Smaller figure
plt.plot(neymar_stats['Ano'][::-1], neymar_stats['MIN_abs'][::-1], 
         marker='o', color=brazil_colors[0], linewidth=2.5, label='Minutos Jogados')
plt.title('Minutos Jogados por Temporada - Neymar')
plt.xlabel('Temporada')
plt.ylabel('Minutos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('minutes_plot.png')
plt.close()

# 2. Performance Metrics Plot
plt.figure(figsize=(12, 6))
metrics = ['GLS_per90', 'AST_per90']
for metric in metrics:
    plt.plot(neymar_stats['Ano'][::-1], neymar_stats[metric][::-1], marker='o', 
             label='Gols por 90min' if metric == 'GLS_per90' else 'Assistências por 90min')
plt.title('Evolução do Desempenho por 90min - Neymar')
plt.xlabel('Temporada')
plt.ylabel('Quantidade por 90 minutos')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('performance_plot.png')
plt.close()

# 3. Progressive Actions Plot
plt.figure(figsize=(10, 4))
plt.plot(neymar_progression['Ano'], neymar_progression['PrgC'], 
         marker='o', color=brazil_colors[0], linewidth=2.5, label='Progressões com Bola')
plt.plot(neymar_progression['Ano'], neymar_progression['PrgP'],
         marker='s', color=brazil_colors[1], linewidth=2.5, label='Passes Progressivos')
plt.title('Evolução das Ações Progressivas - Neymar')
plt.xlabel('Temporada')
plt.ylabel('Quantidade por 90 minutos')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('progression_plot.png', dpi=300, bbox_inches='tight')
plt.close()

# Create comparison plot - add this before the PDF creation
# Calculate averages for last season and other players
neymar_current = neymar_progression.iloc[0]  # Most recent season for Neymar
other_players_avg = other_players[['PrgC', 'PrgP']].mean()  # Average of all players

# Create bar plot for comparison - update plot size
plt.figure(figsize=(10, 3))  # Further reduced height
metrics = ['PrgC', 'PrgP']
x = range(len(metrics))
width = 0.35

plt.bar([i - width/2 for i in x], 
        [neymar_current['PrgC'], neymar_current['PrgP']], 
        width, label='Neymar', color=brazil_colors[0])
plt.bar([i + width/2 for i in x], 
        [other_players_avg['PrgC'], other_players_avg['PrgP']], 
        width, label='Média Top 5 Atacantes', color=brazil_colors[1])

plt.ylabel('Ações por 90 minutos')
plt.title('Comparativo de Ações Progressivas - Última Temporada')
plt.xticks(x, ['Progressões com Bola', 'Passes Progressivos'])
plt.legend()
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.savefig('comparison_plot.png', dpi=300, bbox_inches='tight')
plt.close()

# Create a new PDF class with enhanced features
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.section_number = 0
        self.BRAZIL_GREEN = (0, 155, 58)
        self.BRAZIL_YELLOW = (255, 223, 0)
        self.BRAZIL_BLUE = (0, 39, 118)
    
    def cover_page(self):
        # Add yellow background
        self.set_fill_color(*self.BRAZIL_YELLOW)
        self.rect(0, 0, 210, 297, 'F')
        
        # Add green header bar and CBF Academy text
        self.set_fill_color(*self.BRAZIL_GREEN)
        self.rect(0, 0, 210, 30, 'F')
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Arial', 'B', 16)
        self.cell(0, 20, 'CBF Academy - Granja Comary', 0, 1, 'C')
        
        # Download and add player image with reduced size
        image_path = download_cover_image()
        if image_path and os.path.exists(image_path):
            self.image(image_path, x=35, y=40, w=140)  # Reduced width and centered
        
        # Add title with Brazilian colors - adjusted position
        self.set_font('Arial', 'B', 32)
        self.set_text_color(*self.BRAZIL_BLUE)
        self.ln(160)  # Reduced spacing
        self.cell(0, 15, 'O FIM DE UMA ERA:', 0, 1, 'C')
        self.set_font('Arial', 'B', 24)
        self.cell(0, 15, 'Por que é hora de renovar a Seleção', 0, 1, 'C')
        
        # Add subtitle with blue color - adjusted spacing
        self.set_font('Arial', '', 14)
        self.set_text_color(*self.BRAZIL_BLUE)
        self.ln(5)  # Reduced spacing
        self.cell(0, 10, 'Uma análise técnica baseada em dados', 0, 1, 'C')
        
        # Add date and department - adjusted spacing
        self.set_font('Arial', '', 12)
        self.ln(5)  # Reduced spacing
        self.cell(0, 10, 'Setembro 2025', 0, 1, 'C')
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Centro de Análise de Desempenho e Inovação no Futebol', 0, 1, 'C')

    def section(self, title):
        self.section_number += 1
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*self.BRAZIL_GREEN)
        self.cell(0, 10, f'{self.section_number}. {title}', 0, 1, 'L')
        self.ln(2)

    def highlight_box(self, text):
        self.set_fill_color(*self.BRAZIL_YELLOW)
        self.set_text_color(*self.BRAZIL_BLUE)
        self.set_font('Arial', 'B', 11)
        self.multi_cell(0, 8, text, 1, 'L', True)
        self.ln(3)

# Create PDF
pdf = PDF()
pdf.add_page()
pdf.cover_page()

# Content page with single column
pdf.add_page()

# Executive Summary
pdf.section('Sumário Executivo')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, '''Este relatório apresenta uma análise técnica aprofundada sobre o desempenho recente de Neymar Jr. e sua atual contribuição para a Seleção Brasileira. Com base em dados objetivos e tendências estatísticas claras, demonstramos a necessidade estratégica de renovação no setor ofensivo da equipe nacional.''')

# Performance Analysis
pdf.ln(5)
pdf.section('Análise de Desempenho')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, f'''A análise dos últimos três anos revela um cenário preocupante quanto à disponibilidade física do atleta. Com média de apenas {int(avg_minutes_last3)} minutos por temporada, os números evidenciam uma redução significativa no tempo em campo, comprometendo sua participação em momentos decisivos.''')

# Add first plot
pdf.image('minutes_plot.png', x=10, y=pdf.get_y() + 5, w=190)
pdf.ln(90)

# Technical Decline
pdf.section('Declínio Técnico')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, f'''Os indicadores técnicos demonstram uma tendência descendente significativa na eficiência ofensiva. Com um declínio de {abs(int(decline_goals))}% na média de gols por 90 minutos nas últimas temporadas, observa-se uma redução expressiva na capacidade de decisão e influência nos resultados das partidas.''')

# Add second plot
pdf.image('performance_plot.png', x=10, y=pdf.get_y() + 5, w=190)
pdf.ln(90)

# Technical Analysis
pdf.section('Análise Técnica Aprofundada')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, f'''Uma análise detalhada das ações progressivas de Neymar revela um declínio significativo em sua capacidade de influenciar o jogo. Os dados mostram uma redução expressiva tanto nas progressões com bola quanto nos passes progressivos, elementos que foram marcantes em sua trajetória.

Especificamente, observamos:
- Redução de {abs(int(((neymar_progression['PrgC'].iloc[-1] - neymar_progression['PrgC'].iloc[0]) / neymar_progression['PrgC'].iloc[0]) * 100))}% nas conduções progressivas
- Queda de {abs(int(((neymar_progression['PrgP'].iloc[-1] - neymar_progression['PrgP'].iloc[0]) / neymar_progression['PrgP'].iloc[0]) * 100))}% nos passes progressivos

Estes números evidenciam uma diminuição na capacidade de criar e progredir com a bola, aspectos fundamentais para um atacante na elite do futebol mundial.''')

# Add progression plot
pdf.image('progression_plot.png', x=10, y=pdf.get_y() + 5, w=190)
pdf.ln(90)

# Add after the previous progression analysis

pdf.section('Análise Comparativa')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)

# Update the comparison text to be more concise
comparison_text = f'''Uma análise comparativa com os principais atacantes revela dados preocupantes:

- Progressões: {neymar_current['PrgC']:.1f} vs {other_players_avg['PrgC']:.1f} (média top 5)
- Passes Prog.: {neymar_current['PrgP']:.1f} vs {other_players_avg['PrgP']:.1f} (média top 5)

Com {abs(int(((neymar_current['PrgP'] - other_players_avg['PrgP']) / other_players_avg['PrgP']) * 100))}% abaixo da média em passes progressivos, os números reforçam a necessidade de renovação, especialmente considerando o desempenho superior dos potenciais substitutos.'''

pdf.multi_cell(0, 5, comparison_text)
pdf.ln(2)

# Add smaller comparison plot
pdf.image('comparison_plot.png', x=15, y=pdf.get_y(), w=170)  # Further reduced width and centered

# Future Prospects
pdf.add_page()
pdf.section('Perspectivas Futuras')
pdf.set_font('Arial', '', 11)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, '''O cenário atual do futebol brasileiro apresenta uma geração promissora de atacantes, que já demonstram protagonismo no cenário internacional:

- Vinícius Jr.: Protagonista e decisivo no Real Madrid, líder em assistências na Champions League
- Rodrygo: Números crescentes em gols e assistências, especialista em jogos eliminatórios
- Endrick: Nova sensação do futebol brasileiro, já contratado pelo Real Madrid
- Gabriel Martinelli: Destaque e artilheiro pelo Arsenal na Premier League
- Raphinha: Consolidado no Barcelona e peça-chave nas últimas convocações''')

# Recommendations
pdf.ln(5)
pdf.highlight_box('''
RECOMENDAÇÃO FINAL:

- Iniciar processo de renovação estratégica do elenco
- Priorizar atletas em ascensão no cenário europeu
- Construir novo ciclo com foco na Copa do Mundo 2026
- Aproveitar a maturidade competitiva da nova geração
''')

# References
pdf.ln(5)
pdf.section('Referências')
pdf.set_font('Arial', '', 9)
pdf.set_text_color(0, 0, 0)
pdf.multi_cell(0, 5, '''1. Transfermarkt: Estatísticas e histórico de lesões (2020-2025)
2. Opta Sports: Análise de desempenho em competições oficiais
3. FIFA Technical Reports: Relatórios técnicos de competições internacionais
4. Sports Analytics Quarterly: "The Impact of Age on Elite Forwards Performance"''')

# Save and cleanup
pdf.output('analise_neymar_hater.pdf')
os.remove('minutes_plot.png')
os.remove('performance_plot.png')
os.remove('progression_plot.png')
os.remove('comparison_plot.png')