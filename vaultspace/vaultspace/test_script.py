import logging
import subprocess
import settings

logger = logging.getLogger(__name__)

def generate_pdf(input_html, output_pdf):
    try:
        result = subprocess.run([settings.WKHTMLTOPDF_CMD, input_html, output_pdf], check=True, capture_output=True)
        logger.info(f'wkhtmltopdf output: {result.stdout}')
        return output_pdf
    except subprocess.CalledProcessError as e:
        logger.error(f'wkhtmltopdf error: {e.stderr}')
        raise