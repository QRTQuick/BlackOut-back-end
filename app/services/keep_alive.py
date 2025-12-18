import asyncio
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self, url: str = None, interval: int = 180):  # 3 minutes = 180 seconds
        self.url = url or "https://your-app-name.onrender.com"  # Replace with your Render URL
        self.interval = interval
        self.running = False
        self.task = None
    
    async def ping_self(self):
        """Send a ping request to keep the server awake"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/api/ping", timeout=30) as response:
                    if response.status == 200:
                        logger.info(f"✅ Keep-alive ping successful at {datetime.now()}")
                    else:
                        logger.warning(f"⚠️ Keep-alive ping returned status {response.status}")
        except Exception as e:
            logger.error(f"❌ Keep-alive ping failed: {str(e)}")
    
    async def start_keep_alive(self):
        """Start the keep-alive loop"""
        self.running = True
        logger.info(f"🚀 Keep-alive service started - pinging every {self.interval} seconds")
        
        while self.running:
            await asyncio.sleep(self.interval)
            if self.running:  # Check again in case it was stopped during sleep
                await self.ping_self()
    
    def start(self):
        """Start the keep-alive service in background"""
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.start_keep_alive())
            logger.info("Keep-alive service task created")
    
    def stop(self):
        """Stop the keep-alive service"""
        self.running = False
        if self.task and not self.task.done():
            self.task.cancel()
            logger.info("Keep-alive service stopped")

# Global instance
keep_alive_service = KeepAliveService()