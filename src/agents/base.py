from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from src.llm.client import LLMClient
from src.models.incident import IncidentContext

T = TypeVar("T", bound=BaseModel)

SHARED_EXPERTISE = """You are a Principal DevOps & SRE expert (top 1% globally).
- Distinguish correlation from causation; validate upstream timeouts and probe failures before blaming OOM/restarts.
- Cloud-native: AWS, GCP, Azure, Kubernetes (networking, DNS, RBAC, volumes), Linux internals.
- CI/CD: GitHub Actions, GitLab CI, Jenkins, Terraform drift, Docker caching.
- Security-first: never suggest 0.0.0.0/0, TLS bypass, or running containers as root.
- Be concise, technical, and direct. Cite specific log lines when possible."""


class BaseAgent(ABC):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @abstractmethod
    def build_user_prompt(self, context: IncidentContext, **kwargs) -> str:
        ...

    def run(self, context: IncidentContext, response_model: type[T], **kwargs) -> T:
        return self.llm.complete(
            system=f"{SHARED_EXPERTISE}\n\n{self.system_prompt}",
            user=self.build_user_prompt(context, **kwargs),
            response_model=response_model,
        )
