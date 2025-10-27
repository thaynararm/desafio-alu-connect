# tasks.py
from celery import shared_task
from course.models import Student, Course
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from google import genai
from student.models import StudentCertificate
import logging
import textwrap

logger = logging.getLogger(__name__)

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("Variável GEMINI_API_KEY não encontrada no ambiente!")
        raise ValueError("Chave de API ausente.")

    client = genai.Client(api_key=api_key)
except Exception as e:
    logger.error(f"Erro ao inicializar o cliente Gemini: {e}")
    client = None


@shared_task
def generate_certificate(student_id, course_id):
    student = Student.objects.get(id=student_id)
    course = Course.objects.get(id=course_id)

    try:
        prompt = (
            f"Gere um texto inspirador e curto para inserir no certificado de conclusão de curso "
            f"para o aluno {student.user.full_name} que concluiu o curso '{course.title}'. "
            "Retorne apenas o texto puro, sem Markdown, negrito, itálico, links, emojis ou caracteres especiais."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        certificate_text = response.text
    except Exception as e:
        print(f"Erro ao gerar texto via LLM: {e}")
        certificate_text = f"Certificamos que {student.user.full_name} concluiu o curso {course.title}."

    template_path = os.path.join(
        settings.MEDIA_ROOT, "media/templates", "template_certificate.png"
    )
    if not os.path.exists(template_path):
        print(f"Template de certificado não encontrado em {template_path}")
        return

    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)

    font_path = "C:/Windows/Fonts/arial.ttf"
    font_size = 36
    font = ImageFont.truetype(font_path, font_size)

    lines = []
    for paragraph in certificate_text.split("\n"):
        wrapped = textwrap.wrap(paragraph, width=40)
        lines.extend(wrapped)
        lines.append("")

    total_text_height = sum(
        [draw.textbbox((0, 0), line, font=font)[3] + 10 for line in lines]
    )
    y_text = (image.height - total_text_height) / 2

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:4]
        draw.text(((image.width - w) / 2, y_text), line, font=font, fill="black")
        y_text += h + 10

    output_dir = os.path.join(settings.MEDIA_ROOT, "certificates")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{student.uuid}_{course.uuid}.png"
    output_path = os.path.join(output_dir, filename)
    image.save(output_path)

    StudentCertificate.objects.update_or_create(
        student=student,
        course=course,
        defaults={"file": f"certificates/{filename}", "text": certificate_text},
    )

    logger.info(
        f"Certificado visual gerado para {student.user.full_name} em {output_path}"
    )
