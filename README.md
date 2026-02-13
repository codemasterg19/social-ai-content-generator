# Social AI Content Generator

Proyecto Flask para gestión de contenidos en redes sociales con MySQL y Pydantic.

## Despliegue local

1. **Clona el repositorio:**
   ```
   git clone https://github.com/codemasterg19/social-ai-content-generator.git
   cd social-ai-content-generator
   ```

2. **Crea y activa un entorno virtual:**
   ```
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Mac/Linux:
   source venv/bin/activate
   ```

3. **Instala dependencias:**
   ```
   pip install -r requirements.txt
   ```

4. **Copia y edita el archivo `.env` de ejemplo:**
   ```
   copy .env.example .env
   # O crea manualmente el archivo .env
   ```

5. **Ejecuta la app:**
   ```
   python m3_pablo_jimenez.py
   ```

## requirements.txt

Genera el archivo con:
```
pip freeze > requirements.txt
```

## Ejemplo de archivo `.env`

```
DB_HOST=localhost
DB_USER=usuario_mysql
DB_PASSWORD=tu_password
DB_NAME=social_ai
OPENAI_API_KEY=sk-xxxxxx
```

## Endpoints principales

- `GET /api/contents` — Lista todos los posts
- `POST /api/contents` — Crea un post
- `GET /api/contents/<id>` — Obtiene un post por id
- `PUT /api/contents/<id>` — Actualiza un post

- `POST /api/contents/generate` — Genera y guarda un post usando Azure OpenAI (ver detalles abajo)


## Endpoint IA: Generador de contenido

`POST /api/contents/generate`

Este endpoint utiliza Azure OpenAI para generar automáticamente un post para redes sociales y lo guarda en la base de datos.

**Request JSON:**
```json
{
   "prompt": "Crea un post para anunciar un nuevo producto tecnológico."
}
```

**Respuesta exitosa:**
```json
{
   "id": 5,
   "platform": "twitter",
   "title": "¡Nuevo producto tecnológico!",
   "tone": "emocionante",
   "content": "Descubre nuestro último lanzamiento en tecnología...",
   "hashtags": "#tecnología #innovación",
   "link": null,
   "created_at": "2024-02-13T12:34:56"
}
```

**Variables de entorno necesarias para Azure OpenAI:**
```
AZURE_OPENAI_ENDPOINT=https://<tu-endpoint>.openai.azure.com/
AZURE_OPENAI_KEY=tu_clave
AZURE_OPENAI_DEPLOYMENT=nombre_del_deployment
```

---
No subas tu archivo `.env` real a GitHub.
