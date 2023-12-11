import connexion
import six

from swagger_server.models.game import Game  # noqa: E501
from swagger_server import util
import connexion
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
import time
from prometheus_client import Counter, Histogram, Gauge
import random
import logging
import json
from datetime import datetime
from flask.logging import default_handler
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
            # You can add more fields here as needed
        }
        return json.dumps(log_record)
# Set up application-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_handler = logging.FileHandler('lokiprom/app.log')
log_handler.setFormatter(JsonFormatter())

logger.addHandler(log_handler)
logger.addHandler(default_handler)  # Keep the default handler if needed
# Import your OpenTelemetry code here
    # Configure tracing
trace_provider = TracerProvider()
trace.set_tracer_provider(trace_provider)

    # Configure Jaeger Exporter
jaeger_exporter = JaegerExporter(
        # You can customize the endpoint and other parameters if needed
    agent_host_name='localhost',
    agent_port=6831,
)

trace_provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
tracer = trace.get_tracer(__name__)
# Create a meter from the global meter provider
meter = metrics.get_meter(__name__)
# Create a counter instrument for counting the number of times each operation is called
# games_get_counter = meter.create_counter(
#     "games.controller.get_counter",
#     unit="1",
#     description="Counts the number of times games_get is called",
# )
# games_post_counter = meter.create_counter(
#     "games.controller.post_counter",
#     unit="1",
#     description="Counts the number of times games_post is called",
# )
# Create counter metrics for tracking controller operations
games_get_counter = Counter('games_controller_get_requests_total', 'Total number of games_get requests')
games_post_counter = Counter('games_controller_post_requests_total', 'Total number of games_post requests')
games_get_duration_histogram = Histogram(
    'games_controller_get_duration_seconds',
    'Duration of games_get requests in seconds',
)
games_post_duration_histogram = Histogram(
    'games_controller_post_duration_seconds',
    'Duration of games_post requests in seconds',
)
request_duration_metric = Gauge('api_request_duration_seconds', 'Request processing time in seconds')
# Increment the total API requests counter
requests_counter = Counter('api_requests_total', 'Total number of API requests')
# Mock data for Game objects
games = [
    Game(id=1, title="Game 1", price=29.99),
    Game(id=2, title="Game 2", price=39.99),
    Game(id=3, title="Game 3", price=19.99),
]

def games_get():  # noqa: E501
    """Get a list of games

    Retrieve a list of games available in the shop. # noqa: E501

    :rtype: List[Game]
    """
    with tracer.start_as_current_span("games_get") as span:
        games_get_counter.inc() # Increment the counter
        requests_counter.inc()
        # Record the start time
        start_time = time.time()
        # Simulate some processing time
        sleep_duration = random.uniform(1, 3)
        time.sleep(sleep_duration)
        # Log that the POST method was called
        logger.info(f"GET method called - Get games")
        try:
            # Actual operation logic
            games_list = games
        except Exception as e:
            # Log or handle any exceptions
            print(f"Error in games_get: {str(e)}")
            logger.error(f"Error in games_get: {str(e)}")
            games_list = []

        # Record the end time
        end_time = time.time()

        # Calculate the duration
        duration_ms = (end_time - start_time) * 1000
        # Add request duration to the gauge metric
        request_duration_metric.set(duration_ms)
        games_get_duration_histogram.observe(duration_ms)
        # Add the duration as an attribute to the span
        span.set_attribute("operation.duration_ms", duration_ms)

        return games_list


def games_id_delete(game_id):  # noqa: E501
    """Delete a game by ID

    Delete a game by its ID. # noqa: E501

    :param id: ID of the game
    :type id: int

    :rtype: None
    """
    global games
    requests_counter.inc()
    games = [game for game in games if game.id != game_id]
    return games

def games_id_get(game_id):  # noqa: E501
    """Get a game by ID

    Retrieve a game by its unique ID. # noqa: E501

    :param id: ID of the game
    :type id: int

    :rtype: Game
    """
    requests_counter.inc()
    for game in games:
        if game.id == game_id:
            return game
    return None  # Return None if the game with the given ID is not found

def games_id_put(body, game_id):  # noqa: E501
    """Update a game by ID

    Update an existing game by its ID. # noqa: E501

    :param body: Updated game details
    :type body: dict | bytes
    :param id: ID of the game
    :type id: int

    :rtype: Game
    """
    requests_counter.inc()
    global games
    if connexion.request.is_json:
        updated_game = Game.from_dict(connexion.request.get_json())  # noqa: E501
        for i, game in enumerate(games):
            if game.id == game_id:
                # Update the game with the new details
                games[i] = updated_game
                return updated_game
    return None  # Return None if the game with the given ID is not found

def games_post(body):  # noqa: E501
    """Add a new game

    Add a new game to the shop. # noqa: E501

    :param body: Game details
    :type body: dict | bytes

    :rtype: Game
    """
    
    if connexion.request.is_json:
        with tracer.start_as_current_span("games_post") as span:
            games_post_counter.inc()
            requests_counter.inc()
            start_time = time.time()
            # Simulate some processing time
            sleep_duration = random.uniform(1, 3)
            time.sleep(sleep_duration)
            new_game = Game.from_dict(connexion.request.get_json())  # noqa: E501
            # Assign a new ID for the new game (you might want to generate a unique ID)
            new_game.id = len(games) + 1
            games.append(new_game)
            end_time = time.time()
            duration_seconds = end_time - start_time
            games_post_duration_histogram.observe(duration_seconds)
            span.set_attribute("operation.duration_ms", duration_seconds)
            return new_game

