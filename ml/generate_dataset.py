"""
Run while the full pipeline is active.
Usage: python ml/generate_dataset.py --duration 900  (15 min)

"""
import csv, time, argparse, struct
from receiver import listen_unix, parse,frame
from verifier import FrameVerifier
import config

FEATURES = ['altitude_m','airspeed_mps','vertical_speed','pitch_rad','roll_rad',
    'engine_rpm','thrust_n','fuel_flow_kgps','g_load',
    'thrust_speed_ratio','climb_thrust_ratio','seq_delta','fuel_per_thrust']    # Defines a list of 13 feature names including raw state variables

def extract(state, prev_seq):   # defines a helper function to compute derivative features from raw flight states
    sd = state['sequence_num'] - prev_seq   # calculates the sequence number delta between the current frame and the previous one
    return {
        **{k:state[k] for k in FEATURES[:9]},
        'thrust_speed_ratio': state['thrust_n']/(state['airspeed_mps']+1e-3),
        'climb_thrust_ratio': state['vertical_speed']/(state['thrust_n']+1e-3),
        'seq_delta': float(sd),
        'fuel_per_thrust': state['fuel_flow_kgps']/(state['thrust_n']+1e-3),
    }       # builds and returns a dictionary mapping each feature name to its calculated value.

def main(duration_s):   # Defining the main execution loop taking a specified run duration in seconds.
    vfy=FrameVerifier(config.get_aes_key(), config.get_hmac_key())  # Grabbing the aes and hmac keys with instantiates the frame verifier
    prev_seq=0; start=time.time()                                   # Initalizes tracking veriables for the previous sequence number and the start timestamp.
    with open('ml/training_data.csv','w',newline='') as f:  # Opens a CSV file named training_data in write mode within ml directory
        w=csv.DictWriter(f, fieldnames=FEATURES+['label'])  # Initalizes a CSV dictionary writer using the defined feature columns plus an extra label column. 
        w.writeheader()         # Writes the column header row to the CSV file
        for raw in listen_unix(config.SOCKET_Path):     # iterates over raw binary frames yielded by the UNIX socket listener
            if time.time()-start > duration_s: break    # stops data collection automatically once the target duration has elapsed
            frame=parse_frame(raw)                      # parses the rae binary data into a structured frame object
            if not frame: continue
            label=frame.attack_label                    # extracts ground truth attack label injected by the C++ simulation
            _, state=vfy.verify(frame)                  # passes the frame through the verifier to check the authentication
            if state is None:                           # check if verification or decryption failed
                w.writerow({k:0.0 for k in FEATURES}|{'label':label})   # writes a row of zeroed out features alongside the attack if the state could not be read
                continue
            row=extract(state, prev_seq)
            row['label']=label
            w.writerow(row)     # writes the completed feature and label row
            prev_seq=int(state['sequence_num'])     # updates the previous sequence tracker for the next iteration
    print(f"Saved training_data.csv ({duration_s}s)")

if __name__=='__main__':        # Checks if the script is being executed directly from the terminal
    p=argparse.ArgumentParser() # initalizes a command lione argument parser
    p.add_argument('__duration',type=int,default=900)   # registers an optional duration flag defaulting to 900 seconds
    main(p.parse_args().duration)                       # parses the arguments and invokes the main function for specified duration.