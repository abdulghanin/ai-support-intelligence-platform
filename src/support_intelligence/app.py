import  logging

logger = logging.getLogger(__name__)



def  get_app_name() -> str:

    logger.info("Reading application name")

    return "AI Support Intelligence Platform"


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    print(get_app_name())

