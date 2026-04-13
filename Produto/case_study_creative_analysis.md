# SkiWell Sports: criative read of the case

## Tese central
A SkiWell **nao tem um problema de procura**. Tambem **nao tem um problema de produto**. O que a empresa tem e um problema de **friccao operacional escondida**, sobretudo em shipping e configuracao de servico, que aparece em certos paises e se disfarca de problema geografico.

Em linguagem de apresentacao:

> A SkiWell nao esta a perder dinheiro no topo da montanha. Esta a perde-lo na descida.

## Resposta curta ao caso
- **Nao recomendaria fechar nenhuma geografia** neste momento.
- **Recomendaria uma reestruturacao cirurgica** em 4 mercados: `China`, `Canada`, `Andorra` e `Switzerland`.
- O racional e simples:
  - todas as regioes continuam lucrativas;
  - todas crescem entre 2020 e 2025;
  - a estrutura de margem antes de shipping e quase igual entre mercados;
  - o leak esta concentrado em poucos paises, nao em geografias inteiras.

## 1. O insight mais importante: o problema nao e demanda, e "logistics tax"

### O que os dados dizem
- A margem antes de shipping esta praticamente alinhada em todos os paises, perto de `45%`.
- A margem final cai nos paises com maior `shipping ratio`.
- A correlacao entre margem e shipping ao nivel de pais e quase perfeita: `-0.997`.
- A correlacao entre margem e `has_shipping_rate` e `avg_delivery_days` tambem e quase perfeita: `-0.997` e `-0.998`.

### Traducao executiva
A SkiWell cobra bem. Produz bem. O problema acontece **depois da fabrica e antes do cliente**.

### Exemplos fortes
- `China`: margem final `41.2%`, mas margem antes de shipping `44.9%`; `ship_pct = 3.68%`
- `Japan`: margem final `44.2%`; `ship_pct = 0.89%`
- `South Korea`: margem final `44.2%`; `ship_pct = 0.92%`
- `Canada`: margem final `41.4%`; `ship_pct = 3.36%`
- `USA`: margem final `42.6%`; `ship_pct = 2.50%`

### Conclusao
O que parece ser um problema de geografia e, na verdade, um problema de **ultima milha, cross-border fulfillment e intensidade de expedicao**.

## 2. O insight escondido: os paises "piores" sao quase clones de mix dos melhores

Se o portefolio fosse diferente, ainda havia espaco para dizer que o problema vinha de produto. Mas nao e o caso.

### Prova
Os diferencas de mix por categoria entre os paises problemáticos e os seus melhores peers sao minimas:

- `China vs Japan`: diferenca total de mix de apenas `0.21 p.p.`
- `China vs South Korea`: `0.37 p.p.`
- `Canada vs USA`: `0.80 p.p.`
- `Switzerland vs Italy`: `1.71 p.p.`
- `Andorra vs France`: `2.02 p.p.`

### Leitura
Isto significa:
- o cliente compra essencialmente o mesmo tipo de coisas;
- o portefolio nao explica a quebra;
- o problema nao e "vender os produtos errados";
- o problema e **servir os produtos certos de forma demasiado cara**.

### Frase de slide
> Same basket, different burden.

## 3. O negocio nao esta em declinio. Esta a crescer com fugas de margem

### CAGR de lucro 2020-2025
- `Asia`: `17.4%`
- `Europe`: `18.5%`
- `North America`: `19.1%`

### Leitura
Isto e importante porque desmonta a tentacao de uma recomendacao radical:

> Nao ha evidencia de colapso economico que justifique encerrar uma geografia inteira.

Fechar um mercado nesta fase seria destruir opcionalidade de crescimento para corrigir um problema que parece, sobretudo, operacional.

## 4. A empresa vive de poucos bolsos de lucro

### Arquitetura do profit pool
- `Technical equipment` = `21.3%` das encomendas, mas `55.4%` do lucro
- `Clothing` = `35.7%` das encomendas, `31.1%` do lucro
- `Accessories` = `43.0%` das encomendas, mas so `13.5%` do lucro

### Subcategorias mais importantes
- `Skis` = `28.5%` do lucro total
- `Boots` = `21.1%`
- `Suits` = `9.6%`

As 3 juntas representam:
- `21.4%` das encomendas
- `59.3%` do lucro

### Insight criativo
A SkiWell parece uma empresa diversificada, mas na pratica funciona como um negocio com um **motor central muito concentrado**.

### Implicacao
Se o shipping penaliza os mercados onde `Technical equipment` e forte, o dano e desproporcional. Ou seja:

> O problema logistico nao atinge o volume. Atinge precisamente o coracao do profit pool.

## 5. A geografia certa para atacar nao e a regiao. E o cluster de paises com "frio logistico"

### Watchlist natural
Os 4 paises com maior leak operacional sao:
- `China`
- `Canada`
- `Andorra`
- `Switzerland`

### Porque estes 4?
- Têm margens abaixo dos melhores peers da regiao
- Têm `shipping ratio` elevado
- Têm maior taxa de expedicao
- Têm maior tempo medio de entrega
- Aparecem no topo das anomalias do sistema ML

### Opportunity sizing
Se estes mercados convergissem para o **melhor shipping ratio da sua regiao**, o uplift potencial de lucro seria aproximadamente:

- `China`: `+41.3k`
- `Canada`: `+27.8k`
- `Andorra`: `+21.3k`
- `Switzerland`: `+20.3k`

Total top 4: `~110.7k`

Se convergissem para a **melhor margem da regiao**, o uplift total da empresa seria `~156.3k`.

### Traducao executiva
O caminho certo nao e excluir uma geografia.
O caminho certo e:

> operar uma "targeted margin rescue" nos pontos de fuga.

## 6. A Asia esconde uma historia de duas velocidades

No agregado, a `Asia` parece forte. Mas isso esconde duas dinamicas diferentes:

- `Japan` cresce e mantém margem alta
- `South Korea` mantém margem alta, mas praticamente estagna em lucro entre 2020 e 2025
- `China` cresce muito, mas com margem estruturalmente inferior

### Leitura
A Asia nao e um bloco unico:
- `Japan` = mercado eficiente e robusto
- `South Korea` = mercado maduro, rentavel, mas com pouco impulso
- `China` = mercado de crescimento, mas com grande friccao operacional

### Implicacao
Nao faz sentido tratar "Asia" como um problema ou como uma oportunidade unica. A recomendacao tem de ser diferenciada por pais.

## 7. Sazonalidade existe, mas nao explica a diferenca entre geografias

### O que se observa
- `Q1` e o trimestre mais forte em todas as regioes, com cerca de `29%` das encomendas
- `Q4` vem logo a seguir, com `27%-28%`
- `Q2` e `Q3` sao mais leves, mas o perfil sazonal e muito parecido entre regioes

### Conclusao
A sazonalidade e real, mas **nao explica porque e que umas geografias têm menos margem do que outras**.

Ela explica o ritmo do negocio, nao o leak de performance.

## 8. O sistema ML confirma a mesma historia por outra via

Foi criado um sistema de ML em [group1_ml_insight_system.py](/Users/miguelferreira/Desktop/PwCGit/Produto/group1_ml_insight_system.py:1) com:
- `Random Forest` para margem estrutural
- `Random Forest` para shipping ratio
- `KMeans` para clusters
- `Isolation Forest` para anomalias

### Sinais encontrados
- Modelo de shipping com `R2 = 0.921`
- Drivers principais: `has_shipping_rate`, `avg_delivery_days`, `Subcategory`
- `China` concentra `37.2%` de todas as anomalias
- O cluster mais arriscado e `Pressao logistica`

### O que isto acrescenta
O ML nao substitui a analise. Mas ajuda a provar que:
- os segmentos que saem do padrao saem quase sempre pela via logistica;
- o problema esta concentrado;
- a empresa pode priorizar intervencoes com bastante precisao.

## 9. Recomendacao final para o Grupo 1

### Diagnostico
- A rentabilidade da empresa **nao esta a colapsar**; esta a crescer.
- O gap entre geografias existe, mas nao nasce de procura fraca nem de mix errado.
- O principal constrangimento e **cost-to-serve**, visivel em shipping, taxa de expedicao e tempo de entrega.

### Principais constrangimentos
- `China`: forte crescimento, mas margin leakage estrutural via shipping
- `Canada`: mercado relevante, mas com penalty logistico consistente face aos EUA
- `Andorra` e `Switzerland`: pequenos mercados com friccao operacional alta para o nivel de margem gerado
- Forte dependencia do lucro em `Technical equipment`, especialmente `Skis` e `Boots`

### Recomendacoes
1. **Nao encerrar geografias agora**
   - Todas sao lucrativas
   - Todas mantem escala ou potencial
   - O problema e corrigivel sem destruir crescimento

2. **Lancar um programa de margin rescue nos 4 mercados criticos**
   - Renegociar contratos de shipping
   - Rever rede de fulfillment
   - Redesenhar politica de expedicao e thresholds
   - Reduzir expedicoes caras em SKUs de menor lucro

3. **Proteger o profit pool**
   - Dar prioridade logistica e comercial a `Skis`, `Boots` e `Suits`
   - Garantir disponibilidade, SLA e disciplina de custo nestas linhas

4. **Racionalizar a cauda longa**
   - `Accessories` ocupa muito volume e pouco lucro
   - Deve ser usada para bundle, cross-sell ou retenção, nao como motor isolado de rentabilidade

5. **Gerir paises por arquétipo**
   - Mercados de crescimento com friccao: `China`
   - Mercados robustos: `Japan`, `France`, `Italy`
   - Mercados com friccao e escala relevante: `Canada`
   - Mercados pequenos com custo elevado: `Andorra`, `Switzerland`

## 10. Storyline criativa para 5 slides

### Slide 1
**A SkiWell nao tem um problema de montanha. Tem um problema de descida.**
- Receita e lucro continuam a crescer
- O problema nao e falta de procura
- O gap de rentabilidade nasce na operacao

### Slide 2
**Same basket, different burden**
- Comparar pares de paises com mix quase identico
- Mostrar que o shipping ratio explica a diferenca de margem
- Exemplo: `China vs Japan` e `Canada vs USA`

### Slide 3
**Where profit really lives**
- Profit pool por categoria e subcategoria
- Mostrar dependencia em `Technical equipment`
- Mostrar que shipping afeta precisamente o core do lucro

### Slide 4
**The cold spots**
- Watchlist: `China`, `Canada`, `Andorra`, `Switzerland`
- Quantificar uplift potencial
- Mostrar que anomalias estao concentradas, nao dispersas

### Slide 5
**Do not exit. Rewire.**
- Nao encerrar geografias
- Corrigir rede logistica e cost-to-serve
- Priorizar IA e analytics para previsão, inventory e route optimization

## Fecho
Se tivesse de resumir a resolucao do case numa unica frase:

> A SkiWell nao precisa de cortar paises. Precisa de tirar gelo da sua cadeia de valor.
