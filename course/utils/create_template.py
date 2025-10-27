from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

def create_certificate_template():
    template_dir = "media/templates"
    template_path = os.path.join(template_dir, "template_certificate.png")
    font_path = os.path.join(
        settings.MEDIA_ROOT, "media/fonts", 'arial.ttf'
    )
    

    os.makedirs(template_dir, exist_ok=True)

    if not os.path.exists(template_path):
        image = Image.new("RGB", (1080, 720), color=(255, 255, 230))
        draw = ImageDraw.Draw(image)

        draw.text(
            (540, 100),
            "Certificado de Conclusão",
            fill="black",
            anchor="mm",
            font=ImageFont.truetype(font_path, 50)
        )

        image.save(template_path)
        print(f"Template criado em {template_path}")
    else:
        print(f"Template já existe em {template_path}, não será recriado.")
