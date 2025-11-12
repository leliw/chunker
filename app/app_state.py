import asyncio
import logging
from dataclasses import dataclass
from typing import Dict

from ampf.base import BaseAsyncFactory
from ampf.gcp import GcpAsyncFactory, GcpSubscriptionPull, SubscriptionProcessor
from app_config import AppConfig
from features.embeddings.embedding_service import EmbeddingService

_log = logging.getLogger(__name__)


@dataclass
class AppSubscriptions:
    @property
    def subscriptions(self) -> Dict[str, GcpSubscriptionPull]:
        if not hasattr(self, "_subscriptions"):
            self._subscriptions: Dict[str, GcpSubscriptionPull] = {}
        return self._subscriptions

    def add_topic_subscription(
        self, topic_name: str | None, processor: SubscriptionProcessor
    ) -> GcpSubscriptionPull | None:
        if topic_name:
            return self.add_subscription(topic_name + "-sub", processor)

    def add_subscription(
        self, subscription_name: str | None, processor: SubscriptionProcessor
    ) -> GcpSubscriptionPull | None:
        if subscription_name:
            loop = asyncio.get_running_loop()
            subscription = GcpSubscriptionPull(subscription_name, processor, loop=loop)
            self.subscriptions[subscription_name] = subscription
            return subscription

    def run_subscriptions(self):
        for name, subscription in self.subscriptions.items():
            _log.info("Starting subscription: %s", name)
            subscription.run()

    def stop_subscriptions(self):
        for name, subscription in self.subscriptions.items():
            _log.info("Stopping subscription: %s", name)
            subscription.stop()

    def __enter__(self):
        self.run_subscriptions()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_subscriptions()


@dataclass
class AppState(AppSubscriptions):
    config: AppConfig
    async_factory: BaseAsyncFactory
    embedding_service: EmbeddingService

    @classmethod
    def create(cls, config: AppConfig):
        return cls(
            config=config,
            async_factory=GcpAsyncFactory(),
            embedding_service=EmbeddingService(config),
        )
