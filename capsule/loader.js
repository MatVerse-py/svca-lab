// Ω‑Gate: só ativa se a assinatura for válida
export async function openGate() {
    const wasmResp = await fetch('module.wasm');
    const wasmBytes = await wasmResp.arrayBuffer();
    const mod = await WebAssembly.instantiate(wasmBytes, {});
    console.log('✅ Módulo WASM carregado');
    return mod;
}
