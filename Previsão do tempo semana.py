from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# CONFIGURAÇÃO DA CHAVE DE API
load_dotenv()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


# ==============================================================================
# FUNÇÃO 1: OBTER CLIMA ATUAL
# ==============================================================================
def obter_clima_atual(cidade, pais="BR", lingua="pt_br"):
    if API_KEY == "SUA_API_KEY_AQUI" or not API_KEY:
        print("❌ Erro: Configure sua chave de API na variável 'API_KEY'.")
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': f'{cidade},{pais}',
        'appid': API_KEY.strip(),
        'units': 'metric',
        'lang': lingua
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"❌ Erro ao buscar clima atual: {err}")
        return None


# ==============================================================================
# FUNÇÃO 2: OBTER PREVISÃO SEMANAL
# ==============================================================================
def obter_previsao_tempo(cidade, pais="BR", lingua="pt_br"):
    if API_KEY == "SUA_API_KEY_AQUI" or not API_KEY:
        print("❌ Erro: Configure sua chave de API na variável 'API_KEY'.")
        return None

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': f'{cidade},{pais}',
        'appid': API_KEY.strip(),
        'units': 'metric',
        'lang': lingua
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"❌ Erro ao buscar previsão: {err}")
        return None


# ==============================================================================
# FUNÇÃO AUXILIAR: FORMATAR NOME DO DIA DA SEMANA
# ==============================================================================
def obter_nome_dia_semana(data_str):
    dt_obj = datetime.strptime(data_str, "%Y-%m-%d")
    dias_semana = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }
    nome_dia = dias_semana[dt_obj.weekday()]
    data_formatada = dt_obj.strftime("%d/%m/%Y")
    return f"{nome_dia}, {data_formatada}"


# ==============================================================================
# FUNÇÃO INTELIGENTE: GERAR RESUMO E RECOMENDAÇÕES DO DIA
# ==============================================================================
def gerar_resumo_diario(leituras_do_dia):
    """
    Analisa os dados compilados de um dia e gera sugestões personalizadas sem asteriscos.
    """
    temps = [item['main']['temp'] for item in leituras_do_dia]
    umidades = [item['main']['humidity'] for item in leituras_do_dia]
    chances_chuva = [item.get('pop', 0) * 100 for item in leituras_do_dia]

    temp_max = max(temps)
    temp_min = min(temps)
    media_chuva = sum(chances_chuva) / len(chances_chuva)
    umidade_minima = min(umidades)

    horarios_chuva_alta = []
    for item in leituras_do_dia:
        pop = item.get('pop', 0) * 100
        if pop >= 50:
            hora = item['dt_txt'].split(" ")[1][:5]
            horarios_chuva_alta.append(f"{hora} ({pop:.0f}%)")

    alertas = []

    # 1. Análise de Chuva e Guarda-chuva
    if horarios_chuva_alta:
        horarios_str = ", ".join(horarios_chuva_alta)
        alertas.append(f"🌧️ Atenção para chuva alta nos horários: {horarios_str}. Recomendação: Leve um guarda-chuva ou capa ao sair!")
    elif media_chuva >= 30:
        alertas.append(f"🌦️ Média de chuva no dia em {media_chuva:.0f}%: Há possibilidade de garoa ou chuva isolada. Leve um guarda-chuva por precaução.")
    else:
        alertas.append(f"☀️ Chance de chuva muito baixa ({media_chuva:.0f}% de média): Não há previsão relevante de chuva para hoje.")

    # 2. Análise de Temperatura e Vestuário
    if temp_min < 16 and temp_max > 25:
        alertas.append(f"🧥 Variação térmica alta (mín: {temp_min:.1f}°C / máx: {temp_max:.1f}°C): Vai fazer frio em algum momento e calor em outro. Recomendo levar um casaco leve para o período mais frio.")
    elif temp_max <= 18:
        alertas.append(f"🥶 Dia frio (máxima de {temp_max:.1f}°C): Recomendo vestir roupas bem quentes e casaco forte.")
    elif temp_max >= 28:
        alertas.append(f"🔥 Dia quente (máxima de {temp_max:.1f}°C): Use roupas leves e confortáveis.")

    # 3. Análise de Umidade / Hidratação / Qualidade do Ar
    if umidade_minima <= 30:
        alertas.append(f"💧 Umidade do ar baixa (mínima de {umidade_minima}%): A qualidade do ar pode ficar prejudicada. Mantenha-se bem hidratado e beba bastante água ao longo do dia!")

    return temp_min, temp_max, media_chuva, alertas


# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ☀️ MONITORAMENTO CLIMÁTICO COM ALERTAS E RECOMENDAÇÕES 🌧️ ")
    print("=" * 70)

    cidade_input = input("\nDigite o nome da cidade (ex: Guarulhos, São Paulo): ").strip()

    if not cidade_input:
        print("Nome de cidade inválido.")
    else:
        print(f"\nBuscando dados e gerando análise para {cidade_input}...")

        # 1. Clima Atual
        clima_atual = obter_clima_atual(cidade_input)
        if clima_atual:
            temp = clima_atual['main']['temp']
            sensacao = clima_atual['main']['feels_like']
            umidade = clima_atual['main']['humidity']
            condicao = clima_atual['weather'][0]['description']

            print("\n" + "=" * 70)
            print(f"🌡️ CLIMA ATUAL EM {clima_atual['name'].upper()}")
            print("=" * 70)
            print(f"Temperatura: {temp}°C (Sensação: {sensacao}°C) | Umidade: {umidade}% | {condicao.capitalize()}")

        # 2. Previsão Agrupada por Dia com Recomendações
        previsao = obter_previsao_tempo(cidade_input)
        if previsao:
            print("\n" + "=" * 70)
            print(f"📅 PREVISÃO SEMANAL E ALERTAS DE COMPROMISSO - {cidade_input.upper()}")
            print("=" * 70)

            dias_agrupados = {}
            for item in previsao['list']:
                data_sozinha = item['dt_txt'].split(" ")[0]
                if data_sozinha not in dias_agrupados:
                    dias_agrupados[data_sozinha] = []
                dias_agrupados[data_sozinha].append(item)

            for data_key, leituras in dias_agrupados.items():
                nome_dia = obter_nome_dia_semana(data_key)
                print(f"\n📌 {nome_dia.upper()}")
                print("-" * 50)

                for item in leituras:
                    hora = item['dt_txt'].split(" ")[1][:5]
                    t = item['main']['temp']
                    c = item['weather'][0]['description']
                    p = item.get('pop', 0) * 100
                    print(f"  • {hora} | {t:>4.1f}°C | {c.capitalize():<20} | Chance de chuva: {p:>2.0f}%")

                t_min, t_max, m_chuva, alertas = gerar_resumo_diario(leituras)

                print("\n  📋 RESUMO E RECOMENDAÇÕES DO DIA:")
                print(f"  • Variação de Temperatura: {t_min:.1f}°C até {t_max:.1f}°C")
                print(f"  • Chance Média de Chuva no Dia: {m_chuva:.0f}%")
                for alerta in alertas:
                    print(f"  • {alerta}")
                print("-" * 70)