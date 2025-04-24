import logging
logger = logging.getLogger("supported_networks")
logger.setLevel(logging.DEBUG)
SUPPORTED_NETWORKS = [
    "ethereum", "solana", "base", "bsc", "polygon", "arbitrum",
    "optimism", "avalanche", "cronos", "zksync", "fantom",
    "mantle", "linea", "celo", "moonbeam", "moonriver",
    "harmony", "blast", "sonic", "scroll", "berachain", "monad"
]
