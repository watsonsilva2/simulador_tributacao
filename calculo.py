class SimuladorTributario:
    def __init__(self):
        # Alíquotas do Simples Nacional - Formato: (limite_superior, aliquota, valor_a_deduzir)
        self.tabela_simples = [
            (180000.00, 0.04, 0),
            (360000.00, 0.073, 5940),
            (720000.00, 0.095, 13860),
            (1800000.00, 0.107, 22500),
            (3600000.00, 0.143, 87300),
            (float('inf'), 0.19, 378000)
        ]
        
        # Alíquotas do Lucro Presumido
        self.aliquotas_lp = {
            'pis': 0.0065,
            'cofins': 0.03,
            'irpj': 0.15,
            'adicional_irpj': 0.10,  # Aplicado sobre o que exceder R$ 20.000 por mês
            'csll': 0.09,
            'ipi': 0.10,
            'icms': 0.22,
            'iss': 0.0375,
            'rat': 0.01
        }
        
        # Percentuais de presunção para o Lucro Presumido
        self.percentuais_presuncao = {
            'comercio': 0.08,  # 8% para IRPJ
            'industria': 0.08,  # 8% para IRPJ
            'servicos': 0.32,  # 32% para IRPJ em serviços em geral
            'transporte': 0.16,  # 16% para IRPJ em transporte
            'servicos_profissionais': 0.32  # 32% para IRPJ em serviços profissionais
        }
        
        # Alíquotas do Lucro Real
        self.aliquotas_lr = {
            'pis': 0.0165,
            'cofins': 0.076,
            'irpj': 0.15,
            'adicional_irpj': 0.10,  # Aplicado sobre o que exceder R$ 20.000 por mês
            'csll': 0.09,
            'ipi': 0.10,
            'icms': 0.22,
            'iss': 0.0375,
            'rat': 0.01
        }
        
    def calcular_simples_nacional(self, receita_total):
        """
        Calcula o valor do Simples Nacional com base na receita total
        """
        for limite, aliquota, deducao in self.tabela_simples:
            if receita_total <= limite:
                imposto = (receita_total * aliquota) - deducao
                return imposto
        
        # Se não se encaixar em nenhuma faixa, usa a última (maior faixa)
        imposto = (receita_total * self.tabela_simples[-1][1]) - self.tabela_simples[-1][2]
        return imposto
    
    def calcular_lucro_presumido(self, receitas, despesas=None):
        """
        Calcula os impostos no regime de Lucro Presumido
        
        Args:
            receitas: dicionário com valores de receita por tipo
            despesas: dicionário com valores de despesa (não usado no cálculo do Lucro Presumido, 
                      apenas incluído para manter interface consistente)
        
        Returns:
            dicionário com os valores de cada imposto e o total
        """
        # Calcula a receita total
        receita_total = sum(receitas.values())
        
        # Inicializa os impostos
        impostos = {
            'pis': 0,
            'cofins': 0,
            'irpj': 0,
            'adicional_irpj': 0,
            'csll': 0,
            'ipi': 0,
            'icms': 0,
            'iss': 0,
            'rat': 0,
            'total': 0
        }
        
        # Calcula PIS e COFINS
        impostos['pis'] = receita_total * self.aliquotas_lp['pis']
        impostos['cofins'] = receita_total * self.aliquotas_lp['cofins']
        
        # Base de cálculo para IRPJ e CSLL
        base_irpj = 0
        base_csll = 0
        
        # Calcula base de IRPJ e CSLL por tipo de receita
        if 'comercio' in receitas and receitas['comercio'] > 0:
            base_irpj += receitas['comercio'] * self.percentuais_presuncao['comercio']
            base_csll += receitas['comercio'] * 0.12  # 12% para CSLL
            
        if 'industria' in receitas and receitas['industria'] > 0:
            base_irpj += receitas['industria'] * self.percentuais_presuncao['industria']
            base_csll += receitas['industria'] * 0.12  # 12% para CSLL
            
        if 'servicos' in receitas and receitas['servicos'] > 0:
            base_irpj += receitas['servicos'] * self.percentuais_presuncao['servicos']
            base_csll += receitas['servicos'] * 0.32  # 32% para CSLL
            
        if 'servicos_anexo_iii' in receitas and receitas['servicos_anexo_iii'] > 0:
            base_irpj += receitas['servicos_anexo_iii'] * self.percentuais_presuncao['servicos']
            base_csll += receitas['servicos_anexo_iii'] * 0.32  # 32% para CSLL
            
        if 'servicos_anexo_iv' in receitas and receitas['servicos_anexo_iv'] > 0:
            base_irpj += receitas['servicos_anexo_iv'] * self.percentuais_presuncao['servicos_profissionais']
            base_csll += receitas['servicos_anexo_iv'] * 0.32  # 32% para CSLL
            
        if 'servicos_anexo_v' in receitas and receitas['servicos_anexo_v'] > 0:
            base_irpj += receitas['servicos_anexo_v'] * self.percentuais_presuncao['servicos']
            base_csll += receitas['servicos_anexo_v'] * 0.32  # 32% para CSLL
        
        # Calcula IRPJ
        impostos['irpj'] = base_irpj * self.aliquotas_lp['irpj']
        
        # Calcula Adicional de IRPJ se base anual exceder R$ 240.000 (R$ 20.000 por mês)
        if base_irpj > 240000:
            impostos['adicional_irpj'] = (base_irpj - 240000) * self.aliquotas_lp['adicional_irpj']
        
        # Calcula CSLL
        impostos['csll'] = base_csll * self.aliquotas_lp['csll']
        
        # Calcula outros impostos se houver as respectivas receitas
        if 'industria' in receitas and receitas['industria'] > 0:
            impostos['ipi'] = receitas['industria'] * self.aliquotas_lp['ipi']
            
        if 'comercio' in receitas and receitas['comercio'] > 0:
            impostos['icms'] = receitas['comercio'] * self.aliquotas_lp['icms']
            
        if ('servicos' in receitas and receitas['servicos'] > 0) or \
           ('servicos_anexo_iii' in receitas and receitas['servicos_anexo_iii'] > 0) or \
           ('servicos_anexo_iv' in receitas and receitas['servicos_anexo_iv'] > 0) or \
           ('servicos_anexo_v' in receitas and receitas['servicos_anexo_v'] > 0):
            # Soma todos os serviços para calcular ISS
            total_servicos = receitas.get('servicos', 0) + \
                             receitas.get('servicos_anexo_iii', 0) + \
                             receitas.get('servicos_anexo_iv', 0) + \
                             receitas.get('servicos_anexo_v', 0)
            impostos['iss'] = total_servicos * self.aliquotas_lp['iss']
        
        # Calcula o total de impostos
        impostos['total'] = sum(valor for chave, valor in impostos.items() if chave != 'total')
        
        return impostos
    
    def calcular_lucro_real(self, receitas, despesas):
        """
        Calcula os impostos no regime de Lucro Real
        
        Args:
            receitas: dicionário com valores de receita por tipo
            despesas: dicionário com valores de despesa por tipo
            
        Returns:
            dicionário com os valores de cada imposto e o total
        """
        # Calcula a receita total
        receita_total = sum(receitas.values())
        
        # Calcula a despesa total
        despesa_total = sum(despesas.values())
        
        # Inicializa os impostos
        impostos = {
            'pis': 0,
            'cofins': 0,
            'irpj': 0,
            'adicional_irpj': 0,
            'csll': 0,
            'ipi': 0,
            'icms': 0,
            'iss': 0,
            'rat': 0,
            'total': 0
        }
        
        # No Lucro Real, o PIS e COFINS são não-cumulativos (permitem créditos)
        # Consideramos que as despesas com compras, energia, aluguel e frete geram créditos
        creditos_pis_cofins = 0
        if 'compras' in despesas:
            creditos_pis_cofins += despesas['compras']
        if 'energia_aluguel_frete' in despesas:
            creditos_pis_cofins += despesas['energia_aluguel_frete']
            
        # Calcula PIS e COFINS considerando os créditos
        pis_sobre_receita = receita_total * self.aliquotas_lr['pis']
        cofins_sobre_receita = receita_total * self.aliquotas_lr['cofins']
        
        pis_sobre_creditos = creditos_pis_cofins * self.aliquotas_lr['pis']
        cofins_sobre_creditos = creditos_pis_cofins * self.aliquotas_lr['cofins']
        
        impostos['pis'] = max(0, pis_sobre_receita - pis_sobre_creditos)
        impostos['cofins'] = max(0, cofins_sobre_receita - cofins_sobre_creditos)
        
        # Calcula o lucro contábil (receita - despesa)
        lucro_contabil = receita_total - despesa_total
        
        # No Lucro Real, o IRPJ e CSLL são calculados sobre o lucro contábil
        if lucro_contabil > 0:
            # Calcula IRPJ
            impostos['irpj'] = lucro_contabil * self.aliquotas_lr['irpj']
            
            # Calcula Adicional de IRPJ se lucro anual exceder R$ 240.000 (R$ 20.000 por mês)
            if lucro_contabil > 240000:
                impostos['adicional_irpj'] = (lucro_contabil - 240000) * self.aliquotas_lr['adicional_irpj']
            
            # Calcula CSLL
            impostos['csll'] = lucro_contabil * self.aliquotas_lr['csll']
        
        # Calcula outros impostos se houver as respectivas receitas
        if 'industria' in receitas and receitas['industria'] > 0:
            impostos['ipi'] = receitas['industria'] * self.aliquotas_lr['ipi']
            
        if 'comercio' in receitas and receitas['comercio'] > 0:
            impostos['icms'] = receitas['comercio'] * self.aliquotas_lr['icms']
            
        if ('servicos' in receitas and receitas['servicos'] > 0) or \
           ('servicos_anexo_iii' in receitas and receitas['servicos_anexo_iii'] > 0) or \
           ('servicos_anexo_iv' in receitas and receitas['servicos_anexo_iv'] > 0) or \
           ('servicos_anexo_v' in receitas and receitas['servicos_anexo_v'] > 0):
            # Soma todos os serviços para calcular ISS
            total_servicos = receitas.get('servicos', 0) + \
                             receitas.get('servicos_anexo_iii', 0) + \
                             receitas.get('servicos_anexo_iv', 0) + \
                             receitas.get('servicos_anexo_v', 0)
            impostos['iss'] = total_servicos * self.aliquotas_lr['iss']
        
        # Calcula o total de impostos
        impostos['total'] = sum(valor for chave, valor in impostos.items() if chave != 'total')
        
        return impostos
    
    def comparar_regimes(self, receitas, despesas):
        """
        Compara os três regimes tributários e retorna os resultados
        
        Args:
            receitas: dicionário com valores de receita por tipo
            despesas: dicionário com valores de despesa por tipo
            
        Returns:
            dicionário com os resultados de cada regime
        """
        # Calcula a receita total
        receita_total = sum(receitas.values())
        
        # Calcula os impostos para cada regime
        simples = self.calcular_simples_nacional(receita_total)
        lucro_presumido = self.calcular_lucro_presumido(receitas)
        lucro_real = self.calcular_lucro_real(receitas, despesas)
        
        # Retorna os resultados
        return {
            'simples_nacional': {
                'valor_imposto': simples,
                'aliquota_efetiva': simples / receita_total if receita_total > 0 else 0
            },
            'lucro_presumido': {
                'valor_imposto': lucro_presumido['total'],
                'aliquota_efetiva': lucro_presumido['total'] / receita_total if receita_total > 0 else 0,
                'detalhamento': lucro_presumido
            },
            'lucro_real': {
                'valor_imposto': lucro_real['total'],
                'aliquota_efetiva': lucro_real['total'] / receita_total if receita_total > 0 else 0,
                'detalhamento': lucro_real
            },
            'melhor_opcao': self._determinar_melhor_opcao(simples, lucro_presumido['total'], lucro_real['total'])
        }
    
    def _determinar_melhor_opcao(self, simples, lucro_presumido, lucro_real):
        """
        Determina qual é o melhor regime tributário com base no menor valor de imposto
        """
        valores = {
            'Simples Nacional': simples,
            'Lucro Presumido': lucro_presumido,
            'Lucro Real': lucro_real
        }
        
        melhor_opcao = min(valores.items(), key=lambda x: x[1])
        return {'regime': melhor_opcao[0], 'valor': melhor_opcao[1]}