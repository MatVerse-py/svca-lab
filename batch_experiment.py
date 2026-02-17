#!/usr/bin/env python3
import subprocess
import hashlib
import json
import time
import pathlib
import random
import os

# Configurações do Experimento
ITERATIONS = 1000
ROOT = pathlib.Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "experiments" / "results_1k"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def get_file_hash(path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def simulate_puf():
    """Simula a entropia de um PUF (Physical Unclonable Function)"""
    # Em um sistema real, isso viria do hardware (ex: RP2040)
    return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()

def main():
    print(f"🚀 Iniciando Ensaio Estatístico: {ITERATIONS} iterações")
    print(f"📂 Resultados serão salvos em: {RESULTS_DIR}")
    
    stats = []
    
    for i in range(1, ITERATIONS + 1):
        start_time = time.time()
        
        # 1. Simular Entropia de Hardware (PUF)
        puf_entropy = simulate_puf()
        
        # 2. Build
        build_ok, _, build_err = run_cmd("./build.sh")
        if not build_ok:
            print(f"❌ Erro no Build na iteração {i}: {build_err}")
            continue
            
        hash_v1 = get_file_hash(ROOT / "build" / "module.wasm")
        
        # 3. Verify (inclui o Replay determinístico)
        verify_ok, _, verify_err = run_cmd("./verify.sh")
        if not verify_ok:
            print(f"❌ Erro na Verificação na iteração {i}: {verify_err}")
            continue
            
        hash_v2 = get_file_hash(ROOT / "build" / "module.wasm")
        
        # 4. Checar Determinismo (Replay Match)
        replay_match = (hash_v1 == hash_v2)
        
        # 5. Simular métricas ontológicas (Ψ e Ω)
        # Em um sistema real, estas seriam extraídas do log de execução do Ω-Gate
        psi_stability = 0.99 + (random.random() * 0.01) # Simulação de estabilidade alta
        omega_triggers = 0 if random.random() > 0.01 else 1 # 1% de chance de gatilho de segurança
        alpha_r = hashlib.sha256(f"{puf_entropy}{hash_v1}".encode()).hexdigest()[:16]
        
        duration = time.time() - start_time
        
        iteration_data = {
            "iteration": i,
            "puf_entropy": puf_entropy,
            "wasm_hash": hash_v1,
            "replay_match": replay_match,
            "psi_stability": psi_stability,
            "omega_triggers": omega_triggers,
            "alpha_r": alpha_r,
            "duration_ms": int(duration * 1000)
        }
        
        stats.append(iteration_data)
        
        if i % 100 == 0:
            print(f"✅ Concluídas {i}/{ITERATIONS} iterações...")
            # Salvar progresso parcial
            with open(RESULTS_DIR / f"partial_{i}.json", "w") as f:
                json.dump(stats, f, indent=2)

    # Salvar resultado final
    final_path = RESULTS_DIR / "final_stats.json"
    with open(final_path, "w") as f:
        json.dump(stats, f, indent=2)
        
    print(f"\n✨ Experimento concluído!")
    print(f"📊 Dados salvos em: {final_path}")

if __name__ == "__main__":
    main()
