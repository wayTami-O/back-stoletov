def get_openapi_schema(base_url: str = "") -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Portfolio API",
            "version": "1.0.0",
            "description": "API для проектов, отправки формы и соц. ссылок",
        },
        "servers": [{"url": base_url or "/"}],
        "paths": {
            "/api/projects/": {
                "get": {
                    "summary": "Список проектов",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Project"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/projects/{id}/": {
                "get": {
                    "summary": "Детали проекта",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Project"}
                                }
                            }
                        },
                        "404": {"description": "Not Found"}
                    }
                }
            },
            "/api/contact/": {
                "post": {
                    "summary": "Отправка сообщения формы",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/ContactRequest"}},
                            "application/x-www-form-urlencoded": {"schema": {"$ref": "#/components/schemas/ContactRequest"}},
                        }
                    },
                    "responses": {
                        "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OkResponse"}}}},
                        "400": {"description": "Bad Request"}
                    }
                }
            },
            "/api/social-links/": {
                "get": {
                    "summary": "Получить соц. ссылки",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SocialLinks"}}}
                        }
                    }
                },
                "post": {
                    "summary": "Обновить соц. ссылки",
                    "security": [{"AdminToken": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/SocialLinks"}},
                            "application/x-www-form-urlencoded": {"schema": {"$ref": "#/components/schemas/SocialLinks"}},
                        }
                    },
                    "responses": {
                        "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/OkResponse"}}}},
                        "401": {"description": "Unauthorized"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "AdminToken": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Admin-Token",
                    "description": "Shared admin token из настроек сервера",
                }
            },
            "schemas": {
                "Project": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "subtitle": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string", "enum": ["experience", "freelance", "personal"]},
                        "category_label": {"type": "string"},
                        "release_date": {"type": "string", "format": "date", "nullable": True},
                        "work_period": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string", "format": "date", "nullable": True},
                                "end": {"type": "string", "format": "date", "nullable": True}
                            }
                        },
                        "links": {
                            "type": "object",
                            "properties": {
                                "google_play": {"type": "string", "format": "uri", "nullable": True},
                                "rustore": {"type": "string", "format": "uri", "nullable": True},
                                "appstore": {"type": "string", "format": "uri", "nullable": True},
                                "github": {"type": "string", "format": "uri", "nullable": True},
                                "extra_social": {"type": "string", "format": "uri", "nullable": True}
                            }
                        },
                        "image": {"type": "string", "format": "uri", "nullable": True},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                },
                "ContactRequest": {
                    "type": "object",
                    "required": ["full_name", "email", "message"],
                    "properties": {
                        "full_name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "message": {"type": "string"}
                    }
                },
                "SocialLinks": {
                    "type": "object",
                    "properties": {
                        "telegram": {"type": "string", "format": "uri"},
                        "github": {"type": "string", "format": "uri"},
                        "linkedin": {"type": "string", "format": "uri"}
                    }
                },
                "OkResponse": {
                    "type": "object",
                    "properties": {"ok": {"type": "boolean"}}
                }
            }
        }
    }

