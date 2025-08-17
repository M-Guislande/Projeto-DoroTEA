import cv2
from deepface import DeepFace
import time

# Acessa a câmera do seu computador (0 para a câmera padrão)
cap = cv2.VideoCapture(0)

# Verifique se a câmera abriu corretamente
if not cap.isOpened():
    print("Erro: Não foi possível acessar a câmera.")
    exit()

print("Câmera acessada com sucesso. Pressione 'q' para sair.")

while True:
    # Captura um frame (quadro) do vídeo
    ret, frame = cap.read()

    # Se a captura falhar, saia do loop
    if not ret:
        break

    try:
        # Analisa o frame para detectar emoções
        # O 'actions' pode ser 'age', 'gender', 'race' ou 'emotion'
        analise = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        
        # Pega a emoção dominante
        emocao_dominante = analise[0]['dominant_emotion']
        
        # Pega as informações de localização do rosto
        face_info = analise[0]['face_region']
        x, y, w, h = face_info['x'], face_info['y'], face_info['w'], face_info['h']

        # Desenha um retângulo verde em volta do rosto
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Adiciona o texto com a emoção detectada
        fonte = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, emocao_dominante, (x, y - 10), fonte, 0.9, (0, 255, 0), 2)

    except Exception as e:
        # Se não detectar um rosto, a análise irá falhar. Apenas continue.
        pass

    # Exibe o frame processado
    cv2.imshow('Detector de Emoções', frame)

    # Pressione a tecla 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha a janela
cap.release()
cv2.destroyAllWindows()