from flask import request, Flask, render_template, redirect, url_for, flash
from functions import tabela_atendimentos, novo_atendimento as inserir_atendimento, marcar_pago as pagar_em_lote, dados_graficos
import pandas as pd
import os
from werkzeug.security import check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


MESES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-para-testes")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class AdminUser(UserMixin):
    def __init__(self, user_id: str):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    admin_user = os.getenv("ADMIN_USER", "admin")
    if user_id == admin_user:
        return AdminUser(user_id)
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")

    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass_hash = os.getenv("ADMIN_PASS_HASH", "")

    if username == admin_user and admin_pass_hash and check_password_hash(admin_pass_hash, password):
        login_user(AdminUser(admin_user))
        return redirect(url_for("dashboard"))

    flash("Usuário ou senha inválidos.")
    return redirect(url_for("login"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    return redirect(url_for("dashboard"))




@app.route("/dashboard", methods = ['GET'])
@login_required
def dashboard():
    
    df_last_month, df_all ,atendimentos_total, valor_total_mes = tabela_atendimentos()
    

    
    linhas_tabela_principal = df_all.to_dict(orient='records')
    
    
    df_last_month["valor"] = pd.to_numeric(df_last_month["valor"], errors="coerce").fillna(0)

    pendentes = df_last_month[df_last_month['status'] == 'pendente']
    
    pendentes = pendentes.groupby('nome_cliente', as_index= False).agg(total_pendente = ("valor", "sum"), ids =("id", lambda s: list(s)),
    datas=("data_sessao", lambda s: list(s)))
    
    pendentes = pendentes.to_dict(orient='records')
    
    mes_ref = (pd.Timestamp.today().replace(day=1) - pd.offsets.MonthBegin(1))
    nome_mes = MESES_PT[mes_ref.month]
    ano_ref = mes_ref.year

    for p in pendentes:
        datas = p["datas"]                 
        datas_fmt = [d.strftime("%d/%m") for d in datas]

        if len(datas_fmt) == 1:
            datas_txt = datas_fmt[0]
        elif len(datas_fmt) == 2:
            datas_txt = f"{datas_fmt[0]} e {datas_fmt[1]}"
        else:
            datas_txt = ", ".join(datas_fmt[:-1]) + " e " + datas_fmt[-1]

        qtd = len(datas)
        sessao_txt = "sessão" if qtd == 1 else "sessões"
        total = float(p["total_pendente"])

        total_fmt = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        p["mensagem"] = (
            f"O fechamento dos atendimentos do/a {p['nome_cliente']} no mês de "
            f"{nome_mes}/{ano_ref} foi de {qtd} {sessao_txt} "
            f"({datas_txt}), totalizando R${total_fmt}."
        )

    
    
    atend_mes, rec_mes = dados_graficos()
    
    atend_dict = {mes: qtd for (mes, qtd) in atend_mes}
    
    rec_dict = {mes: float(total) for(mes, total) in rec_mes}
    
    meses = sorted(
            m for m in (set(atend_dict.keys()) | set(rec_dict.keys()))
            if m is not None
        )
    
    labels_meses = [f'{MESES_PT[m.month]}/{m.year}' for m in meses]
    
    serie_atendimentos = [int(atend_dict.get(m, 0)) for m in meses]
    serie_recebido = [int(rec_dict.get(m,0)) for m in meses]
    
        
    return render_template(
        "index.html",
        atendimentos_total = atendimentos_total,
        valor_total_mes = valor_total_mes,
        atendimentos = linhas_tabela_principal,
        pendentes = pendentes,
          labels_meses=labels_meses,
        serie_atendimentos=serie_atendimentos,
        serie_recebido=serie_recebido,
)

@app.route("/novo_atendimento", methods = ['POST'])
@login_required
def criar_novo_atendimento():
    
    nome_cliente = request.form.get("nome_cliente")
    data_sessao = request.form.get("data_sessao")
    valor = request.form.get("valor")
    status = request.form.get("status")
    data_pagamento = request.form.get("data_pagamento")
    
    if data_pagamento == "" or data_pagamento is None:
        data_pagamento = None
    
    inserir_atendimento(nome_cliente,data_sessao, valor, status, data_pagamento)
    
    
    return redirect(url_for("dashboard"))


@app.route("/marcar_pago", methods = ['POST'])
@login_required
def marcar_pago_route():
    
    ids = request.form.getlist('ids')
    
    ids = [int(x) for x in ids]
    
    data_pagamento = request.form.get("data_pagamento")
    if data_pagamento == "" or data_pagamento is None:
        data_pagamento = None
        
    pagar_em_lote(ids, data_pagamento=data_pagamento)
    
    

    
    return redirect(url_for("dashboard"))
        
    


if __name__ == "__main__":
    app.run(debug=True)