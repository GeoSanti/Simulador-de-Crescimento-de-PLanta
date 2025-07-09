O projeto é um simulador do crescimento e plantio de plantas feito em Python. A ideia principal é permitir que o usuário plante espécies reais de diferentes regiões do Brasil e cuide delas diariamente, enfrentando variações de clima e controlando o nível de água. Tudo acontece de forma interativa, com uma interface gráfica feita no CustomTkinter.
O projeto usa SQLite para armazenar as informações. Tem tabelas com as regiões do Brasil, cada uma contendo duas espécies típicas, e uma tabela que guarda as plantas plantadas pelo usuário, incluindo o nome personalizado que ele pode dar para cada planta.
Durante o uso, o usuário pode escolher entre plantar uma nova espécie ou visualizar as plantas que ele já tem. Depois de plantar, o jogo simula o passar dos dias: cada dia pode ter um clima diferente (normal, quente e seco, frio ou chuvoso), e o usuário precisa regar a planta corretamente. Se deixar ela sem água por 3 dias ou regar demais, a planta morre. As plantas evoluem ao longo dos dias, passando pelos estados de semente, brotando, crescendo e adulta.

O projeto utiliza:
Python 3
SQLite (Banco de dados)
CustomTkinter (interface gráfica)
SQLAlchemy (ORM)


