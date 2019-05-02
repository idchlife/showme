import os
import dataset
from ..config import DATABASE_PATH


DATABASE_URI = "sqlite:///" + DATABASE_PATH


db = dataset.connect(DATABASE_URI)