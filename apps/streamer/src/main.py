from .config import Config
from .streamer import Streamer

def main() -> None:
    cfg = Config()
    streamer = Streamer(cfg)
    streamer.run()

if __name__ == "__main__":
    main()
