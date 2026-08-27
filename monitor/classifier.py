import joblib, numpy as np      # imports joblib (library) for saving/loading large python objects & numpy for numerical matrix operations
from verifier import ThreatClass    # Imports a custom class or enum from another file within the project
import config                       # Imports from another local file config.py 

FEATURES = [        # Defining the list of string names that the model expects. Serves as an internal documentation
    'altitude_m','airspeed_mps','vertical_speed','pitch_rad','roll_rad',
    'engine_rpm','thrust_n','fuel_flow_kgps','g_load',
    'thrust_speed_ratio','climb_thrust_ratio','seq_delta','fuel_per_thrust'
]

class ThreatClassifier:     # Defines the blueprint for the object using OOP 
    def __init__(self):     # The constructor method to initalize the class state. 
        self.model  = joblib.load(config.MODEL_PATH)    # Reads the trained machine learning model from disk into RAM. This helps the reading of Files to be much quicker because the model sits ready in memory
        self.scaler = joblib.load(config.SCALER_PATH)   # Loads pre-fitted scaling parameters. Helps transform live data exactly the same way
        self.prev_seq = 0                               # Initalizes a counter variables to track sequence of numbers

    def predict(self, state:dict) -> 'tuple[ThreatClass, float]':   # Defines the prediction method state:dict & tells us it expects a dictionary
        seq_delta =  state['sequence_num'] - self.prev_seq          # Calculates gap between current sequence number and last tracked one
        self.prev_seq = state['sequence_num']                       # Updates tracker so the next packet is compared to this one
        feats = np.array([[                                         # Constructs a 2D NumPy array using two {{}}
            state['altitude_m'], state['airspeed_mps'], state['vertical_speed'],    # Extracts direct sensor readings from dictionary
            state['pitch_rad'],  state['roll_rad'],     state['engine_rpm'],        
            state['thrust_n'],   state['fuel_flow_kgps'], state['g_load'],          # Calculates ratio between thrust and speed
            state['thrust_n']        / (state['airspeed_mps'] + 1e-3),
            state['vertical_speed']  / (state['thrust_n']     + 1e-3),              # Derives climb efficency. 
            float(seq_delta),                                                       # Casts the sequence gap to a float
            state['fuel_flow_kgps']  / (state['thrust_n']     + 1e-3),   
        ]])
        fs      = self.scaler.transform(feats)                                      # Applies loaded scaling transformation to the 13 features.
        proba   = self.model.predict_proba(fs)[0]                                   # Generates an array of probabilities 
        pred    = int(np.argmax(proba))                                             # Finds the array index containing highest probability value
        return ThreatClass(pred), float(proba[pred])                                # Converts the raw integer into my strict ThreatClass enum & matches it with the float probability