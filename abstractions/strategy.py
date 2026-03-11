"""
Strategy Pattern.

Defines a family of algorithms, encapsulates each one,
and makes them interchangeable at runtime.

Implements:
- Strategy interface
- Context for strategy execution
- Strategy registration and selection

SOLID Principles:
- Open/Closed: Add strategies without modification
- Liskov Substitution: Strategies are interchangeable
- Dependency Inversion: Context depends on abstraction
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class IStrategy(ABC, Generic[TInput, TOutput]):
    """
    Abstract strategy interface.

    Usage:
        class PaymentStrategy(IStrategy[Order, PaymentResult]):
            pass

        class CreditCardPayment(PaymentStrategy):
            def execute(self, order: Order) -> PaymentResult:
                # Process credit card payment
                return PaymentResult(success=True)

        class PayPalPayment(PaymentStrategy):
            def execute(self, order: Order) -> PaymentResult:
                # Process PayPal payment
                return PaymentResult(success=True)
    """

    @abstractmethod
    def execute(self, input: TInput) -> TOutput:
        """
        Execute the strategy.

        Args:
            input: Input data for the strategy.

        Returns:
            Strategy result.
        """
        pass


class IAsyncStrategy(ABC, Generic[TInput, TOutput]):
    """Async strategy interface."""

    @abstractmethod
    async def execute(self, input: TInput) -> TOutput:
        """Execute the strategy asynchronously."""
        pass


class StrategyContext(Generic[TInput, TOutput]):
    """
    Context for executing strategies.

    Usage:
        context = StrategyContext()
        context.set_strategy(CreditCardPayment())
        result = context.execute(order)

        # Change strategy at runtime
        context.set_strategy(PayPalPayment())
        result = context.execute(order)
    """

    def __init__(self, strategy: Optional[IStrategy[TInput, TOutput]] = None):
        self._strategy = strategy

    def set_strategy(self, strategy: IStrategy[TInput, TOutput]) -> None:
        """Set the current strategy."""
        self._strategy = strategy

    def execute(self, input: TInput) -> TOutput:
        """Execute current strategy."""
        if not self._strategy:
            raise ValueError("No strategy set")
        return self._strategy.execute(input)


class StrategyRegistry(Generic[TInput, TOutput]):
    """
    Registry for named strategies.

    Usage:
        registry = StrategyRegistry()
        registry.register("credit_card", CreditCardPayment())
        registry.register("paypal", PayPalPayment())
        registry.register("crypto", CryptoPayment())

        # Get strategy by name
        strategy = registry.get("paypal")
        result = strategy.execute(order)

        # Or use directly
        result = registry.execute("credit_card", order)
    """

    def __init__(self):
        self._strategies: Dict[str, IStrategy[TInput, TOutput]] = {}
        self._default: Optional[str] = None

    def register(
        self,
        name: str,
        strategy: IStrategy[TInput, TOutput],
        is_default: bool = False,
    ) -> "StrategyRegistry[TInput, TOutput]":
        """Register a strategy."""
        self._strategies[name] = strategy
        if is_default:
            self._default = name
        return self

    def get(self, name: str) -> IStrategy[TInput, TOutput]:
        """Get a strategy by name."""
        if name not in self._strategies:
            raise KeyError(f"Strategy not found: {name}")
        return self._strategies[name]

    def get_default(self) -> Optional[IStrategy[TInput, TOutput]]:
        """Get the default strategy."""
        if self._default:
            return self._strategies.get(self._default)
        return None

    def execute(self, name: str, input: TInput) -> TOutput:
        """Execute a named strategy."""
        return self.get(name).execute(input)

    def list_strategies(self) -> list:
        """List all registered strategy names."""
        return list(self._strategies.keys())


class ConditionalStrategy(IStrategy[TInput, TOutput]):
    """
    Strategy that selects based on conditions.

    Usage:
        strategy = ConditionalStrategy()
        strategy.when(lambda o: o.total > 1000, PremiumPayment())
        strategy.when(lambda o: o.is_international, InternationalPayment())
        strategy.default(StandardPayment())

        result = strategy.execute(order)  # Selects appropriate strategy
    """

    def __init__(self):
        self._conditions: list = []
        self._default: Optional[IStrategy[TInput, TOutput]] = None

    def when(
        self,
        condition: Callable[[TInput], bool],
        strategy: IStrategy[TInput, TOutput],
    ) -> "ConditionalStrategy[TInput, TOutput]":
        """Add a conditional strategy."""
        self._conditions.append((condition, strategy))
        return self

    def default(
        self,
        strategy: IStrategy[TInput, TOutput],
    ) -> "ConditionalStrategy[TInput, TOutput]":
        """Set default strategy."""
        self._default = strategy
        return self

    def execute(self, input: TInput) -> TOutput:
        """Execute matching strategy."""
        for condition, strategy in self._conditions:
            if condition(input):
                return strategy.execute(input)

        if self._default:
            return self._default.execute(input)

        raise ValueError("No matching strategy found")


class CompositeStrategy(IStrategy[TInput, list]):
    """
    Executes multiple strategies and combines results.

    Usage:
        composite = CompositeStrategy([
            TaxCalculation(),
            ShippingCalculation(),
            DiscountCalculation()
        ])

        results = composite.execute(order)  # [tax, shipping, discount]
    """

    def __init__(self, strategies: list):
        self._strategies = strategies

    def execute(self, input: TInput) -> list:
        """Execute all strategies."""
        return [s.execute(input) for s in self._strategies]


class FallbackStrategy(IStrategy[TInput, TOutput]):
    """
    Tries strategies in order until one succeeds.

    Usage:
        strategy = FallbackStrategy([
            PrimaryPaymentGateway(),
            SecondaryPaymentGateway(),
            OfflinePaymentHandler()
        ])

        result = strategy.execute(order)  # Tries each until success
    """

    def __init__(
        self,
        strategies: list,
        error_handler: Optional[Callable[[Exception], None]] = None,
    ):
        self._strategies = strategies
        self._error_handler = error_handler

    def execute(self, input: TInput) -> TOutput:
        """Execute strategies until one succeeds."""
        last_error: Optional[Exception] = None

        for strategy in self._strategies:
            try:
                return strategy.execute(input)
            except Exception as e:
                last_error = e
                if self._error_handler:
                    self._error_handler(e)
                continue

        raise last_error or ValueError("All strategies failed")


class LambdaStrategy(IStrategy[TInput, TOutput]):
    """
    Strategy from a lambda function.

    Usage:
        strategy = LambdaStrategy(lambda x: x * 2)
        result = strategy.execute(5)  # 10
    """

    def __init__(self, func: Callable[[TInput], TOutput]):
        self._func = func

    def execute(self, input: TInput) -> TOutput:
        return self._func(input)


def strategy(name: str):
    """
    Decorator to register a strategy.

    Usage:
        @strategy("credit_card")
        class CreditCardPayment(PaymentStrategy):
            def execute(self, order: Order) -> PaymentResult:
                ...
    """
    def decorator(cls: Type[IStrategy]) -> Type[IStrategy]:
        cls._strategy_name = name
        return cls
    return decorator
