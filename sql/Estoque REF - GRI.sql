select 
DataAtualizacaoDados,              
IdVeiculo,                                  
Chassi,                                     
Placa,                                    
RENAVAM,                                
IdCorVeiculo,                               
Cor,                                        
AnoModelo,                                  
AnoFabricacao,
IdModelo,
Modelo,
IdMontadora,
Montadora,
IdGrupoVeiculo,
GrupoVeiculo,
IdFilial,
Filial,
FilialOperacional,
SituacaoFinanceira,
ComSeguroVigente,
Proprietario

from veiculos
where FilialOperacional LIKE '%GRITSCH%'
OR FilialOperacional LIKE '%REF%'
order by FilialOperacional, Modelo