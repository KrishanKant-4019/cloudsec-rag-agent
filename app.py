import uvicorn

from app.config import get_settings


def main():
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=str(settings["host"]),
        port=int(settings["port"]),
        reload=False,
    )


if __name__ == "__main__":
    main()
