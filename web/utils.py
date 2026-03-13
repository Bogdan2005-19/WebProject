from datetime import datetime
import requests
from .models import Videojuego, Genero

CLIENT_ID = "9vfzl5tc1x9ekb58ahdtg14og1ecmp"
CLIENT_SECRET = "fr4k4hthydicvx8p5zskmrj4t3aqgz"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
API_URL = "https://api.igdb.com/v4/games"

def obtener_token():
    """Obtiene un token de acceso para la API de IGDB"""
    response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    })
    return response.json().get("access_token")

def importar_juegos_desde_igdb():
    """Importa juegos desde IGDB y los guarda en la base de datos"""
    token = obtener_token()
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    query = """
        fields name, summary, first_release_date, aggregated_rating, genres.name, cover.url;
        where aggregated_rating > 40;
        limit 500;
    """

    response = requests.post(API_URL, headers=headers, data=query)

    if response.status_code == 200:
        data = response.json()
        for game in data:
            # Convertir la fecha de lanzamiento (si existe) de timestamp a datetime
            fecha_lanzamiento = game.get("first_release_date")
            if fecha_lanzamiento:
                try:
                    fecha_lanzamiento = datetime.fromtimestamp(fecha_lanzamiento)
                except ValueError:
                    fecha_lanzamiento = None  # Si hay un error al convertir la fecha, la dejamos como None

            # Obtener la URL completa de la imagen (si existe)
            imagen_url = game.get("cover", {}).get("url", "")
            if imagen_url:
                if not imagen_url.startswith("http"):
                    imagen_url = "https:" + imagen_url  # Completar la URL si es relativa
                if "t_thumb" in imagen_url:
                    imagen_url = imagen_url.replace("t_thumb", "t_1080p")  # Usar t_1080p si está disponible
                elif "t_cover_small" in imagen_url:
                    imagen_url = imagen_url.replace("t_cover_small", "t_1080p")

                # Crear los géneros o buscar los existentes
                generos = []
                for genre_data in game.get("genres", []):
                    genero_nombre = genre_data["name"]
                    genero, created = Genero.objects.get_or_create(nombre=genero_nombre)
                    generos.append(genero)

                # Usar update_or_create solo si la imagen existe
                videojuego, created = Videojuego.objects.update_or_create(
                    titulo=game.get("name"),
                    defaults={
                        'portada': imagen_url,
                        'fecha_lanzamiento': fecha_lanzamiento,
                        'rating': game.get("aggregated_rating"),
                        'descripcion': game.get("summary", "")
                    }
                )

                if created:
                    videojuego.genero.set(generos)  # Asignar los géneros a través de la relación ManyToMany
                    print(f"✅ Juego creado: {videojuego.titulo}")
                else:
                    videojuego.genero.set(generos)
                    print(f"🔄 Juego actualizado: {videojuego.titulo}")
            else:
                print(f"❌ Juego sin imagen: {game['name']} no se ha importado.")

        print("✅ Juegos importados o actualizados con éxito")
    else:
        print(f"❌ Error al obtener juegos: {response.status_code}")


NEWS_API_KEY = 'pub_78670010e7e9dc763d072171bfec442ce08dc'
NEWS_URL = 'https://newsdata.io/api/1/news'

def obtener_noticias_videojuegos():
    """Obtiene noticias sobre videojuegos desde la API de NewsData"""
    noticias = []
    try:
        params = {
            'apikey': NEWS_API_KEY,
            'q': 'videojuegos',
            'language': 'es',
            'category': 'technology',
        }
        response = requests.get(NEWS_URL, params=params)
        response.raise_for_status()
        resultados = response.json().get('results', [])

        # Usamos un conjunto para almacenar títulos únicos
        titulos_vistos = set()
        noticias_unicas = []

        for noticia in resultados:
            titulo = noticia['title']

            if titulo not in titulos_vistos:
                titulos_vistos.add(titulo)
                noticias_unicas.append(noticia)

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener noticias: {e}")
    except ValueError as e:
        print(f"Error al procesar los datos JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return noticias_unicas[:4]

def juegos_similares(videojuego):
    """Obtiene juegos similares basados en el género del videojuego dado"""
    generos = videojuego.genero.all()
    if generos.exists():
        genero = generos.first()  # Tomamos el primer género para buscar juegos similares
        juegos_similares = Videojuego.objects.filter(genero=genero).exclude(id=videojuego.id)[:6]
        return juegos_similares
    return []