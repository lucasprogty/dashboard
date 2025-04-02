import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import dash_bootstrap_components as dbc

# Carregar os dados
df = pd.read_csv('ecommerce_estatistica.csv')


# fazendo a categoria "outros" para o grafico
def categorizar_temporada(temporada):
    if temporada in ['outono/inverno', 'primavera/verão']:
        return temporada
    else:
        return 'Outros'


df['Temporada'] = df['Temporada'].apply(categorizar_temporada)

# vamos iniciar o dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Análise de Dados  E-commerce", className="text-center my-4"), width=12)),

    dbc.Row([
        dbc.Col([
            html.H3("Distribuição de Notas dos Produtos", className="text-center"),
            dcc.Graph(id='histograma-notas')
        ], md=6),

        dbc.Col([
            html.H3("Relação entre Desconto e Nota", className="text-center"),
            dcc.Graph(id='dispersao-desconto-nota')
        ], md=6)
    ]),

    dbc.Row(dbc.Col([
        html.H3("Correlação entre Variáveis", className="text-center mt-4"),
        dcc.Graph(id='mapa-calor')
    ], width=12)),

    dbc.Row([
        dbc.Col([
            html.H3("Distribuição por Temporada", className="text-center"),
            dcc.Graph(id='grafico-pizza')
        ], md=6),

        dbc.Col([
            html.H3("Densidade das Notas", className="text-center"),
            dcc.Graph(id='grafico-densidade')
        ], md=6)
    ]),

    dbc.Row(dbc.Col([
        html.H3("Relação entre Preço e Nota", className="text-center mt-4"),
        dcc.Graph(id='grafico-regressao')
    ], width=12)),

    dbc.Row(dbc.Col(
        html.Footer("Analise de e-commerce | Dados atualizados em abril 2024",
                    className="text-center mt-5 text-muted")
    ))
], fluid=True)


# Callbacks para atualizar
@app.callback(
    Output('histograma-notas', 'figure'),
    Output('dispersao-desconto-nota', 'figure'),
    Output('mapa-calor', 'figure'),
    Output('grafico-pizza', 'figure'),
    Output('grafico-densidade', 'figure'),
    Output('grafico-regressao', 'figure'),
    Input('histograma-notas', 'relayoutData')
)
def update_graphs(_):
    # Histograma
    fig_hist = px.histogram(df, x='Nota', nbins=10,
                            title='Distribuição de Notas dos Produtos',
                            labels={'Nota': 'Nota do Produto', 'count': 'Frequência'},
                            color_discrete_sequence=['#2c7fb8'])
    fig_hist.update_layout(bargap=0.1)

    # Dispersão
    fig_disp = px.scatter(df, x='Nota', y='Desconto',
                          title='Relação entre Desconto e Nota do Produto',
                          labels={'Nota': 'Nota do Produto', 'Desconto': 'Desconto (%)'},
                          trendline="lowess",
                          color_discrete_sequence=['#e6550d'])

    # Mapa de Calor
    colunas_numericas = ['Nota_MinMax', 'N_Avaliações_MinMax', 'Desconto_MinMax', 'Preço_MinMax', 'Qtd_Vendidos_Cod']
    corr_matrix = df[colunas_numericas].corr()
    fig_heatmap = px.imshow(corr_matrix,
                            text_auto=True,
                            color_continuous_scale='RdBu',
                            title='Correlação entre Variáveis Numéricas',
                            labels=dict(color="Correlação"))
    fig_heatmap.update_layout(height=500)

    # Gráfico de Pizza
    distribuicao_temporada = df['Temporada'].value_counts().reset_index()
    distribuicao_temporada.columns = ['Temporada', 'Quantidade']
    fig_pie = px.pie(distribuicao_temporada, values='Quantidade', names='Temporada',
                     title='Distribuição de Produtos por Temporada',
                     color_discrete_sequence=px.colors.sequential.RdBu,
                     hole=0.3)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')



    # Gráfico de Regressão
    fig_reg = px.scatter(df, x='Preço', y='Nota',
                         trendline="ols",
                         title='Relação entre Preço e Nota do Produto',
                         labels={'Preço': 'Preço (R$)', 'Nota': 'Nota do Produto'},
                         color_discrete_sequence=['#756bb1'])
    fig_reg.update_traces(marker=dict(size=8, opacity=0.6))

    return fig_hist, fig_disp, fig_heatmap, fig_pie, fig_reg


# Executar o aplicativo
if __name__ == '__main__':
    app.run(debug=True)