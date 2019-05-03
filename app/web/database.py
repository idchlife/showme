import os
import dataset
from ..config import DATABASE_PATH


DATABASE_URI = "sqlite:///" + DATABASE_PATH


db = dataset.connect(DATABASE_URI, engine_kwargs={
  # NOTE: Since db accessed via cli and daemon thread, we don't check for the same thread
  'connect_args': {
    'check_same_thread': False
  }
})
