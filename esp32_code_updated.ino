// Handler para retornar música selecionada e emoção (substitui handleStatus)
void handleMusicStatus() {
    server.sendHeader("Access-Control-Allow-Origin", "*");
    
    // Determina a música atual baseada no que está tocando
    String selectedMusic = "";
    if (isPlaying && !currentMusicPath.isEmpty()) {
        // Extrai o ID da música do caminho atual
        if (currentMusicPath == "/DoroTEA.mp3") selectedMusic = "DoroTEA";
        else if (currentMusicPath == "/bbee.mp3") selectedMusic = "bbee";
        else if (currentMusicPath == "/clairdelune.mp3") selectedMusic = "clairedelune";
        else if (currentMusicPath == "/lullabyy.mp3") selectedMusic = "lullabyy";
        else if (currentMusicPath == "/bmp.mp3") selectedMusic = "bmp";
        else selectedMusic = "DoroTEA"; // padrão
    } else {
        selectedMusic = "DoroTEA"; // música padrão quando não está tocando
    }
    
    // Simula uma emoção (você pode conectar com sensor real depois)
    String emotion = isPlaying ? "happy" : "neutral";
    
    String response = "{\"musica_selecionada\":\"" + selectedMusic + "\",\"ultima_emocao\":\"" + emotion + "\"}";
    server.send(200, "application/json", response);
}

// No setup(), substitua a linha:
// server.on("/status", HTTP_GET, handleStatus);
// Por:
// server.on("/status", HTTP_GET, handleMusicStatus);