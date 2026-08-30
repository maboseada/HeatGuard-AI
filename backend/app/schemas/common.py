from enum import Enum

class JobStatus(str, Enum):
    pending = "Pending"
    processing = "Processing"
    completed = "Completed"
    failed = "Failed"

class AnalysisType(str, Enum):
    heatmap = "heatmap"
    environmental = "environmental"

class Granularity(int, Enum):
    g60 = 60
    g80 = 80
    g100 = 100
