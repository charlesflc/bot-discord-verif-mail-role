import asyncio
from config import bot, logger, TOKEN

async def main():
    logger.info("Démarrage du bot...")
    
    # Charger l'extension commands de manière asynchrone
    await bot.load_extension("commands")
    
    # Démarrer le bot
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
