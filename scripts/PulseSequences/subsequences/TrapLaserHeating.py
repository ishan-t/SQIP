from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict

class trap_laser_heating(pulse_sequence):
    
    required_parameters = [
                            ('Heating','ontrap_laser_duration'), 
                          ]
    
    #required_subsequences = [doppler_cooling]
    
    def sequence(self):
        h = self.parameters.Heating
        repump_duration = h.ontrap_laser_duration 
        if h.ontrap_laser_duration['s'] > 40e-9:
            self.addTTL ('Optical4', self.start, h.ontrap_laser_duration)
        self.end = self.start + repump_duration
        
