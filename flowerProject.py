import os
import pygame
import time
from difflib import get_close_matches
import subprocess
import whisper
from pathlib import Path

def say(text):
    subprocess.run(["say", "-v", "Thomas", text])

def transcribe(file_path):
    model = whisper.load_model("base") 
    
    print("📜 Transcription en cours...")
    result = model.transcribe(file_path, language="fr")
  
    print("📝 Transcription:")
    print(result['text'])
    return result['text']

def record(file_path, duration=4):
    print(f"🎙️ Enregistrement en cours pour {duration} secondes...")
    subprocess.run(["ffmpeg", "-f", "avfoundation", "-i", ":1", "-t", str(duration), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-y", file_path])
    print(f"🎙️ Enregistrement terminé et sauvegardé sous {file_path}")

my_file = Path("recorded_audio.wav")
audio_file = "recorded_audio.wav"
record(audio_file, duration=10)
#transcribe(audio_file)

def ask(question):
        prompt = f"""Tu es un assitant qui trouve le nom des villes dans laquel les gens on grandit. Tu renvoie que le nom de la ville. Par exemple si quelqun dit 'J'ai passé ma vie à Annecy' tu doit renvoyer le mot 'Annecy' si quelqun te dit 'Je suis de Pringy' tu doit renvoyer le mot 'Pringy'. Parfois les villes seront mal écrites c'est à toi de deviner l'écriture correcte. Tu dois t'aider de la liste suivante des 34 communes du grand Annecy: [
        "Annecy",
        "Alby-sur-Chéran",
        "Allèves",
        "Argonay",
        "Bluffy",
        "Chainaz-les-Frasses",
        "Chapeiry",
        "La Chapelle-Saint-Maurice",
        "Charvonnex",
        "Chavanod",
        "Cusy",
        "Duingt",
        "Entrevernes",
        "Epagny Metz-Tessy",
        "Fillière",
        "Groisy",
        "Gruffy",
        "Héry-sur-Alby",
        "Leschaux",
        "Menthon-Saint-Bernard",
        "Montagny-les-Lanches",
        "Mûres",
        "Nâves-Parmelan",
        "Poisy",
        "Quintal",
        "Saint-Eustache",
        "Saint-Félix",
        "Saint-Jorioz",
        "Saint-Sylvestre",
        "Sevrier",
        "Talloires-Montmin",
        "Veyrier-du-Lac",
        "Villaz",
        "Viuz-la-Chiésaz"]"""
        prompt += """
Voici un exemple de prompt/réponse:
Q: J'ai passé ma vie à Ansi
Answer: Annecy
Q: Je suis de T'as l'ouin
Answer: Talloires-Montmin
Q: J'ai grandit à Poisy
Answer: Poisy
Q: Je suis de Pringy
Answer: Pringy
Q: J'ai grandi à Ainsi.
Answer: Annecy
Q: J'ai grandi à Vylase.
Answer: Villaz
Q: J'ai vécu longtemps à Un jour yo
Answer: Saint-Jorioz
Q: J'ai vécu longtemps là bas à poésie
Answer: Poisy
Q: """

        prompt += question
        result = subprocess.run(
            ["llama-cli", "-m", "EXAONE-3.5-2.4B-Instruct-Q4_K_M.gguf", "-p", prompt, "-n", "128", "--temp", "0.3"],
            capture_output=True,
            text=True
        )
        print(result.stdout)  # Affiche la réponse générée
        if result.stderr:
            print("Erreur :", result.stderr)
        # get everything after the last "A: " 
        response = result.stdout.split("Answer: ")[-1]
        response = response.replace("[end of text]", "")
        response = response.strip()
        # convertir la chaine de caractères en dictionnaire
        print(response)
        return response

question = transcribe(audio_file)
print(question)
if question:
    print("ok")
    text = ask(question)
    print("Test:", text)


# Config
IMAGE_DISPLAY_TIME = 2       # seconds per image
FADE_DURATION = 1            # seconds for fade in/out
SCREEN_SIZE = (800, 600)     # Adjust as needed

def find_matching_folder(base_path, user_input):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    matches = get_close_matches(user_input, folders, n=1, cutoff=0.4)
    return matches[0] if matches else None

def load_images_from_folder(folder_path):
    supported = ('.jpg', '.jpeg', '.png', '.bmp')
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(supported)]

def fade_in_out(screen, image_path):
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, SCREEN_SIZE)

    fade_surface = pygame.Surface(SCREEN_SIZE)
    fade_surface.fill((0, 0, 0))

    # Fade in
    for alpha in range(255, -1, -15):
        screen.blit(image, (0, 0))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        time.sleep(FADE_DURATION / 17)

    # Display image
    screen.blit(image, (0, 0))
    pygame.display.flip()
    time.sleep(IMAGE_DISPLAY_TIME)

    # Fade out
    for alpha in range(0, 256, 15):
        screen.blit(image, (0, 0))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        time.sleep(FADE_DURATION / 17)

def main():
    base_path = './images'  # Parent directory containing folders of images
    if my_file.is_file():
        user_input = text

        matching_folder = find_matching_folder(base_path, user_input)
        if not matching_folder:
            print("No matching folder found.")
            return

        folder_path = os.path.join(base_path, matching_folder)
        images = load_images_from_folder(folder_path)

        if not images:
            print("No images found in the folder.")
            return

        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Image Slideshow")

        for img_path in images:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            fade_in_out(screen, img_path)

        pygame.quit()

if __name__ == "__main__":
    main()
