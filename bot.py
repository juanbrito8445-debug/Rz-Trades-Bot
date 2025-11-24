import os
import discord 
from discord.ext import commands
import asyncio 
import json # <--- ADICIONE ESTA LINHA

# --- FUNÇÕES DE PERSISTÊNCIA ---

def carregar_estoque():
    """Carrega o estoque do arquivo JSON."""
    try:
        # Tenta abrir e ler o arquivo
        with open('estoque.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("AVISO: O arquivo estoque.json não foi encontrado. Usando estoque vazio.")
        return {}
    except json.JSONDecodeError:
        print("ERRO: O arquivo estoque.json está corrompido.")
        return {}

def salvar_estoque(estoque_dados):
    """Salva o estoque no arquivo JSON."""
    try:
        with open('estoque.json', 'w', encoding='utf-8') as f:
            # Salva o dicionário com indentação para facilitar a leitura humana
            json.dump(estoque_dados, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"ERRO ao salvar o estoque: {e}")

# --- CONFIGURAÇÃO INICIAL ---

# Carrega o estoque do arquivo assim que o bot iniciar
ESTOQUE = carregar_estoque() 

# ... (o resto do seu código de intents e bot continua aqui)
# bot.py

import discord
from discord.ext import commands

# --- CONFIGURAÇÃO INICIAL ---
# Defina o prefixo para os comandos (ex: !comprar, !confirmar)
intents = discord.Intents.default()
# Lembre-se de ligar as Intents Privilegiadas no painel de desenvolvedor!
intents.members = True 
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# Armazenamento simples de estoque (Na vida real, usaria um banco de dados)
ESTOQUE = {
    "conta_001": {"login": "usuario123", "senha": "senha_segura", "status": "disponível"},
    "conta_002": {"login": "usuario456", "senha": "outra_senha", "status": "disponível"},
    # Adicione mais contas aqui.
}
# --- FIM CONFIGURAÇÃO INICIAL ---

@bot.event
async def on_ready():
    """Confirma que o bot está logado e funcionando."""
    print(f'Bot logado como {bot.user}')

# --- COMANDO DE CRIAÇÃO DE TICKET (!comprar) ---
@bot.command()
async def comprar(ctx):
    # DENTRO da função 'comprar(ctx)':

# ...
# 3. Resposta Automática no Ticket
# Lista apenas as contas disponíveis
contas_disponiveis = [
    id_conta for id_conta, dados in ESTOQUE.items() if dados["status"] == "disponível"
]
estoque_listado = ', '.join(contas_disponiveis) if contas_disponiveis else "NENHUMA"

await ticket_channel.send(
    f"Bem-vindo(a), {ctx.author.mention}! **Seu ticket de compra foi criado.**\n"
    "Por favor, envie o comprovante de pagamento e informe qual conta deseja.\n"
    f"Nosso estoque atual é: **{estoque_listado}**." # <--- LINHA ATUALIZADA
)
# ...
    """Cria um canal privado (ticket) para iniciar uma compra."""
    # Evita que o comando seja usado fora de um canal de texto
    if not isinstance(ctx.channel, discord.TextChannel):
        return

    # 1. Definições de Permissões
    # Cria um dicionário de permissões para o novo canal.
    # O usuário que iniciou o ticket e o bot podem ver.
    # Todos (@everyone) não podem ver.
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    # 2. Criação do Canal
    try:
        # Cria um novo canal de texto (o ticket)
        ticket_channel = await ctx.guild.create_text_channel(
            name=f'ticket-{ctx.author.name}-{ctx.author.discriminator}',
            category=ctx.channel.category, # Opcional: cria na mesma categoria
            overwrites=overwrites
        )

        # 3. Resposta no Ticket
        await ticket_channel.send(
            f"Bem-vindo(a), {ctx.author.mention}!\n\n"
            "**Seu ticket de compra foi criado.** Por favor, envie uma captura de tela do comprovante de pagamento.\n"
            f"Nosso estoque atual é: {', '.join(ESTOQUE.keys())}"
        )

        # 4. Feedback ao Usuário (no canal original)
        await ctx.send(f'{ctx.author.mention}, seu ticket foi aberto em {ticket_channel.mention}.', delete_after=10)
        await ctx.message.delete() # Limpa o comando !comprar
        
    except discord.Forbidden:
        await ctx.send("Erro: Eu não tenho permissão para criar canais.")
    except Exception as e:
        print(f"Erro ao criar ticket: {e}")
        await ctx.send("Ocorreu um erro ao criar seu ticket.")


# --- COMANDO DE CONFIRMAÇÃO DE PAGAMENTO (!confirmar) ---
@bot.command()
@commands.has_permissions(administrator=True) # Apenas administradores podem usar
async def confirmar(ctx, id_conta: str):
    # DENTRO da função 'confirmar(ctx, id_conta)':

# ...
# 2. Atualiza o Status
ESTOQUE[id_conta]["status"] = "vendido"

# SALVA A MUDANÇA NO ARQUIVO JSON! <--- ADICIONE ESTAS DUAS LINHAS
salvar_estoque(ESTOQUE) 

# 3. Fechamento do Ticket
# ...
    """Comando para administradores confirmarem o pagamento e enviarem a conta."""

    if id_conta not in ESTOQUE:
        await ctx.send(f"Erro: ID da conta **{id_conta}** não encontrado no estoque.", delete_after=15)
        return

    conta = ESTOQUE[id_conta]

    if conta["status"] != "disponível":
        await ctx.send(f"Erro: A conta **{id_conta}** já foi vendida ou está indisponível.", delete_after=15)
        return

    # 1. Envio da Conta ao Usuário (no canal do ticket)
    await ctx.send(
        f"✅ **PAGAMENTO CONFIRMADO!**\n\n"
        f"Aqui estão os dados da sua conta **{id_conta}**:\n"
        f"**Login:** `{conta['login']}`\n"
        f"**Senha:** `{conta['senha']}`\n\n"
        "Obrigado por comprar conosco! Este ticket será fechado em breve."
    )

    # 2. Atualiza o Status no Estoque
    ESTOQUE[id_conta]["status"] = "vendido"

    # 3. Fechamento do Ticket (Opcional, mas recomendado)
    # Você pode adicionar um atraso e depois deletar o canal.
    # await asyncio.sleep(600) # Espera 10 minutos
    # await ctx.channel.delete() 

# --- RODAR O BOT ---
# Substitua 'MTQ0MjYzNjQ0NTI1MTY3MDEwNg.G19xTo.MZsMyV7YcPh8JA_zlzNCHd2F4FadOl3EOWAhA0' pelo token que você copiou no passo 1.
# --- RODAR O BOT ---
# O bot irá buscar o token da variável de ambiente BOT_TOKEN definida no Render/Railway.
try:
    # Pega o token da variável de ambiente (definida no Render/Railway)
    token = os.environ.get('BOT_TOKEN') 
    if token:
        bot.run(token)
    else:
        print("ERRO: Variável de ambiente 'BOT_TOKEN' não encontrada. O bot não pode ser iniciado.")
except discord.errors.LoginFailure:
    print("ERRO: O token do bot está incorreto. Verifique se o token inserido é válido.")
