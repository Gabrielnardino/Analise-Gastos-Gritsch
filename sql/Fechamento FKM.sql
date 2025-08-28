
;WITH MAPEAMENTO AS (
    -- CTE de Mapeamento de Naturezas de Despesa Correta
    SELECT * FROM (VALUES
        ('01.01 - DIREÇÃO', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('01.02 - FREIOS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('01.03 - INJEÇÃO E ALIMENTAÇÃO', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('01.04 - MOTOR', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('01.05 - SUSPENSÃO', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('01.06 - TRANSMISSÃO', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('01.07 - AR-CONDICIONADO', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('02.01 - ADITIVOS E FLUIDOS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('02.02 - ARLA', '02.02 - ARLA'), ('02.03 - FILTROS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('02.04 - ÓLEOS E LUBRIFICANTES', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('03.01 - BATERIA', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('03.02 - LANTERNAS E FARÓIS', '03.02 - LATARIA E PINTURA'), 
        ('03.03 - RASTREAMENTO E MONITORAMENTO DE VEÍCULO', '04.01 - RASTREAMENTO E MONITORAMENTO DE VEÍCULO'),
        ('03.04 - SISTEMA ELÉTRICO', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('04.01 - ALINHAMENTO E BALANCEAMENTO', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('04.02 - PNEUS', '03.05 - RODAS E PNEUS'), 
        ('04.03 - RODAS', '03.05 - RODAS E PNEUS'),
        ('05.01 - ACESSÓRIOS DE VEÍCULOS', '03.04 - ACESSÓRIOS DE VEÍCULOS'), 
        ('05.02 - LATARIA E PINTURA', '03.02 - LATARIA E PINTURA'),
        ('05.03 - LAVAGEM E HIGIENIZAÇÃO', '03.01 - LAVagem'), 
        ('05.04 - VIDROS E PARABRISAS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('05.05 - DEDETIZAÇÃO DE VEÍCULO', '07.07 - DEDETIZAÇÃO DE VEÍCULO'),
        ('06.01 - IPVA (ANUAL)', '07.02 - IPVA (ANUAL)'),
        ('06.02 - IPVA (AQUISIÇÃO DE VEÍCULOS)', '07.06 - IPVA (AQUISIÇÃO DE VEÍCULOS)'),
        ('06.03 - LICENCIAMENTO', '07.03 - LICENCIAMENTO'),
        ('07.01 - SEGURO DE VEÍCULOS (FACULTATIVO)', '06.01 - SEGURO DE VEÍCULOS (FACULTATIVO)'),
        ('07.02 - VMI', '15.11 - REEMBOLSO CLIENTE (AVARIAS)'),
        ('08.01 - ASSISTÊNCIA 24 HORAS', '05.03 - ASSISTÊNCIA 24 HORAS'), 
        ('08.02 - COMBUSTÍVEL', '02.01 - COMBUSTÍVEL'),
        ('08.03 - ESTACIONAMENTO', '08.01 - ESTACIONAMENTO'), 
        ('08.04 - FRETES E CARRETOS', '05.01 - FRETES E CARRETOS'),
        ('08.05 - GUINCHO', '05.03 - ASSISTÊNCIA 24 HORAS'),
        ('08.06 - SERVIÇO DE DESLOCAMENTO', '16.01 - TAXI'),
        ('08.07 - SUBLOCAÇÃO DE VEÍCULOS', '09.01 - SUBCONTRATAÇÃO DE LOCAÇÃO DE VEÍCULOS'), 
        ('03.03 - MANUTENÇÃO DE VEÍCULOS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('09.02 - MÃO DE OBRA - PREVENTIVA', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('03.01 - LAVAGEM', '03.01 - LAVAGEM'),
        ('09.01 - MÃO DE OBRA - CORRETIVA', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('15.03 - TAXAS DIVERSAS', '15.03 - TAXAS DIVERSAS'),
        ('03.06 - MANUTENÇÃO PREVENTIVA', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('03.22 - VIDROS E PARABRISAS', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('03.07 - ADITIVOS E FLUÍDOS', '03.03 - MANUTENÇÃO DE VEÍCULOS'), 
        ('03.10 - BATERIA', '03.03 - MANUTENÇÃO DE VEÍCULOS'),
        ('04.01 - RASTREAMENTO E MONITORAMENTO DE VEÍCULO', '04.01 - RASTREAMENTO E MONITORAMENTO DE VEÍCULO'), 
        ('05.03 - ASSISTÊNCIA 24 HORAS', '05.03 - ASSISTÊNCIA 24 HORAS'),
        ('03.02 - LATARIA E PINTURA', '03.02 - LATARIA E PINTURA'), 
        ('03.04 - ACESSÓRIOS DE VEÍCULOS', '03.04 - ACESSÓRIOS DE VEÍCULOS'),
        ('03.05 - RODAS E PNEUS', '03.05 - RODAS E PNEUS'), 
        ('09.01 - SUBLOCAÇÃO DE VEÍCULOS', '09.01 - SUBCONTRATAÇÃO DE LOCAÇÃO DE VEÍCULOS'),
        ('05.05 - GUINCHO', '05.03 - ASSISTÊNCIA 24 HORAS'), 
        ('05.01 - FRETES E CARRETOS', '05.01 - FRETES E CARRETOS'),
        ('07.06 - IPVA (AQUISIÇÃO DE VEÍCULOS)', '07.06 - IPVA (AQUISIÇÃO DE VEÍCULOS)')

    ) AS t(DescricaoCompleta, NaturezaVinculada)
),

BASE AS (
    -- CTE principal que reúne os dados brutos e utiliza OUTER APPLY para buscar o último movimento de forma segura
    SELECT
        OS.IdNF, 
        NF.NumeroNF, 
        NF.TipoOrdemCompra, 
        OS.OrdemServico, 
        OS.Ocorrencia, 
        OS.OrdemCompra, 
        OS.Placa,
        OS.DescricaoItem, 
        OS.TipoItem, 
        OS.Tipo, 
        NF.TipoNF, 
        OS.IdGrupoDespesa, 
        OS.GrupoDespesa, 
        GP.CodigoCompleto,
        GP.DescricaoCompleta, 
        OS.Quantidade, 
        OS.ValorUnitario, 
        OS.ValorTotal, 
        OS.SituacaoOrdemServico,
        NF.IdUnidadeDeFaturamento, 
        NF.UnidadeDeFaturamento, 
        VC.IdFilialOperacional, 
        VC.FilialOperacional,
        OS.IdVeiculo, 
        VC.SituacaoVeiculo, 
        OS.CriadoPor, 
        OS.DataCriacaoOrdemServico, 
        OS.DataCriacaoOcorrencia,
        NF.DataEmissao, 
        NF.DataEntrada, 
        OS.SituacaoOcorrencia, 
        NF.IdFornecedor, 
        OS.Fornecedor,
        LC.Natureza AS NaturezaFinanceira, 
        NF.DataCriacao, 
        OS.IdOcorrencia, 
        OC.IdContratoComercial,
        CO.UnidadeDeFaturamento AS UnidadeDeFaturamentoContrato, 
        USU.IdUsuario, 
        USU.Nome,
        m.Unidade_de_Origem,
        m.Unidade_de_Destino 
        

    FROM
        dbo.ItensOrdemServico AS OS
        INNER JOIN dbo.NotasFiscais AS NF ON NF.IdNF = OS.IdNF
        INNER JOIN dbo.GruposDespesa AS GP ON GP.IdGrupoDespesas = OS.IdGrupoDespesa
        INNER JOIN dbo.Veiculos AS VC ON VC.Placa = OS.Placa
        INNER JOIN dbo.NaturezasFinanceiras AS LC ON GP.IdNaturezaFinanceira = LC.IdNaturezaFinanceira
        LEFT JOIN dbo.OcorrenciasManutencao AS OC ON OC.IdOcorrencia = OS.IdOcorrencia
        LEFT JOIN dbo.ContratosComerciais AS CO ON CO.IdContratoComercial = OC.IdContratoComercial
        OUTER APPLY (
            SELECT TOP 1 Unidade_de_Origem, Unidade_de_Destino
            FROM dbo.Movimentos
            WHERE Placa = OS.Placa AND Data_da_movimentação <= NF.DataCriacao
            ORDER BY Data_da_movimentação DESC
        ) m
        OUTER APPLY (
            SELECT TOP 1 IdUsuario, Nome
            FROM dbo.Usuarios
            WHERE IdUsuario = OC.IdUsuarioCriacao
        ) AS USU
    WHERE
        NF.DataCriacao BETWEEN '2025-01-01' AND '2025-12-31'
        AND OS.SituacaoOrdemServico <> 'Cancelada'
)

SELECT *
FROM(-- SELECT Final com colunas organizadas e lógicas de negócio aplicadas
    SELECT
        -- Identificadores Principais
        b.IdNF, 
        b.NumeroNF, 
        b.OrdemServico, 
        b.Ocorrencia, 
        b.OrdemCompra, 
        b.Placa, 
        b.IdVeiculo,

        -- Detalhes do Item/Serviço
        b.DescricaoItem, 
        b.TipoItem, 
        b.Tipo, 
        b.TipoOrdemCompra, 
        b.IdGrupoDespesa, 
        b.GrupoDespesa, 
        b.CodigoCompleto,
        b.DescricaoCompleta, 
        b.Quantidade, 
        b.ValorUnitario, 
        b.ValorTotal,

        -- Status e Situações
        b.SituacaoOrdemServico, 
        b.SituacaoOcorrencia, 
        b.SituacaoVeiculo,

        -- Informações de Filial e Unidades
        b.IdUnidadeDeFaturamento, 
        b.UnidadeDeFaturamento, 
        b.IdFilialOperacional, 
        b.FilialOperacional,

        -- Datas Relevantes
        b.DataCriacao, 
        b.DataCriacaoOrdemServico, 
        b.DataCriacaoOcorrencia, 
        b.DataEmissao, 
        b.DataEntrada,

        -- Fornecedor e Contrato
        b.IdFornecedor, 
        b.Fornecedor, 
        b.IdContratoComercial, 
        b.UnidadeDeFaturamentoContrato,

        -- Usuário
        b.CriadoPor, 
        b.IdUsuario, 
        b.Nome,

        -- Natureza Financeira
        b.NaturezaFinanceira,

    -- ========================================================================================================================================
    -- CColuna Para Identificar a regra de Filial Corretamente, abaixo segue todas as regras 
    -- ========================================================================================================================================

    CASE
        -- REGRA 1: Contrato Referencia (maior prioridade).
        WHEN b.IdContratoComercial IS NOT NULL 
            THEN b.UnidadeDeFaturamentoContrato

        -- REGRA 2: Lógica de Movimentação (alta prioridade).
        WHEN b.Unidade_de_Destino IS NOT NULL THEN
            CASE
                -- Sub-regra A: O destino é uma filial real (não genérica).
                WHEN 
                    b.Unidade_de_Destino NOT LIKE '%VENDA%' AND
                    b.Unidade_de_Destino NOT LIKE '%DEFINIR%' AND
                    b.Unidade_de_Destino NOT LIKE '%PARTICULARES%' AND
                    b.Unidade_de_Destino NOT LIKE '%VENDIDOS%'
                THEN b.Unidade_de_Destino
            
                -- Sub-regra B: O destino é genérico, então rateamos pela ORIGEM.
                ELSE
                    CASE
                        WHEN b.Unidade_de_Origem LIKE '%REF%' THEN 'RATEIO - REF'
                        WHEN b.Unidade_de_Origem LIKE '%GRI%' THEN 'RATEIO - GRI'
                        ELSE 'RATEIO GRI/REF' -- Se a origem também for genérica
                    END
            END

        -- REGRA 3: Rateio misto explícito.
        WHEN 
            (b.UnidadeDeFaturamento LIKE '%GRI%' AND b.FilialOperacional LIKE '%REF%') OR
            (b.UnidadeDeFaturamento LIKE '%REF%' AND b.FilialOperacional LIKE '%GRI%')
        THEN 'RATEIO GRI/REF'

        -- REGRA 4: Rateio explícito já definido na Unidade de Faturamento.
        WHEN b.UnidadeDeFaturamento LIKE 'RATEIO%' 
        THEN b.UnidadeDeFaturamento

        -- REGRA 5: Regra para situação do veiculo/ Unidades e Grupos que estao com status de veiculos para venda ou similar
        WHEN 
            b.SituacaoVeiculo IN ('Vendido', 'Disponível para Venda', 'Preparação para Venda') OR
            b.UnidadeDeFaturamento LIKE '%VENDA%' OR
            b.UnidadeDeFaturamento LIKE '%DEFINIR%' OR
            b.UnidadeDeFaturamento LIKE '%PARTICULARES%' OR
            b.UnidadeDeFaturamento LIKE '%VENDIDOS%' OR
            b.FilialOperacional LIKE '%VENDA%' OR
            b.FilialOperacional LIKE '%DEFINIR%' OR
            b.FilialOperacional LIKE '%PARTICULARES%' OR
            b.FilialOperacional LIKE '%VENDIDOS%'
        THEN
            CASE
                WHEN b.UnidadeDeFaturamento LIKE '%REF%' OR b.FilialOperacional LIKE '%REF%' THEN 'RATEIO - REF'
                WHEN b.UnidadeDeFaturamento LIKE '%GRI%' OR b.FilialOperacional LIKE '%GRI%' THEN 'RATEIO - GRI'
                ELSE 'RATEIO GRI/REF' 
            END

        -- REGRA 6 (O PADRÃO): Se nenhuma das regras de exceção acima for atendida, use a Filial Operacional.
        ELSE b.FilialOperacional
    END AS FILIAL,


        -- Lógica para Correção da Natureza da Despesa
        CASE
            -- REGRA 1: Exceção para Pneus e serviços de Recapagem/Recauchutagem
            WHEN m.NaturezaVinculada = '03.05 - RODAS E PNEUS' AND ((UPPER(TRIM(b.TipoItem)) = 'PEÇA' AND UPPER(b.DescricaoItem) LIKE '%PNEU%') OR (UPPER(TRIM(b.TipoItem)) = 'SERVIÇO' AND UPPER(b.DescricaoItem) LIKE '%RECAP%')) THEN '03.05 - RODAS E PNEUS'
            -- REGRA 2: Reclassificação do que não é Pneu/Recapagem
            WHEN m.NaturezaVinculada = '03.05 - RODAS E PNEUS' THEN '03.03 - MANUTENÇÃO DE VEÍCULOS'
            -- REGRA 3: Padrão para todas as outras naturezas
            ELSE m.NaturezaVinculada
        END AS Natureza_Correta

    FROM
        BASE b
    LEFT JOIN
        MAPEAMENTO m ON UPPER(TRIM(b.DescricaoCompleta)) = UPPER(TRIM(m.DescricaoCompleta))
) AS RESULTADO_FINAL;
