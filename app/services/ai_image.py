import torch
from diffusers import DiffusionPipeline
import os
from datetime import datetime
from app.config import Config

async def generate_image(prompt: str) -> str:
    """
    Генерация изображения с использованием Stable Diffusion
    """
    try:
        # Проверяем доступность MPS (Mac) или CUDA
        if not torch.backends.mps.is_available():
            if not torch.backends.mps.is_built():
                print("MPS недоступен (torch.backends.mps.is_built() == False).")
            else:
                print("MPS недоступен (не поддерживается).")
            device = torch.device("cpu")
            print("Используется CPU")
        else:
            print("MPS доступен.")
            device = torch.device("mps")

        # Используем более легкую модель для скорости
        pipe = DiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16"
        )

        pipe = pipe.to(device)

        print(f"Генерация изображения: {prompt}")
        
        # Генерируем с настройками для скорости
        image = pipe(
            prompt=prompt,
            num_inference_steps=50,  # Уменьшаем шаги для скорости
            guidance_scale=7.5
        ).images[0]

        # Сохраняем изображение
        os.makedirs("data/images", exist_ok=True)
        output_filename = f"data/images/generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(output_filename)

        print(f"Изображение успешно сохранено в файл {output_filename}")
        return output_filename

    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
        return create_fallback_image(prompt)

def create_fallback_image(prompt: str) -> str:
    """Создает заглушку если генерация не удалась"""
    from PIL import Image, ImageDraw
    import os
    
    os.makedirs("data/images", exist_ok=True)
    filename = f"data/images/fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    img = Image.new('RGB', (512, 512), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    lines = []
    words = prompt.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if len(test_line) > 30:
            lines.append(line)
            line = word + " "
        else:
            line = test_line
    if line:
        lines.append(line)
    
    y = 10
    for line in lines:
        d.text((10, y), line, fill=(255, 255, 255))
        y += 20
    
    d.text((10, y + 20), "❌ Ошибка генерации изображения", fill=(255, 200, 200))
    d.text((10, y + 40), "Проверьте настройки Stable Diffusion", fill=(255, 200, 200))

    img.save(filename)
    return filename