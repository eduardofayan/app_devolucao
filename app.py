from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from PIL import Image
from src.database import DevolucaoDatabase
from src.exporter import exportar_mes
from src.resource_path import resource_path
import customtkinter as ctk

# CONFIGURAÇÕES DO CUSTOMTKINTER
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Função principal da aplicação
class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        # CONFIGURAÇÕES DA JANELA
        self.title("CONTROLE DE DEVOLUÇÕES")
        try:
            self.iconbitmap(resource_path("assets/icon.ico"))
        except Exception:
            pass

        # Abre maximizado
        self.after(100,lambda: self.state("zoomed"))

        # Impede janela muito pequena
        self.minsize(1100,650)

        # BANCO
        self.db = DevolucaoDatabase()

        # VARIÁVEIS
        self.conferente = ""
        self.logo_login = None
        self.logo_home = None

        # TELA INICIAL
        self.tela_login()

    # UTILITÁRIOS
    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()
    def voltar_login(self):
        resposta = messagebox.askyesno(
            "Tela Inicial",
            "Deseja voltar para a tela inicial?"
        )

        if not resposta:
            return

        self.conferente = ""

        self.tela_login()
    @staticmethod
    def converter_valor(valor):
        """
        Converte valores informados pelo usuário para float.

        Aceita:
        5000
        5000,00
        5.000,00
        5000.00
        R$ 5.000,00
        """

        valor = str(valor).strip()

        valor = (
            valor
            .replace("R$", "")
            .replace(" ", "")
        )

        if not valor:
            raise ValueError("Valor vazio.")

        try:
            # Formato brasileiro:
            # 5.000,00
            # 5000,00
            if "," in valor:

                valor = valor.replace(".", "")
                valor = valor.replace(",", ".")

            return float(valor)

        except (ValueError, TypeError):

            raise ValueError(
                "Informe um valor válido."
            )
    @staticmethod
    def formatar_moeda(valor):

        valor = float(valor)

        texto = f"{valor:,.2f}"

        texto = (
            texto
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return f"R$ {texto}"

    # Função para validar se o valor contém apenas números.
    @staticmethod
    def validar_somente_numeros(valor):

        if valor == "":
            return True

        return valor.isdigit()

    # Função Tela de Login
    def tela_login(self):
        self.limpar_tela()

        # FRAME PRINCIPAL
        frame = ctk.CTkFrame(self)

        frame.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=20
        )

        # LOGO
        try:
            imagem = Image.open(resource_path("assets/logo.png"))

            self.logo_login = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(300, 100)
            )

            ctk.CTkLabel(
                frame,
                text="",
                image=self.logo_login
            ).pack(
                pady=(20, 5)
            )
        except Exception as erro:
            print(f"Não foi possível carregar a logo: {erro}")

        # TÍTULO
        ctk.CTkLabel(
            frame,
            text="CONTROLE DE DEVOLUÇÕES",
            font=(
                "Arial",
                30,
                "bold"
            )
        ).pack(
            pady=30,
            expand=True
        )

        # NOME CONFERENTE
        self.nome_entry = ctk.CTkEntry(
            frame,
            width=400,
            height=45,
            placeholder_text="Nome do Conferente"
        )

        self.nome_entry.pack(
            pady=15
        )

        # ENTER inicia sessão
        self.nome_entry.bind(
            "<Return>",
            lambda event:
            self.iniciar_sessao()
        )

        # BOTÃO INICIAR
        ctk.CTkButton(
            frame,
            text="INICIAR",
            width=200,
            height=45,
            font=(
                "Arial",
                15,
                "bold"
            ),
            command=self.iniciar_sessao
        ).pack(
            pady=20
        )

        # RODAPÉ
        ctk.CTkLabel(
            frame,
            text=(
                "Jaguar Indústria e Comércio de Plásticos S.A. "
                "- Desenvolvedor Eduardo Fayan"
            )
        ).pack(
            side="bottom",
            pady=10
        )

        self.after(
            200,
            self.nome_entry.focus_force
        )

    # INICIAR SESSÃO
    def iniciar_sessao(self):
        nome = (
            self.nome_entry
            .get()
            .strip()
        )

        if not nome:
            messagebox.showwarning(
                "Aviso",
                "Informe o nome do Conferente."
            )

            return

        self.conferente = nome

        self.tela_principal()

    #Função Tela Principal
    def tela_principal(self):

        self.limpar_tela()

        # TOPO
        topo = ctk.CTkFrame(self)
        topo.pack(fill="x",padx=10,pady=(10, 5))

        # VOLTAR
        ctk.CTkButton(
            topo,
            text="Tela Inicial",
            width=120,
            command=self.voltar_login
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        # TÍTULO
        frame_titulo_topo = ctk.CTkFrame(topo,fg_color="transparent")
        frame_titulo_topo.pack(side="left",expand=True)

        ctk.CTkLabel(
            frame_titulo_topo,
            text="CONTROLE DE DEVOLUÇÕES",
            font=(
                "Arial",
                24,
                "bold"
            )
        ).pack()

        ctk.CTkLabel(
            frame_titulo_topo,
            text=(
                f"Conferente: "
                f"{self.conferente}"
            ),
            font=(
                "Arial",
                15
            )
        ).pack(
            pady=3
        )

        # EXPORTAR
        ctk.CTkButton(
            topo,
            text="Exportar Devoluções",
            width=160,
            command=self.tela_exportacao
        ).pack(
            side="right",
            padx=10,
            pady=10
        )

        # CABEÇALHO DA LISTAGEM
        frame_titulo = ctk.CTkFrame(self)
        frame_titulo.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            frame_titulo,
            text="DEVOLUÇÕES EM ABERTO",
            font=(
                "Arial",
                20,
                "bold"
            )
        ).pack(
            side="left",
            padx=15,
            pady=12
        )

        self.lbl_total_abertas = ctk.CTkLabel(
            frame_titulo,
            text="Total em aberto: 0",
            font=(
                "Arial",
                15,
                "bold"
            )
        )

        self.lbl_total_abertas.pack(
            side="right",
            padx=20
        )

        # TABELA
        frame_tabela = ctk.CTkFrame(self)
        frame_tabela.pack(expand=True, fill="both", padx=10, pady=5)

        colunas = (
            "ID",
            "OC",
            "CLIENTE",
            "PLACA",
            "MOTIVO",
            "VALOR",
            "INICIO",
            "CONFERENTE"
        )

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )

        # CABEÇALHOS
        nomes_colunas = {
            "ID": "ID",
            "OC": "NÚMERO OCS",
            "CLIENTE": "CLIENTE",
            "PLACA": "PLACA",
            "MOTIVO": "MOTIVO",
            "VALOR": "VALOR NF",
            "INICIO": "INÍCIO",
            "CONFERENTE": "ABERTO POR"
        }

        for coluna in colunas:
            self.tree.heading(coluna, text=nomes_colunas[coluna])

        # TAMANHOS
        self.tree.column(
            "ID",
            width=60,
            minwidth=50,
            anchor="center",
            stretch=False
        )

        self.tree.column(
            "OC",
            width=300,
            minwidth=180,
            anchor="center"
        )

        self.tree.column(
            "CLIENTE",
            width=250,
            minwidth=150
        )

        self.tree.column(
            "PLACA",
            width=120,
            minwidth=100,
            anchor="center"
        )

        self.tree.column(
            "MOTIVO",
            width=300,
            minwidth=180
        )

        self.tree.column(
            "VALOR",
            width=140,
            minwidth=120,
            anchor="e"
        )

        self.tree.column(
            "INICIO",
            width=170,
            minwidth=160,
            anchor="center"
        )

        self.tree.column(
            "CONFERENTE",
            width=180,
            minwidth=150
        )

        # SCROLLBAR
        scrollbar_vertical = ttk.Scrollbar(
            frame_tabela,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar_horizontal = ttk.Scrollbar(
            frame_tabela,
            orient="horizontal",
            command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set
        )
        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        scrollbar_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )
        scrollbar_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )
        frame_tabela.grid_rowconfigure(
            0,
            weight=1
        )

        frame_tabela.grid_columnconfigure(
            0,
            weight=1
        )

        # Duplo clique não finaliza automaticamente.
        # Apenas mantém o item selecionado.

        # BOTÕES
        frame_botoes = ctk.CTkFrame(self)
        frame_botoes.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ATUALIZAR
        ctk.CTkButton(
            frame_botoes,
            text="ATUALIZAR",
            width=120,
            command=self.carregar_abertas
        ).pack(
            side="left",
            padx=5,
            pady=8
        )

        """ # EXPORTAR
        ctk.CTkButton(
            frame_botoes,
            text="EXPORTAR",
            width=120,
            command=self.tela_exportacao
        ).pack(
            side="left",
            padx=5,
            pady=8
        ) """

        # FINALIZAR
        ctk.CTkButton(
            frame_botoes,
            text="FINALIZAR DEVOLUÇÃO",
            width=200,
            height=40,
            fg_color="#C0392B",
            hover_color="#922B21",
            font=(
                "Arial",
                14,
                "bold"
            ),
            command=self.finalizar_devolucao
        ).pack(
            side="right",
            padx=5,
            pady=8
        )

        # NOVA DEVOLUÇÃO
        ctk.CTkButton(
            frame_botoes,
            text="+ INICIAR DEVOLUÇÃO",
            width=200,
            height=40,
            fg_color="#138D75",
            hover_color="#117864",
            font=(
                "Arial",
                14,
                "bold"
            ),
            command=self.abrir_nova_devolucao
        ).pack(
            side="right",
            padx=5,
            pady=8
        )

        # RODAPÉ
        ctk.CTkLabel(
            self,
            text=(
                "Jaguar Indústria e Comércio de Plásticos S.A. "
                "- Desenvolvedor Eduardo Fayan"
            )
        ).pack(
            pady=5
        )

        # CARREGAR BANCO
        self.carregar_abertas()

    # Função para carregar as devoluções abertas
    def carregar_abertas(self):

        # LIMPAR TABELA
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            registros = self.db.listar_abertas()
        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Falha ao consultar as devoluções:\n\n{erro}"
            )
            return

        # PREENCHER TABELA
        for row in registros:

            # DATA
            try:
                inicio = datetime.strptime(row["data_hora_inicio"],"%Y-%m-%d %H:%M:%S")
                inicio_formatado = (inicio.strftime("%d/%m/%Y %H:%M:%S"))
            except Exception:
                inicio_formatado = (row["data_hora_inicio"])

            # VALOR
            try:
                valor = self.formatar_moeda(row["valor_nf"])
            except Exception:
                valor = (str(row["valor_nf"]))

            # INSERIR
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["numero_oc"],
                    row["clientes"],
                    row["placa_caminhao"],
                    row["motivo"],
                    valor,
                    inicio_formatado,
                    row["conferente_abertura"]
                )
            )

        # TOTAL
        self.lbl_total_abertas.configure(
            text=(
                f"Total em aberto: "
                f"{len(registros)}"
            )
        )

    # Função para abrir a janela de nova devolução
    def abrir_nova_devolucao(self):

        janela = ctk.CTkToplevel(self)

        janela.title(
            "Iniciar Nova Devolução"
        )

        janela.state("zoomed")

        lista_ocs = []

        # TÍTULO

        ctk.CTkLabel(
            janela,
            text="NOVA DEVOLUÇÃO",
            font=(
                "Arial",
                24,
                "bold"
            )
        ).pack(
            pady=(20, 10)
        )

        # FORMULÁRIO

        frame_form = ctk.CTkFrame(
            janela
        )

        frame_form.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        validacao_oc = (
            janela.register(
                self.validar_somente_numeros
            )
        )

        # ÁREA DAS OCs

        frame_oc = ctk.CTkFrame(
            frame_form,
            fg_color="transparent"
        )

        frame_oc.pack(
            fill="x",
            padx=30,
            pady=(15, 5),
            anchor="w"
        )
        # TÍTULO

        ctk.CTkLabel(
            frame_oc,
            text="Número da OC",
            font=("Arial", 14, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            frame_oc,
            text="Cliente",
            font=("Arial", 14, "bold")
        ).grid(
            row=0,
            column=1,
            padx=(10, 0),
            sticky="w"
        )

        ctk.CTkLabel(
            frame_oc,
            text="Valor NF",
            font=("Arial", 14, "bold")
        ).grid(
            row=0,
            column=2,
            padx=(10, 0),
            sticky="w"
        )
        # INPUT

        entry_oc = ctk.CTkEntry(
            frame_oc,
            width=250,
            height=40,
            placeholder_text="Número da OC",
            validate="key",
            validatecommand=(
                validacao_oc,
                "%P"
            )
        )

        entry_oc.grid(
            row=1,
            column=0,
            padx=(0, 10),
            pady=(3, 0)
        )

        entry_cliente_oc = ctk.CTkEntry(
            frame_oc,
            width=420,
            height=40,
            placeholder_text="Cliente"
        )

        entry_cliente_oc.grid(
            row=1,
            column=1,
            padx=(10, 10),
            pady=(3, 0)
        )

        entry_valor_oc = ctk.CTkEntry(
            frame_oc,
            width=180,
            height=40,
            placeholder_text="Valor NF"
        )

        entry_valor_oc.grid(
            row=1,
            column=2,
            padx=(10, 10),
            pady=(3, 0)
        )


        # LISTAGEM DAS OCs ADICIONADAS

        frame_lista = ctk.CTkFrame(
            frame_form
        )

        frame_lista.pack(
            fill="x",
            padx=30,
            pady=(20, 10)
        )
        ctk.CTkLabel(
            frame_form,
            text=""
        ).pack(
            pady=5
        )

        lbl_lista = ctk.CTkLabel(
            frame_lista,
            text="Nenhuma OC adicionada.",
            justify="left",
            anchor="w"
        )

        lbl_lista.pack(
            fill="x",
            padx=10,
            pady=10
        )

        # VALOR TOTAL

        lbl_total = ctk.CTkLabel(
            frame_lista,
            text="Valor total: R$ 0,00",
            font=(
                "Arial",
                14,
                "bold"
            )
        )

        lbl_total.pack(
            anchor="e",
            padx=10,
            pady=(0, 10)
        )

        # ATUALIZAR LISTAGEM DE OCs

        def atualizar_lista():

            if not lista_ocs:

                lbl_lista.configure(
                    text="Nenhuma OC adicionada."
                )

                lbl_total.configure(
                    text="Valor total: R$ 0,00"
                )

                return

            linhas = []

            for item in lista_ocs:

                linhas.append(
                    f"OC {item['numero_oc']} | "
                    f"{item['cliente']} | "
                    f"{self.formatar_moeda(item['valor_nf'])}"
                )

            lbl_lista.configure(
                text="\n".join(linhas)
            )

            total = sum(
                item["valor_nf"]
                for item in lista_ocs
            )

            lbl_total.configure(
                text=(
                    f"Valor total: "
                    f"{self.formatar_moeda(total)}"
                )
            )

        # ADICIONAR OC

        def adicionar_oc():

            numero_oc = (
                entry_oc
                .get()
                .strip()
            )

            cliente_oc = (
                entry_cliente_oc
                .get()
                .strip()
            )

            valor = (
                entry_valor_oc
                .get()
                .strip()
            )

            # VALIDAR OC

            if not numero_oc:

                messagebox.showwarning(
                    "OC",
                    "Informe o número da OC.",
                    parent=janela
                )

                entry_oc.focus_force()

                return

            if not numero_oc.isdigit():

                messagebox.showerror(
                    "OC Inválida",
                    "A OC deve conter somente números.",
                    parent=janela
                )

                entry_oc.focus_force()

                return

            # NÃO PERMITE OC DUPLICADA

            if any(
                item["numero_oc"] == numero_oc
                for item in lista_ocs
            ):

                messagebox.showwarning(
                    "OC Duplicada",
                    f"A OC {numero_oc} já foi adicionada.",
                    parent=janela
                )

                entry_oc.delete(
                    0,
                    "end"
                )

                entry_oc.focus_force()

                return

            # VALIDAR CLIENTE 
            if not cliente_oc:
                messagebox.showwarning(
                    "Cliente",
                    "Informe o cliente da OC.",
                    parent=janela
                )

                entry_cliente_oc.focus_force()

                return

            # VALIDAR VALOR

            if not valor:

                messagebox.showwarning(
                    "Valor",
                    "Informe o valor da NF da OC.",
                    parent=janela
                )

                entry_valor_oc.focus_force()

                return

            try:

                valor_float = (
                    self.converter_valor(
                        valor
                    )
                )

            except ValueError:

                messagebox.showerror(
                    "Valor Inválido",
                    "Informe um valor válido para a NF.\n\n"
                    "Exemplos:\n"
                    "5000\n"
                    "5000,00\n"
                    "5.000,00",
                    parent=janela
                )

                entry_valor_oc.focus_force()

                return

            if valor_float < 0:

                messagebox.showerror(
                    "Valor Inválido",
                    "O valor não pode ser negativo.",
                    parent=janela
                )

                entry_valor_oc.focus_force()

                return

            # ADICIONAR NA LISTA

            lista_ocs.append(
                {
                    "numero_oc": numero_oc,
                    "cliente": cliente_oc,
                    "valor_nf": valor_float
                }
            )

            # LIMPAR CAMPOS

            entry_oc.delete(
                0,
                "end"
            )

            entry_cliente_oc.delete(
                0,
                "end"
            )

            entry_valor_oc.delete(
                0,
                "end"
            )

            atualizar_lista()

            entry_oc.focus_force()

        # BOTÃO ADICIONAR OC

        btn_adicionar = ctk.CTkButton(
            frame_oc,
            text="+ ADICIONAR",
            width=140,
            height=40,
            fg_color="#138D75",
            hover_color="#117864",
            command=adicionar_oc
        )

        btn_adicionar.grid(
            row=1,
            column=3,
            padx=(15, 0),
            pady=(3, 0)
        )

        # ENTER NO VALOR ADICIONA A OC

        entry_valor_oc.bind(
            "<Return>",
            lambda event:
            adicionar_oc()
        )

        # REMOVER ÚLTIMA OC

        def remover_ultima_oc():

            if not lista_ocs:

                messagebox.showinfo(
                    "Informação",
                    "Não existem OCs para remover.",
                    parent=janela
                )

                return

            lista_ocs.pop()

            atualizar_lista()

            entry_oc.focus_force()

        ctk.CTkButton(
            frame_lista,
            text="REMOVER ÚLTIMA OC",
            width=160,
            fg_color="#7F8C8D",
            hover_color="#626567",
            command=remover_ultima_oc
        ).pack(
            anchor="w",
            padx=10,
            pady=(0, 10)
        )

        # PLACA

        ctk.CTkLabel(
            frame_form,
            text="Placa do Caminhão",
            font=(
                "Arial",
                14,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=30,
            pady=(8, 3)
        )

        entry_placa = ctk.CTkEntry(
            frame_form,
            width=580,
            height=40,
            placeholder_text="Ex.: ABC1D23"
        )

        entry_placa.pack(
            anchor="w",
            padx=30
        )

        # MOTIVO

        ctk.CTkLabel(
            frame_form,
            text="Motivo da Devolução",
            font=(
                "Arial",
                14,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=30,
            pady=(8, 3)
        )

        entry_motivo = ctk.CTkEntry(
            frame_form,
            width=580,
            height=40,
            placeholder_text="Informe o motivo"
        )

        entry_motivo.pack(
            anchor="w",
            padx=30
        )

        # SALVAR DEVOLUÇÃO

        def salvar():

            placa = (
                entry_placa
                .get()
                .strip()
                .upper()
            )

            motivo = (
                entry_motivo
                .get()
                .strip()
            )

            # VALIDAR CAMPOS

            campos_faltantes = []

            if not lista_ocs:

                campos_faltantes.append(
                    "Pelo menos uma OC"
                )

            if not placa:

                campos_faltantes.append(
                    "Placa do Caminhão"
                )

            if not motivo:

                campos_faltantes.append(
                    "Motivo"
                )

            if campos_faltantes:

                texto = "\n".join(
                    f"• {campo}"
                    for campo in campos_faltantes
                )

                messagebox.showwarning(
                    "Campos Obrigatórios",
                    "Preencha os seguintes campos:\n\n"
                    f"{texto}",
                    parent=janela
                )

                return

            # CALCULAR VALOR TOTAL

            total = sum(
                item["valor_nf"]
                for item in lista_ocs
            )

            # MONTAR TEXTO DAS OCs

            ocs_texto = ", ".join(
                item["numero_oc"]
                for item in lista_ocs
            )

            clientes = ", ".join(
                sorted(
                    {
                        item["cliente"]
                        for item in lista_ocs
                    }
                )
            )

            # CONFIRMAÇÃO

            resposta = messagebox.askyesno(
                "Confirmar Abertura",

                "Deseja iniciar esta devolução?\n\n"

                f"OCs: {ocs_texto}\n"
                f"Placa: {placa}\n"
                f"Cliente: {clientes}\n"
                f"Motivo: {motivo}\n"
                f"Valor total: "
                f"{self.formatar_moeda(total)}\n\n"

                f"Conferente: {self.conferente}",

                parent=janela
            )

            if not resposta:
                return

            # GRAVAR NO BANCO

            try:

                devolucao_id = (
                    self.db.criar_devolucao(
                        self.conferente,
                        lista_ocs,
                        placa,
                        motivo
                    )
                )

            except Exception as erro:

                messagebox.showerror(
                    "Erro",
                    "Falha ao iniciar a devolução:\n\n"
                    f"{erro}",
                    parent=janela
                )

                return

            # FECHAR MODAL

            janela.destroy()

            # ATUALIZAR HOME

            self.carregar_abertas()

            # SUCESSO

            messagebox.showinfo(
                "Sucesso",
                "Devolução iniciada com sucesso.\n\n"

                f"ID: {devolucao_id}\n"
                f"Placa: {placa}\n"
                f"OCs: {ocs_texto}\n"
                f"Valor total: "
                f"{self.formatar_moeda(total)}"
            )

        # BOTÕES

        frame_acoes = ctk.CTkFrame(
            frame_form,
            fg_color="transparent"
        )

        frame_acoes.pack(
            fill="x",
            padx=30,
            pady=20
        )

        # CANCELAR

        ctk.CTkButton(
            frame_acoes,
            text="CANCELAR",
            width=150,
            height=40,
            fg_color="#7F8C8D",
            hover_color="#626567",
            command=janela.destroy
        ).pack(
            side="left"
        )

        # INICIAR

        ctk.CTkButton(
            frame_acoes,
            text="INICIAR DEVOLUÇÃO",
            width=200,
            height=40,
            fg_color="#138D75",
            hover_color="#117864",
            font=(
                "Arial",
                14,
                "bold"
            ),
            command=salvar
        ).pack(
            side="right"
        )

        # FOCO INICIAL

        janela.after(
            200,
            entry_oc.focus_force
        )
    
    # Função para finalizar devolução
    def finalizar_devolucao(self):
        selecionado = (self.tree.selection())

        if not selecionado:
            messagebox.showwarning(
                "Aviso",
                "Selecione uma devolução "
                "para finalizar."
            )
            return

        # DADOS DA LINHA
        valores = self.tree.item(
            selecionado[0],
            "values"
        )

        devolucao_id = valores[0]
        ocs = valores[1]
        cliente = valores[2]
        placa = valores[3]
        motivo = valores[4]
        valor = valores[5]
        inicio = valores[6]
        aberto_por = valores[7]

        # CONFIRMAÇÃO
        resposta = messagebox.askyesno(
            "Finalizar Devolução",
            "Deseja realmente finalizar "
            "esta devolução?\n\n"
            f"OCs: {ocs}\n"
            f"Cliente: {cliente}\n"
            f"Placa: {placa}\n"
            f"Motivo: {motivo}\n"
            f"Valor NF: {valor}\n"
            f"Início: {inicio}\n"
            f"Aberto por: {aberto_por}\n\n"
            f"Finalizado por: {self.conferente}"
        )
        if not resposta:
            return

        # BANCO
        try:
            sucesso = (
                self.db.finalizar_devolucao(
                    devolucao_id,
                    self.conferente
                )
            )
        except Exception as erro:
            messagebox.showerror(
                "Erro",
                "Falha ao finalizar "
                "a devolução:\n\n"
                f"{erro}"
            )
            return

        # Se não conseguiu finalizar (já finalizada)
        if not sucesso:
            messagebox.showwarning(
                "Aviso",
                "Esta devolução não está mais "
                "em aberto.\n\n"
                "A listagem será atualizada."
            )
            self.carregar_abertas()
            return

        # REFRESH
        self.carregar_abertas()

        # SUCESSO
        messagebox.showinfo(
            "Sucesso",
            "Devolução finalizada com sucesso.\n\n"
            f"OCs: {ocs}"
        )

    # Função de exportação
    def tela_exportacao(self):

        janela = ctk.CTkToplevel(self)

        janela.title(
            "Exportar Devoluções"
        )

        largura = 500
        altura = 440

        janela.geometry(
            f"{largura}x{altura}"
        )

        janela.resizable(
            False,
            False
        )

        # CENTRALIZAR
        janela.update_idletasks()

        x = (
            janela.winfo_screenwidth()
            - largura
        ) // 2

        y = (
            janela.winfo_screenheight()
            - altura
        ) // 2

        janela.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

        janela.transient(self)

        janela.grab_set()

        # TÍTULO

        ctk.CTkLabel(
            janela,
            text="EXPORTAR DEVOLUÇÕES",
            font=(
                "Arial",
                22,
                "bold"
            )
        ).pack(
            pady=(30, 20)
        )

        ctk.CTkLabel(
            janela,
            text=(
                "Selecione o mês e o ano "
                "das devoluções."
            ),
            font=(
                "Arial",
                14
            )
        ).pack(
            pady=(0, 20)
        )

        # MESES

        meses = [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12"
        ]

        mes_var = ctk.StringVar(
            value=datetime.now().strftime(
                "%m"
            )
        )

        ano_var = ctk.StringVar(
            value=str(
                datetime.now().year
            )
        )

        # MÊS

        ctk.CTkLabel(
            janela,
            text="Mês",
            font=(
                "Arial",
                14,
                "bold"
            )
        ).pack(
            pady=(5, 3)
        )

        combo_mes = ctk.CTkComboBox(
            janela,
            values=meses,
            variable=mes_var,
            width=250,
            state="readonly"
        )

        combo_mes.pack(
            pady=5
        )

        # ANO

        ctk.CTkLabel(
            janela,
            text="Ano",
            font=(
                "Arial",
                14,
                "bold"
            )
        ).pack(
            pady=(15, 3)
        )

        entry_ano = ctk.CTkEntry(
            janela,
            textvariable=ano_var,
            width=250
        )

        entry_ano.pack(
            pady=5
        )

        # GERAR EXCEL
        def gerar():
            mes = (
                mes_var
                .get()
                .strip()
            )
            ano = (
                ano_var
                .get()
                .strip()
            )

            # VALIDAR ANO
            if (not ano.isdigit() or len(ano) != 4):
                messagebox.showerror(
                    "Erro",
                    "Informe um ano válido.\n\n"
                    "Exemplo: 2026",
                    parent=janela
                )
                return

            # ESCOLHER CAMINHO PARA SALVAR O ARQUIVO
            caminho = (
                filedialog.asksaveasfilename(
                    parent=janela,
                    title="Salvar Exportação",
                    defaultextension=".xlsx",
                    initialfile=(
                        f"DEVOLUCOES_"
                        f"{mes}_{ano}.xlsx"
                    ),
                    filetypes=[
                        (
                            "Arquivo Excel",
                            "*.xlsx"
                        )
                    ]
                )
            )

            if not caminho:
                return

            # EXPORTAR
            try:
                arquivo = exportar_mes(
                    self.db,
                    mes,
                    ano,
                    caminho
                )
            except ValueError as erro:
                messagebox.showwarning(
                    "Exportação",
                    str(erro),
                    parent=janela
                )
                return
            except Exception as erro:
                messagebox.showerror(
                    "Erro",
                    "Falha ao gerar o arquivo:\n\n"
                    f"{erro}",
                    parent=janela
                )
                return

            # SUCESSO
            messagebox.showinfo(
                "Sucesso",
                "Arquivo gerado com sucesso:\n\n"
                f"{arquivo}",
                parent=janela
            )

        # BOTÃO
        ctk.CTkButton(
            janela,
            text="EXPORTAR XLSX",
            width=250,
            height=45,
            font=(
                "Arial",
                14,
                "bold"
            ),
            command=gerar
        ).pack(
            pady=30
        )

    # Função para converter valor brasileiro em float
    
if __name__ == "__main__":
    app = App()
    app.mainloop()   