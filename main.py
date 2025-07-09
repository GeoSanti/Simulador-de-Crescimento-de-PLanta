# Importa as libs necessárias para a interface e banco de dados
from customtkinter import CTk, CTkButton, CTkLabel, CTkEntry, CTkFrame, set_appearance_mode, set_default_color_theme
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import random

# Define o tema escuro com botões verdes pra interface
set_appearance_mode("dark")
set_default_color_theme("green")

# Configuração do banco SQLite usando SQLAlchemy
Base = declarative_base()
engine = create_engine('sqlite:///plantas.db')
Session = sessionmaker(bind=engine)
session = Session()

# Tabela Regiao que armazena as regiões e mantém a relação com as plantas daquela região
class Regiao(Base):
    __tablename__ = 'regiao'
    id_regiao = Column(Integer, primary_key=True)
    nome_regiao = Column(String, nullable=False)
    plantas = relationship('Planta', back_populates='regiao')

# Tabela Planta que guarda as características das plantas, incluindo sua região e água ideal
class Planta(Base):
    __tablename__ = 'plantas'
    id_planta = Column(Integer, primary_key=True)
    id_regiao = Column(Integer, ForeignKey('regiao.id_regiao'))
    nome_planta = Column(String, nullable=False)
    especie = Column(String, nullable=False)
    agua_ideal = Column(Integer, nullable=False)
    regiao = relationship('Regiao', back_populates='plantas')

# Tabela que representa as plantas cultivadas pelo usuário, com nome, estado e saúde
class PlantaUsuario(Base):
    __tablename__ = 'plantas_usuario'
    id_planta_usuario = Column(Integer, primary_key=True)
    id_planta = Column(Integer, ForeignKey('plantas.id_planta'))
    nome_planta = Column(String, nullable=False)
    especie = Column(String, nullable=False)
    estado_crescimento = Column(String, nullable=False)
    saude = Column(String, nullable=False)
    nivel_agua = Column(Integer, nullable=False)
    dias_sem_agua = Column(Integer, default=0)
    planta = relationship('Planta')

# Cria as tabelas no banco se não existirem
Base.metadata.create_all(engine)

# Insere dados iniciais no banco se ele estiver vazio, como as regiões e plantas padrões
def inserir_dados_iniciais():
    if session.query(Regiao).count() == 0:
        regioes = [Regiao(id_regiao=i+1, nome_regiao=r) for i, r in enumerate(['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'])]
        session.add_all(regioes)
        session.commit()
    if session.query(Planta).count() == 0:
        plantas = [
            Planta(id_planta=1, id_regiao=1, nome_planta='Açaí', especie='Euterpe oleracea', agua_ideal=300),
            Planta(id_planta=2, id_regiao=1, nome_planta='Bacaba', especie='Oenocarpus bacaba', agua_ideal=300),
            Planta(id_planta=3, id_regiao=2, nome_planta='Mandacaru', especie='Cereus jamacaru', agua_ideal=200),
            Planta(id_planta=4, id_regiao=2, nome_planta='Xique-Xique', especie='Pilosocereus gounellei', agua_ideal=150),
            Planta(id_planta=5, id_regiao=3, nome_planta='Ipê', especie='Handroanthus serratifolius', agua_ideal=400),
            Planta(id_planta=6, id_regiao=3, nome_planta="Pau-d'Arco", especie='Tabebuia avellanedae', agua_ideal=400),
            Planta(id_planta=7, id_regiao=4, nome_planta='Pau-brasil', especie='Paubrasilia echinata', agua_ideal=350),
            Planta(id_planta=8, id_regiao=4, nome_planta='Ipê-amarelo', especie='Handroanthus albus', agua_ideal=350),
            Planta(id_planta=9, id_regiao=5, nome_planta='Erva-mate', especie='Ilex paraguariensis', agua_ideal=250),
            Planta(id_planta=10, id_regiao=5, nome_planta='Araucária', especie='Araucaria angustifolia', agua_ideal=300)
        ]
        session.add_all(plantas)
        session.commit()

inserir_dados_iniciais()

# Função que busca todas as regiões cadastradas no banco e retorna como lista
def buscar_regioes():
    return session.query(Regiao).all()

# Função que busca todas as plantas que pertencem a uma região específica
def buscar_plantas_por_regiao(id_regiao):
    return session.query(Planta).filter_by(id_regiao=id_regiao).all()

# Cria uma nova planta associada ao usuário, com nome customizado ou o padrão da planta
def criar_planta_usuario(id_planta, nome_customizado):
    planta = session.query(Planta).get(id_planta)
    nova_planta = PlantaUsuario(
        id_planta=planta.id_planta,
        nome_planta=nome_customizado or planta.nome_planta,  # Usa o nome passado ou o padrão
        especie=planta.especie,
        estado_crescimento='semente',  # Estado inicial da planta
        saude='BEM',                   # Começa saudável
        nivel_agua=0,
        dias_sem_agua=0
    )
    session.add(nova_planta)
    session.commit()
    return nova_planta

# Retorna todas as plantas do usuário para exibir ou manipular
def listar_plantas_usuario():
    return session.query(PlantaUsuario).all()

# Avalia a saúde da planta conforme água e dias sem rega
def avaliar_saude(pu):
    ideal = pu.planta.agua_ideal
    # Se ficar 3 dias ou mais sem água, planta morre
    if pu.dias_sem_agua >= 3:
        pu.estado_crescimento = 'morta'
        pu.saude = 'RUIM'
    # Se regar com o dobro ou mais da água ideal, planta também morre
    elif pu.nivel_agua >= ideal * 2:
        pu.estado_crescimento = 'morta'
        pu.saude = 'RUIM'
    else:
        margem = int(ideal * 0.1)  # Tolerância de 10% pra água
        # Se a quantidade está dentro da margem, saúde fica boa
        if abs(pu.nivel_agua - ideal) <= margem:
            pu.saude = 'BEM'
        else:
            pu.saude = 'RUIM'
    session.commit()

# Sorteia o clima do dia e quantos dias esse clima vai durar
def proximo_clima():
    climas = ['Normal', 'Quente e Seco', 'Frio', 'Chuvoso']
    pesos = [70, 10, 10, 10]  # Probabilidades: normal mais comum
    clima = random.choices(climas, weights=pesos, k=1)[0]
    dias = random.randint(1, 5)  # Duração do clima varia entre 1 e 5 dias
    return clima, dias

# Função que gerencia o ciclo de dias da planta na interface gráfica
def ciclo_dias(pu, frame):
    dias_totais = 0
    clima_atual, dias_clima = proximo_clima()

    # Avança um dia na simulação, atualizando estados e exibindo info
    def proximo_dia():
        nonlocal dias_totais, clima_atual, dias_clima

        avaliar_saude(pu)
        if pu.estado_crescimento == 'morta':
            status_label.configure(text=f"Sua planta morreu! Estado final: {pu.estado_crescimento}", text_color="red")
            return

        clima_msg = f"Clima: {clima_atual} ({dias_clima} dias restantes)\n"
        # Se estiver chuvoso, planta recebe água automaticamente
        if clima_atual == 'Chuvoso':
            pu.nivel_agua = pu.planta.agua_ideal
            pu.saude = 'BEM'
            pu.dias_sem_agua = 0
            clima_msg += "Choveu! A planta foi regada automaticamente.\n"
        elif clima_atual == 'Quente e Seco':
            clima_msg += "Está seco, precisa de 20% a mais de água.\n"
        elif clima_atual == 'Frio':
            clima_msg += "Está frio, proteja sua planta.\n"

        # Atualiza o texto com o status da planta
        status_label.configure(text=f"{clima_msg}\nNome: {pu.nome_planta} | Espécie: {pu.especie}\n"
                                    f"Estado: {pu.estado_crescimento} | Saúde: {pu.saude}\n"
                                    f"Água atual: {pu.nivel_agua} mL | Dias sem água: {pu.dias_sem_agua}")

        dias_totais += 1
        dias_clima -= 1

        # Altera o estado da planta conforme os dias vão passando
        if dias_totais == 5:
            pu.estado_crescimento = 'brotando'
        elif dias_totais == 10:
            pu.estado_crescimento = 'crescendo'
        elif dias_totais == 15:
            pu.estado_crescimento = 'adulta'

        pu.dias_sem_agua += 1
        session.commit()

        # Se o clima atual acabou, sorteia um novo
        if dias_clima == 0:
            clima_atual, dias_clima = proximo_clima()

    # Função ativada quando o usuário rega a planta, atualizando os valores
    def regar():
        try:
            qtd = int(agua_entry.get())
            pu.nivel_agua = qtd
            pu.dias_sem_agua = 0
            session.commit()
            proximo_dia()
        except:
            status_label.configure(text="⚠️ Insira um valor numérico pra água.", text_color="orange")

    # Elementos gráficos do ciclo: label, entrada de texto e botões
    CTkLabel(frame, text="Digite a quantidade de água (mL):").pack(pady=5)
    agua_entry = CTkEntry(frame)
    agua_entry.pack(pady=5)
    CTkButton(frame, text="Regar", command=regar).pack(pady=5)
    CTkButton(frame, text="Passar o Dia", command=proximo_dia).pack(pady=5)
    status_label = CTkLabel(frame, text="")
    status_label.pack(pady=10)

    proximo_dia()

# Classe principal que monta a interface usando CustomTkinter
class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Plantas")
        self.geometry("500x500")
        self.menu_inicial()

    # Limpa todos os widgets da janela para trocar de tela
    def limpar(self):
        for widget in self.winfo_children():
            widget.destroy()

    # Tela inicial perguntando se usuário quer iniciar o programa
    def menu_inicial(self):
        self.limpar()
        CTkLabel(self, text="Deseja iniciar o programa?").pack(pady=10)
        CTkButton(self, text="Iniciar", command=self.menu_principal).pack(pady=5)
        CTkButton(self, text="Sair", command=self.destroy).pack(pady=5)

    # Menu principal com opções pra plantar ou ver plantas do usuário
    def menu_principal(self):
        self.limpar()
        CTkButton(self, text="Plantar nova planta", command=self.plantar_view).pack(pady=5)
        CTkButton(self, text="Minhas plantas", command=self.minhas_plantas_view).pack(pady=5)

    # Permite escolher a região onde vai plantar
    def plantar_view(self):
        self.limpar()
        regioes = buscar_regioes()
        for r in regioes:
            CTkButton(self, text=r.nome_regiao, command=lambda rid=r.id_regiao: self.listar_plantas_view(rid)).pack(pady=2)
        CTkButton(self, text="Voltar", command=self.menu_principal).pack(pady=5)

    # Lista as plantas disponíveis na região escolhida
    def listar_plantas_view(self, id_regiao):
        self.limpar()
        plantas = buscar_plantas_por_regiao(id_regiao)
        for p in plantas:
            CTkButton(self, text=f"{p.nome_planta} ({p.especie}) - {p.agua_ideal} mL",
                      command=lambda pid=p.id_planta: self.definir_nome(pid)).pack(pady=2)
        CTkButton(self, text="Voltar", command=self.plantar_view).pack(pady=5)

    # Solicita ao usuário um nome personalizado pra planta que vai criar
    def definir_nome(self, id_planta):
        self.limpar()
        CTkLabel(self, text="Digite um nome pra sua planta:").pack(pady=5)
        nome_entry = CTkEntry(self)
        nome_entry.pack(pady=5)

        def confirmar():
            planta = criar_planta_usuario(id_planta, nome_entry.get())
            self.iniciar_ciclo(planta)

        CTkButton(self, text="Confirmar", command=confirmar).pack(pady=5)

    # Exibe a lista de plantas que o usuário já tem plantado
    def minhas_plantas_view(self):
        self.limpar()
        plantas = listar_plantas_usuario()
        if not plantas:
            CTkLabel(self, text="Você não tem nenhuma planta.").pack(pady=10)
        for pu in plantas:
            CTkButton(self, text=f"{pu.nome_planta} ({pu.especie}) - Estado: {pu.estado_crescimento}",
                      command=lambda p=pu: self.iniciar_ciclo(p)).pack(pady=2)
        CTkButton(self, text="Voltar", command=self.menu_principal).pack(pady=5)

    # Começa o ciclo diário da planta selecionada
    def iniciar_ciclo(self, planta_usuario):
        self.limpar()
        ciclo_dias(planta_usuario, self)

# Roda o programa, abrindo a janela principal
if __name__ == '__main__':
    app = App()
    app.mainloop()
