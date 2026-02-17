#!/usr/bin/env python3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib

# Configurações
ROOT = pathlib.Path(__file__).resolve().parent
RESULTS_FILE = ROOT / "experiments" / "results_1k" / "final_stats.json"
OUTPUT_DIR = ROOT / "experiments" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    if not RESULTS_FILE.exists():
        print(f"❌ Arquivo de resultados não encontrado: {RESULTS_FILE}")
        return

    # Carregar dados
    with open(RESULTS_FILE, "r") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # 1. Estatísticas Descritivas
    summary = {
        "total_iterations": len(df),
        "replay_match_rate": df["replay_match"].mean() * 100,
        "avg_psi_stability": df["psi_stability"].mean(),
        "total_omega_triggers": int(df["omega_triggers"].sum()),
        "avg_duration_ms": df["duration_ms"].mean(),
        "std_duration_ms": df["duration_ms"].std()
    }
    
    with open(OUTPUT_DIR / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("📊 Resumo Estatístico:")
    print(json.dumps(summary, indent=2))

    # 2. Visualizações
    sns.set_theme(style="whitegrid")
    
    # Distribuição da Estabilidade Ψ
    plt.figure(figsize=(10, 6))
    sns.histplot(df["psi_stability"], kde=True, color="blue")
    plt.title("Distribuição da Estabilidade Ontológica (Ψ)")
    plt.xlabel("Estabilidade Ψ")
    plt.ylabel("Frequência")
    plt.savefig(OUTPUT_DIR / "psi_stability_dist.png")
    plt.close()
    
    # Tempo de Execução ao longo das iterações
    plt.figure(figsize=(12, 6))
    plt.plot(df["iteration"], df["duration_ms"], alpha=0.5, color="green")
    plt.title("Latência de Execução do Pipeline Causal")
    plt.xlabel("Iteração")
    plt.ylabel("Duração (ms)")
    plt.savefig(OUTPUT_DIR / "execution_latency.png")
    plt.close()
    
    # Mapa de Calor de Gatilhos Ω (se houver)
    if summary["total_omega_triggers"] > 0:
        plt.figure(figsize=(10, 2))
        triggers = df[df["omega_triggers"] > 0]["iteration"]
        plt.scatter(triggers, [1]*len(triggers), color="red", marker="|", s=100)
        plt.title("Eventos de Interdição do Ω-Gate")
        plt.xlabel("Iteração")
        plt.yticks([])
        plt.savefig(OUTPUT_DIR / "omega_triggers.png")
        plt.close()

    print(f"✅ Análise concluída. Gráficos salvos em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
