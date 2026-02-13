
import os
from flask import Flask, jsonify
from pydantic import BaseModel, RootModel
from typing import List, Optional
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from flask import Flask, jsonify
from pydantic import BaseModel, RootModel
from typing import List, Optional
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from dotenv import load_dotenv
from urllib.parse import quote_plus


# Cargar variables de entorno desde .env
load_dotenv()


# Configuración de la app Flask
app = Flask(__name__)

# Import necesarios para el endpoint de generación IA
from openai import AzureOpenAI
import json

# Configuración de la base de datos MySQL
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = quote_plus(os.getenv('DB_PASSWORD'))
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME')


app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo SocialMediaPost
# Modelo SocialMediaPost
default_length = 255
class SocialMediaPost(db.Model):
    __tablename__ = 'social_media_post'
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(default_length), nullable=False)
    title = db.Column(db.String(default_length), nullable=False)
    tone = db.Column(db.String(default_length), nullable=False)
    content = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.String(default_length), nullable=False)
    link = db.Column(db.String(default_length), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

# Pydantic Schemas

class SocialMediaPostCreateSchema(BaseModel):
    platform: str
    title: str
    tone: str
    content: str
    hashtags: str
    link: Optional[str] = None

class SocialMediaPostSchema(SocialMediaPostCreateSchema):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class SocialMediaPostSchemas(RootModel[List[SocialMediaPostSchema]]):
    pass

# Crear tablas automáticamente
with app.app_context():
    db.create_all()


# Endpoint de salud
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Endpoint GET /api/contents
@app.route('/api/contents', methods=['GET'])
def get_contents():
    posts = SocialMediaPost.query.all()
    posts_schema = SocialMediaPostSchemas([SocialMediaPostSchema.model_validate(post) for post in posts])
    return jsonify(posts_schema.model_dump())

# Endpoint GET /api/contents/<id>
@app.route('/api/contents/<int:post_id>', methods=['GET'])
def get_content(post_id):
    post = SocialMediaPost.query.get(post_id)
    if not post:
        return jsonify({'detail': 'Not found'}), 404
    return jsonify(SocialMediaPostSchema.model_validate(post).model_dump())

# Endpoint POST /api/contents
@app.route('/api/contents', methods=['POST'])
def create_content():
    from flask import request
    try:
        data = request.get_json(force=True)
        post_data = SocialMediaPostCreateSchema.model_validate(data, strict=False)
    except Exception:
        return jsonify({'detail': 'Invalid JSON'}), 400
    post = SocialMediaPost(
        platform=post_data.platform,
        title=post_data.title,
        tone=post_data.tone,
        content=post_data.content,
        hashtags=post_data.hashtags,
        link=post_data.link
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(SocialMediaPostSchema.model_validate(post).model_dump()), 201

# Endpoint POST /api/contents/generate
@app.route('/api/contents/generate', methods=['POST'])
def generate_content():
    from flask import request
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"detail": "Missing prompt"}), 400

        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un generador experto de contenidos para redes sociales. "
                        "Devuelve SIEMPRE un JSON estricto con las claves: platform, title, tone, content, hashtags. "
                        "No incluyas explicaciones ni texto adicional, solo el JSON."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        post = SocialMediaPost(
            platform=result["platform"],
            title=result["title"],
            tone=result["tone"],
            content=result["content"],
            hashtags=result["hashtags"],
            link=None
        )
        db.session.add(post)
        db.session.commit()

        return jsonify(SocialMediaPostSchema.model_validate(post).model_dump()), 201

    except Exception as e:
        return jsonify({"detail": f"Error al generar contenido: {str(e)}"}), 500
    
# Endpoint PUT /api/contents/<id>
@app.route('/api/contents/<int:post_id>', methods=['PUT'])
def update_content(post_id):
    from flask import request
    post = SocialMediaPost.query.get(post_id)
    if not post:
        return jsonify({'detail': 'Not found'}), 404
    try:
        data = request.get_json(force=True)
        post_data = SocialMediaPostCreateSchema.model_validate(data, strict=False)
    except Exception:
        return jsonify({'detail': 'Invalid JSON'}), 400
    post.platform = post_data.platform
    post.title = post_data.title
    post.tone = post_data.tone
    post.content = post_data.content
    post.hashtags = post_data.hashtags
    post.link = post_data.link
    db.session.commit()
    return jsonify(SocialMediaPostSchema.model_validate(post).model_dump())

# Endpoint DELETE /api/contents/<id>
@app.route('/api/contents/<int:post_id>', methods=['DELETE'])
def delete_content(post_id):
    post = SocialMediaPost.query.get(post_id)
    if not post:
        return jsonify({'detail': 'Not found'}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({'detail': 'Deleted'})

if __name__ == '__main__':
    app.run(debug=True)
