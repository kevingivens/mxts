from typing import Optional

from pydantic import BaseSettings, Field, BaseModel


class AppConfig(BaseModel):
    """Application configurations."""

    VAR_A: int = 33
    VAR_B: float = 22.0


class GlobalConfig(BaseSettings):
    """Global configurations."""

    # These variables will be loaded from the .env file. However, if
    # there is a shell environment variable having the same name,
    # that will take precedence.

    APP_CONFIG: AppConfig = AppConfig()

    # define global variables with the Field class
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")

    # environment specific variables do not need the Field class
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASS: Optional[str] = None

    class Config:
        """Loads the dotenv file."""
        env_file: str = ".env"


class DevConfig(GlobalConfig):
    """Development configurations."""

    class Config:
        env_prefix: str = "DEV_"


class ProdConfig(GlobalConfig):
    """Production configurations."""

    class Config:
        env_prefix: str = "PROD_"


class FactoryConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        elif self.env_state == "prod":
            return ProdConfig()


cnf = FactoryConfig(GlobalConfig().ENV_STATE)()


def parseConfig(argv: list = None) -> dict:
    pass
    
    # "--verbose", action="store_true", help="Run in verbose mode", default=False

    # "--load_accounts", action="store_true", help="Load accounts from exchanges", default=False,

    #"--trading_type",
    #    help='Trading Type in ("live", "sandbox", "simulation", "backtest")',
    #    choices=[_.lower() for _ in TradingType.members()],
    #    default="simulation",
    #
    #    "--strategies",
    #    action="append",
    #    nargs="+",
    #    help="Strategies to run in form <path.to.module:Class,args,for,strat>",
    #    default=[],

    #    "--exchanges",
    #    action="append",
    #    nargs="+",
    #    help="Exchanges to run on",
    #    default=[]
