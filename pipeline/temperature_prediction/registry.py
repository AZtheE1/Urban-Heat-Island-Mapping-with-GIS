"""Registry for swappable temperature prediction models."""

from .linear_regression import LinearRegressionPredictor

PREDICTOR_REGISTRY = {
    LinearRegressionPredictor.name: LinearRegressionPredictor,
}

DEFAULT_PREDICTOR = LinearRegressionPredictor.name


def get_predictor(model_name=None):
    """Instantiate a registered predictor by name."""
    name = model_name or DEFAULT_PREDICTOR
    predictor_cls = PREDICTOR_REGISTRY.get(name)
    if predictor_cls is None:
        available = ", ".join(sorted(PREDICTOR_REGISTRY))
        raise ValueError(f"Unknown model '{name}'. Available models: {available}")
    return predictor_cls()
