from functools import lru_cache

from elasticsearch import Elasticsearch

from config.settings import get_settings

""" Elasticsearch 客户端 """
@lru_cache
def get_elasticsearch_client() -> Elasticsearch:
    settings = get_settings()

    kwargs: dict = {
        "hosts": [settings.es_url],
        "verify_certs": settings.es_verify_certs,
        "request_timeout": 30,
    }

    if settings.es_username:
        kwargs["basic_auth"] = (settings.es_username, settings.es_password)

    return Elasticsearch(**kwargs)