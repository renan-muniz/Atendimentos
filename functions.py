from variables import get_connection
import pandas as pd
from flask import jsonify
from datetime import date

def tabela_atendimentos():
    
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        query = """SELECT *
            FROM public.atendimentos
            WHERE data_sessao >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
            AND data_sessao <  date_trunc('month', CURRENT_DATE)
            ORDER BY data_sessao, nome_cliente;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        query_2 = """SELECT *
            FROM public.atendimentos
            ORDER BY data_sessao DESC
            
        """
        cursor.execute(query_2)
        resultados_2 = cursor.fetchall()
        
        

        df_last_month = pd.DataFrame(resultados, columns=['id', 'nome_cliente', 'data_sessao', 'valor', 'status', 'data_pagamento', 'criado_em'])
        
        df_all = pd.DataFrame(resultados_2, columns=['id', 'nome_cliente', 'data_sessao', 'valor', 'status', 'data_pagamento', 'criado_em'])

        atendimentos_total = len(df_last_month)
        valor_total_mes = float(df_last_month['valor'].sum())


        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        if cursor:
            cursor.close()
        conexion.close()
        
    return df_last_month, df_all, atendimentos_total, valor_total_mes 
 


 
def novo_atendimento(nome_cliente,data_sessao, valor, status, data_pagamento):
    
    conexion = get_connection()
    cursor = None
    
    status = status.lower().strip()
    
    if status == 'pendente':
        data_pagamento = None
    elif status == 'pago' and data_pagamento is None:
        data_pagamento = date.today()
    
    try:
        cursor = conexion.cursor()
        query = """INSERT INTO public.atendimentos(nome_cliente, data_sessao, valor, status, data_pagamento)
        VALUES(%s, %s, %s, %s, %s)"""
        
        cursor.execute(query, (nome_cliente, data_sessao, valor, status, data_pagamento))
        conexion.commit()
        

    except Exception as e:
        import traceback
        traceback.print_exc()
        conexion.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        conexion.close()
    return True
            


def marcar_pago(ids: list[int], data_pagamento = None) -> int:
    
    conexion = get_connection()
    cursor = None
    
    if not ids:
        return 0
    
    if data_pagamento is None:
        data_pagamento = date.today()
    
    try:
        cursor = conexion.cursor()
        ids_tuple = tuple(ids)
        
        query = """UPDATE public.atendimentos 
        SET status = 'pago', data_pagamento = %s 
        WHERE id IN %s 
        AND status = 'pendente'  
        AND data_sessao >= date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'
            AND data_sessao <  date_trunc('month', CURRENT_DATE)
        """
        
        cursor.execute(query, (data_pagamento, ids_tuple))
        linhas = cursor.rowcount
        conexion.commit()
        return linhas
    except Exception as e:
        
        conexion.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def dados_graficos(ultimos_meses=12):
    
    
    conexion = get_connection()
    cursor = None
    
    try:
        cursor = conexion.cursor()

        query_atendimentos  = """SELECT date_trunc('month', data_sessao) AS mes, 
        COUNT(*) AS qtd_atendimentos
        FROM public.atendimentos
        GROUP BY mes
        ORDER BY mes"""
        
        query_recebido  = """SELECT date_trunc('month', data_pagamento) AS mes, 
        SUM(valor) AS total_recebido
        FROM public.atendimentos
        WHERE status = 'pago' AND data_pagamento IS NOT NULL
        GROUP BY mes
        ORDER BY mes"""

        
        cursor.execute(query_atendimentos )
        atendimentos = cursor.fetchall()
        
        
        
        cursor.execute(query_recebido )
        recebidos = cursor.fetchall()
        
        
        
        return atendimentos, recebidos

    except:
        conexion.rollback()
        raise
    
    finally:
        if cursor:
            cursor.close()    
        conexion.close()
