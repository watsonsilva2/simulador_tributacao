import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from calculo import SimuladorTributario

# Configuração da página
st.set_page_config(
    page_title="Simulador Tributário",
    page_icon="💰",
    layout="wide"
)

# Título do aplicativo
st.title("Simulador Tributário Empresarial")
st.markdown("### Compare os regimes tributários: Simples Nacional, Lucro Presumido e Lucro Real")

# Inicializando o simulador
simulador = SimuladorTributario()

# Criando abas
tab1, tab2, tab3 = st.tabs(["Simulação Básica", "Simulação Detalhada", "Sobre"])

with tab1:
    st.header("Simulação Básica")
    st.markdown("Informe o faturamento anual e as despesas para uma comparação rápida dos regimes tributários.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Entrada de faturamento
        receita_total = st.number_input(
            "Faturamento Anual (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=1000000.0,
            step=10000.0,
            format="%.2f"
        )
        
        # Seletor de tipo de atividade principal
        tipo_atividade = st.selectbox(
            "Atividade Principal",
            ["Comércio", "Indústria", "Serviços - Anexo III", "Serviços - Anexo IV", "Serviços - Anexo V"]
        )
    
    with col2:
        # Entrada de despesas
        despesa_total = st.number_input(
            "Despesas Totais (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=500000.0,
            step=10000.0,
            format="%.2f"
        )
        
        # Despesas com compras (para crédito de PIS/COFINS no Lucro Real)
        despesa_compras = st.number_input(
            "Despesas com Compras (R$)",
            min_value=0.0,
            max_value=despesa_total,
            value=min(300000.0, despesa_total),
            step=10000.0,
            format="%.2f"
        )
    
    # Converter tipo_atividade para o formato esperado pelo simulador
    mapeamento_atividades = {
        "Comércio": "comercio",
        "Indústria": "industria",
        "Serviços - Anexo III": "servicos_anexo_iii",
        "Serviços - Anexo IV": "servicos_anexo_iv",
        "Serviços - Anexo V": "servicos_anexo_v"
    }
    
    # Preparar dados para o simulador
    receitas = {mapeamento_atividades[tipo_atividade]: receita_total}
    
    # Distribuir outras despesas
    outras_despesas = despesa_total - despesa_compras
    
    despesas = {
        "compras": despesa_compras,
        "energia_aluguel_frete": outras_despesas * 0.3,  # 30% para energia, aluguel, frete
        "depreciacao": outras_despesas * 0.1,  # 10% para depreciação
        "demais_despesas": outras_despesas * 0.6  # 60% para demais despesas
    }
    
    # Botão para calcular
    if st.button("Calcular Tributos"):
        # Calcular comparação dos regimes
        resultados = simulador.comparar_regimes(receitas, despesas)
        
        # Exibir resultados
        st.markdown("## Resultados da Simulação")
        
        # Criar colunas para os regimes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Simples Nacional")
            st.markdown(f"**Valor do Imposto:** R$ {resultados['simples_nacional']['valor_imposto']:,.2f}")
            st.markdown(f"**Alíquota Efetiva:** {resultados['simples_nacional']['aliquota_efetiva']*100:.2f}%")
        
        with col2:
            st.markdown("### Lucro Presumido")
            st.markdown(f"**Valor do Imposto:** R$ {resultados['lucro_presumido']['valor_imposto']:,.2f}")
            st.markdown(f"**Alíquota Efetiva:** {resultados['lucro_presumido']['aliquota_efetiva']*100:.2f}%")
        
        with col3:
            st.markdown("### Lucro Real")
            st.markdown(f"**Valor do Imposto:** R$ {resultados['lucro_real']['valor_imposto']:,.2f}")
            st.markdown(f"**Alíquota Efetiva:** {resultados['lucro_real']['aliquota_efetiva']*100:.2f}%")
        
        # Exibir melhor opção
        st.success(f"## Melhor Opção: {resultados['melhor_opcao']['regime']} - R$ {resultados['melhor_opcao']['valor']:,.2f}")
        
        # Criar um gráfico de comparação
        fig, ax = plt.subplots(figsize=(10, 6))
        
        regimes = ["Simples Nacional", "Lucro Presumido", "Lucro Real"]
        valores = [
            resultados['simples_nacional']['valor_imposto'],
            resultados['lucro_presumido']['valor_imposto'],
            resultados['lucro_real']['valor_imposto']
        ]
        
        # Adicionar cores para cada regime
        cores = ['#ff9999', '#66b3ff', '#99ff99']
        
        # Destacar a melhor opção
        melhor_opcao_index = regimes.index(resultados['melhor_opcao']['regime'])
        cores_barras = [cor for cor in cores]
        cores_barras[melhor_opcao_index] = '#32CD32'  # Cor verde mais forte para destacar
        
        # Criar o gráfico de barras
        barras = ax.bar(regimes, valores, color=cores_barras)
        
        # Adicionar valores no topo das barras
        for i, barra in enumerate(barras):
            ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 1000,
                    f'R$ {valores[i]:,.2f}', ha='center', va='bottom', fontsize=12)
        
        ax.set_ylabel('Valor Total de Impostos (R$)')
        ax.set_title('Comparação entre Regimes Tributários')
        plt.xticks(rotation=0)
        
        # Exibir o gráfico no Streamlit
        st.pyplot(fig)
        
        # Exibir detalhamento dos impostos
        st.markdown("## Detalhamento dos Impostos")
        
        # Criar tabelas para cada regime
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Lucro Presumido")
            detalhamento_lp = pd.DataFrame({
                'Imposto': list(resultados['lucro_presumido']['detalhamento'].keys()),
                'Valor (R$)': list(resultados['lucro_presumido']['detalhamento'].values())
            })
            detalhamento_lp = detalhamento_lp[detalhamento_lp['Imposto'] != 'total']
            detalhamento_lp = detalhamento_lp[detalhamento_lp['Valor (R$)'] > 0]
            st.dataframe(detalhamento_lp)
        
        with col2:
            st.markdown("### Lucro Real")
            detalhamento_lr = pd.DataFrame({
                'Imposto': list(resultados['lucro_real']['detalhamento'].keys()),
                'Valor (R$)': list(resultados['lucro_real']['detalhamento'].values())
            })
            detalhamento_lr = detalhamento_lr[detalhamento_lr['Imposto'] != 'total']
            detalhamento_lr = detalhamento_lr[detalhamento_lr['Valor (R$)'] > 0]
            st.dataframe(detalhamento_lr)

with tab2:
    st.header("Simulação Detalhada")
    st.markdown("Informe o detalhamento das receitas e despesas para uma análise mais precisa.")
    
    # Criação de colunas para receitas e despesas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Receitas")
        
        # Entradas para cada tipo de receita
        receita_comercio = st.number_input(
            "Comércio (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=0.0,
            step=10000.0,
            format="%.2f"
        )
        
        receita_industria = st.number_input(
            "Indústria (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=1000000.0,
            step=10000.0,
            format="%.2f"
        )
        
        receita_servicos_anexo_iii = st.number_input(
            "Serviços - Anexo III (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=0.0,
            step=10000.0,
            format="%.2f"
        )
        
        receita_servicos_anexo_iv = st.number_input(
            "Serviços - Anexo IV (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=0.0,
            step=10000.0,
            format="%.2f"
        )
        
        receita_servicos_anexo_v = st.number_input(
            "Serviços - Anexo V (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=0.0,
            step=10000.0,
            format="%.2f"
        )
    
    with col2:
        st.subheader("Despesas")
        
        # Entradas para cada tipo de despesa
        despesa_salarios = st.number_input(
            "Salários (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=200000.0,
            step=10000.0,
            format="%.2f"
        )
        
        despesa_compras_detalhada = st.number_input(
            "Compras/Estoque (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=500000.0,
            step=10000.0,
            format="%.2f"
        )
        
        despesa_energia_aluguel_frete = st.number_input(
            "Energia/Aluguel/Frete (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=36000.0,
            step=1000.0,
            format="%.2f"
        )
        
        despesa_depreciacao = st.number_input(
            "Depreciação (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=10000.0,
            step=1000.0,
            format="%.2f"
        )
        
        despesa_outras = st.number_input(
            "Outras Despesas (R$)",
            min_value=0.0,
            max_value=10000000.0,
            value=0.0,
            step=10000.0,
            format="%.2f"
        )
    
    # Preparar dados para o simulador
    receitas_detalhadas = {
        "comercio": receita_comercio,
        "industria": receita_industria,
        "servicos_anexo_iii": receita_servicos_anexo_iii,
        "servicos_anexo_iv": receita_servicos_anexo_iv,
        "servicos_anexo_v": receita_servicos_anexo_v
    }
    
    # Filtrar receitas com valor zero
    receitas_detalhadas = {k: v for k, v in receitas_detalhadas.items() if v > 0}
    
    despesas_detalhadas = {
        "salarios": despesa_salarios,
        "compras": despesa_compras_detalhada,
        "energia_aluguel_frete": despesa_energia_aluguel_frete,
        "depreciacao": despesa_depreciacao,
        "demais_despesas": despesa_outras
    }
    
    # Botão para calcular simulação detalhada
    if st.button("Calcular Simulação Detalhada"):
        # Verificar se há receitas informadas
        if not receitas_detalhadas:
            st.warning("Por favor, informe pelo menos um tipo de receita.")
        else:
            # Calcular resultados
            resultados_detalhados = simulador.comparar_regimes(receitas_detalhadas, despesas_detalhadas)
            
            # Exibir resultados
            st.markdown("## Resultados da Simulação Detalhada")
            
            # Totais
            receita_total_detalhada = sum(receitas_detalhadas.values())
            despesa_total_detalhada = sum(despesas_detalhadas.values())
            
            # Informações gerais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Receita Total", f"R$ {receita_total_detalhada:,.2f}")
            
            with col2:
                st.metric("Despesa Total", f"R$ {despesa_total_detalhada:,.2f}")
            
            with col3:
                st.metric("Lucro Bruto", f"R$ {(receita_total_detalhada - despesa_total_detalhada):,.2f}")
            
            # Comparativo dos regimes
            st.markdown("### Comparativo dos Regimes Tributários")
            
            # Criar dataframe para comparação
            dados_comparacao = {
                'Regime': ["Simples Nacional", "Lucro Presumido", "Lucro Real"],
                'Valor do Imposto (R$)': [
                    resultados_detalhados['simples_nacional']['valor_imposto'],
                    resultados_detalhados['lucro_presumido']['valor_imposto'],
                    resultados_detalhados['lucro_real']['valor_imposto']
                ],
                'Alíquota Efetiva (%)': [
                    resultados_detalhados['simples_nacional']['aliquota_efetiva'] * 100,
                    resultados_detalhados['lucro_presumido']['aliquota_efetiva'] * 100,
                    resultados_detalhados['lucro_real']['aliquota_efetiva'] * 100
                ],
                'Lucro Líquido (R$)': [
                    receita_total_detalhada - despesa_total_detalhada - resultados_detalhados['simples_nacional']['valor_imposto'],
                    receita_total_detalhada - despesa_total_detalhada - resultados_detalhados['lucro_presumido']['valor_imposto'],
                    receita_total_detalhada - despesa_total_detalhada - resultados_detalhados['lucro_real']['valor_imposto']
                ]
            }
            
            df_comparacao = pd.DataFrame(dados_comparacao)
            
            # Formatar valores monetários e percentuais
            df_comparacao['Valor do Imposto (R$)'] = df_comparacao['Valor do Imposto (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            df_comparacao['Alíquota Efetiva (%)'] = df_comparacao['Alíquota Efetiva (%)'].apply(lambda x: f"{x:.2f}%")
            df_comparacao['Lucro Líquido (R$)'] = df_comparacao['Lucro Líquido (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            
            # Exibir tabela comparativa
            st.dataframe(df_comparacao, use_container_width=True)
            
            # Destacar melhor opção
            st.success(f"## Melhor Opção: {resultados_detalhados['melhor_opcao']['regime']} - {resultados_detalhados['melhor_opcao']['valor']:,.2f}")
            
            # Gráficos de comparação
            st.markdown("### Análise Gráfica")
            
            # Gráfico de barras comparando os impostos
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            
            valores_impostos = [
                resultados_detalhados['simples_nacional']['valor_imposto'],
                resultados_detalhados['lucro_presumido']['valor_imposto'],
                resultados_detalhados['lucro_real']['valor_imposto']
            ]
            
            regimes = ["Simples Nacional", "Lucro Presumido", "Lucro Real"]
            
            # Cores para cada regime
            cores = ['#ff9999', '#66b3ff', '#99ff99']
            
            # Destacar a melhor opção
            melhor_opcao_index = regimes.index(resultados_detalhados['melhor_opcao']['regime'])
            cores_barras = [cor for cor in cores]
            cores_barras[melhor_opcao_index] = '#32CD32'  # Cor verde mais forte para destacar
            
            # Criar o gráfico de barras
            barras = ax1.bar(regimes, valores_impostos, color=cores_barras)
            
            # Adicionar valores no topo das barras
            for i, barra in enumerate(barras):
                ax1.text(barra.get_x() + barra.get_width()/2, barra.get_height() + valores_impostos[i]*0.02,
                        f'R$ {valores_impostos[i]:,.2f}', ha='center', va='bottom', fontsize=12)
            
            ax1.set_ylabel('Valor Total de Impostos (R$)')
            ax1.set_title('Comparação de Impostos entre Regimes Tributários')
            plt.xticks(rotation=0)
            
            # Exibir o gráfico no Streamlit
            st.pyplot(fig1)
            
            # Gráfico de pizza para a composição dos impostos no regime escolhido
            st.markdown(f"### Composição dos Impostos - {resultados_detalhados['melhor_opcao']['regime']}")
            
            # Obter detalhamento conforme o regime escolhido
            if resultados_detalhados['melhor_opcao']['regime'] == 'Simples Nacional':
                # Simples Nacional não tem detalhamento, é um imposto único
                dados_pizza = {
                    'Imposto': ['Simples Nacional'],
                    'Valor': [resultados_detalhados['simples_nacional']['valor_imposto']]
                }
            elif resultados_detalhados['melhor_opcao']['regime'] == 'Lucro Presumido':
                detalhamento = resultados_detalhados['lucro_presumido']['detalhamento']
                dados_pizza = {
                    'Imposto': [k for k, v in detalhamento.items() if k != 'total' and v > 0],
                    'Valor': [v for k, v in detalhamento.items() if k != 'total' and v > 0]
                }
            else:  # Lucro Real
                detalhamento = resultados_detalhados['lucro_real']['detalhamento']
                dados_pizza = {
                    'Imposto': [k for k, v in detalhamento.items() if k != 'total' and v > 0],
                    'Valor': [v for k, v in detalhamento.items() if k != 'total' and v > 0]
                }
            
            # Verificar se há dados para o gráfico de pizza
            if dados_pizza['Valor']:
                fig2, ax2 = plt.subplots(figsize=(10, 10))
                
                # Criar gráfico de pizza
                patches, texts, autotexts = ax2.pie(
                    dados_pizza['Valor'], 
                    labels=dados_pizza['Imposto'],
                    autopct='%1.1f%%',
                    startangle=90,
                    shadow=True
                )
                
                # Formatar os textos
                for text in texts:
                    text.set_fontsize(12)
                for autotext in autotexts:
                    autotext.set_fontsize(10)
                    autotext.set_color('white')
                
                ax2.axis('equal')  # Garantir que o gráfico seja um círculo
                ax2.set_title(f'Composição dos Impostos - {resultados_detalhados["melhor_opcao"]["regime"]}')
                
                # Exibir o gráfico no Streamlit
                st.pyplot(fig2)
                
                # Tabela de detalhamento dos impostos
                if resultados_detalhados['melhor_opcao']['regime'] != 'Simples Nacional':
                    st.markdown(f"### Detalhamento dos Impostos - {resultados_detalhados['melhor_opcao']['regime']}")
                    
                    df_detalhamento = pd.DataFrame({
                        'Imposto': dados_pizza['Imposto'],
                        'Valor (R$)': dados_pizza['Valor']
                    })
                    
                    # Ordenar por valor decrescente
                    df_detalhamento = df_detalhamento.sort_values(by='Valor (R$)', ascending=False)
                    
                    # Formatar valores
                    df_detalhamento['Valor (R$)'] = df_detalhamento['Valor (R$)'].apply(lambda x: f"R$ {x:,.2f}")
                    
                    st.dataframe(df_detalhamento, use_container_width=True)
            
            # Análise de sensibilidade - variação do faturamento
            st.markdown("### Análise de Sensibilidade")
            st.markdown("Veja como os impostos variam com diferentes níveis de faturamento, mantendo a proporção de despesas.")
            
            # Definir valores para análise de sensibilidade
            faturamento_base = receita_total_detalhada
            
            # Calcular proporção das despesas em relação ao faturamento
            proporcao_despesas = despesa_total_detalhada / faturamento_base if faturamento_base > 0 else 0
            
            # Criar faixas de faturamento para análise
            faixas_faturamento = [
                faturamento_base * 0.5,
                faturamento_base * 0.75,
                faturamento_base,
                faturamento_base * 1.25,
                faturamento_base * 1.5,
                faturamento_base * 2.0
            ]
            
            # Calcular impostos para cada faixa
            dados_sensibilidade = {
                'Faturamento (R$)': [],
                'Simples Nacional (R$)': [],
                'Lucro Presumido (R$)': [],
                'Lucro Real (R$)': []
            }
            
            for faturamento in faixas_faturamento:
                # Ajustar as receitas proporcionalmente
                receitas_ajustadas = {k: v * (faturamento / faturamento_base) for k, v in receitas_detalhadas.items()}
                
                # Ajustar as despesas proporcionalmente
                despesas_ajustadas = {k: v * (faturamento / faturamento_base) for k, v in despesas_detalhadas.items()}
                
                # Calcular os impostos
                resultados_sensibilidade = simulador.comparar_regimes(receitas_ajustadas, despesas_ajustadas)
                
                # Armazenar os resultados
                dados_sensibilidade['Faturamento (R$)'].append(faturamento)
                dados_sensibilidade['Simples Nacional (R$)'].append(resultados_sensibilidade['simples_nacional']['valor_imposto'])
                dados_sensibilidade['Lucro Presumido (R$)'].append(resultados_sensibilidade['lucro_presumido']['valor_imposto'])
                dados_sensibilidade['Lucro Real (R$)'].append(resultados_sensibilidade['lucro_real']['valor_imposto'])
            
            # Criar DataFrame para a análise de sensibilidade
            df_sensibilidade = pd.DataFrame(dados_sensibilidade)
            
            # Criar gráfico de linha
            fig3, ax3 = plt.subplots(figsize=(12, 8))
            
            ax3.plot(df_sensibilidade['Faturamento (R$)'], df_sensibilidade['Simples Nacional (R$)'], 'o-', color='red', label='Simples Nacional')
            ax3.plot(df_sensibilidade['Faturamento (R$)'], df_sensibilidade['Lucro Presumido (R$)'], 'o-', color='blue', label='Lucro Presumido')
            ax3.plot(df_sensibilidade['Faturamento (R$)'], df_sensibilidade['Lucro Real (R$)'], 'o-', color='green', label='Lucro Real')
            
            # Formatação do gráfico
            ax3.set_xlabel('Faturamento (R$)')
            ax3.set_ylabel('Valor do Imposto (R$)')
            ax3.set_title('Análise de Sensibilidade - Variação do Faturamento')
            
            # Formatar eixo x para mostrar valores em milhares/milhões
            from matplotlib.ticker import FuncFormatter
            
            def milhares(x, pos):
                if x >= 1e6:
                    return f'{x*1e-6:.1f}M'
                else:
                    return f'{x*1e-3:.0f}K'
            
            ax3.xaxis.set_major_formatter(FuncFormatter(milhares))
            ax3.grid(True, linestyle='--', alpha=0.7)
            ax3.legend()
            
            # Exibir o gráfico
            st.pyplot(fig3)
            
            # Exibir tabela de sensibilidade
            df_sensibilidade_formatada = df_sensibilidade.copy()
            df_sensibilidade_formatada['Faturamento (R$)'] = df_sensibilidade_formatada['Faturamento (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            df_sensibilidade_formatada['Simples Nacional (R$)'] = df_sensibilidade_formatada['Simples Nacional (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            df_sensibilidade_formatada['Lucro Presumido (R$)'] = df_sensibilidade_formatada['Lucro Presumido (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            df_sensibilidade_formatada['Lucro Real (R$)'] = df_sensibilidade_formatada['Lucro Real (R$)'].apply(lambda x: f"R$ {x:,.2f}")
            
            st.dataframe(df_sensibilidade_formatada, use_container_width=True)

with tab3:
    st.header("Sobre o Simulador Tributário")
    
    st.markdown("""
    ## Como funciona este simulador?
    
    Este simulador tributário foi desenvolvido para ajudar empresas a comparar os diferentes regimes tributários brasileiros:
    
    - **Simples Nacional**: Regime simplificado para micro e pequenas empresas
    - **Lucro Presumido**: Regime com base em percentuais de presunção sobre o faturamento
    - **Lucro Real**: Regime baseado no lucro efetivo da empresa
    
    ## Simulação Básica
    
    Na aba "Simulação Básica", você pode fazer uma comparação rápida informando apenas:
    
    - Faturamento anual total
    - Tipo principal de atividade
    - Despesas totais
    - Despesas com compras (para cálculo de créditos no Lucro Real)
    
    ## Simulação Detalhada
    
    Na aba "Simulação Detalhada", você pode informar:
    
    - Detalhamento das receitas por tipo de atividade
    - Detalhamento das despesas por categoria
    
    Esta opção permite uma análise mais precisa e gera gráficos comparativos adicionais.
    
    ## Limitações
    
    Este simulador é uma ferramenta de apoio e não substitui a análise de um contador. 
    Os resultados são estimativas baseadas nas alíquotas e regras tributárias atuais.
    
    Para uma análise mais completa e atualizada, sempre consulte um profissional especializado.
    
    ## Tributos Considerados
    
    - **Simples Nacional**: Imposto unificado com alíquotas progressivas
    - **Lucro Presumido**: PIS, COFINS, IRPJ, CSLL, ICMS, ISS, IPI
    - **Lucro Real**: PIS, COFINS, IRPJ, CSLL, ICMS, ISS, IPI
    
    ## Responsabilidade
    
    As informações e cálculos apresentados neste simulador são de caráter informativo e educacional.
    As decisões tributárias devem ser tomadas com base em análise profissional especializada.
    """)

# Rodapé
st.markdown("---")
st.markdown("### Simulador Tributário Empresarial | Desenvolvido como ferramenta de apoio à decisão gerencial")
st.markdown("*Os cálculos são estimativas e não substituem a análise de um contador profissional.*")

# Função principal para execução do aplicativo
if __name__ == "__main__":
    pass  # O Streamlit executa todo o script por padrão
