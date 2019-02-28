import numpy as np
import math
import itertools
from copy import deepcopy
import operator
from spinn_front_end_common.utilities.globals_variables import get_simulator
import traceback
import csv
from ast import literal_eval

class neuron_population(object):
    def __init__(self,
                 v_rest=-65.0,  # Resting membrane potential in mV.
                 v_rest_stdev=0,
                 cm=1.0,  # Capacity of the membrane in nF
                 cm_stdev=0,
                 tau_m=20.0,  # Membrane time constant in ms.
                 tau_m_stdev=0,
                 tau_refrac=0.1,  # Duration of refractory period in ms.
                 tau_refrac_stdev=0,
                 tau_syn_E=0.3,  # Rise time of the excitatory synaptic alpha function in ms.
                 tau_syn_E_stdev=0,
                 tau_syn_I=0.5,  # Rise time of the inhibitory synaptic alpha function in ms.
                 tau_syn_I_stdev=0,
                 e_rev_E=0.0,  # Reversal potential for excitatory input in mV
                 e_rev_E_stdev=0,
                 e_rev_I=-70.0,  # Reversal potential for inhibitory input in mV
                 e_rev_I_stdev=0,
                 v_thresh=-50.0,  # Spike threshold in mV.
                 v_thresh_stdev=0,
                 v_reset=-65.0,  # Reset potential after a spike in mV.
                 v_reset_stdev=0,
                 i_offset=0.0,  # Offset current in nA
                 i_offset_stdev=0,
                 default=True,
                 io_prob=1,
                 inputs=0,
                 outputs=0,
                 ex_prob=0.5,
                 read_population=False,
                 pop_size=200
                 ):

        # neuron params
        self.v_rest = v_rest
        self.v_rest_stdev = v_rest_stdev
        self.cm = cm
        self.cm_stdev = cm_stdev
        self.tau_m = tau_m
        self.tau_m_stdev = tau_m_stdev
        self.tau_refrac = tau_refrac
        self.tau_refrac_stdev = tau_refrac_stdev
        self.tau_syn_E = tau_syn_E
        self.tau_syn_E_stdev = tau_syn_E_stdev
        self.tau_syn_I = tau_syn_I
        self.tau_syn_I_stdev = tau_syn_I_stdev
        self.e_rev_E = e_rev_E
        self.e_rev_E_stdev = e_rev_E_stdev
        self.e_rev_I = e_rev_I
        self.e_rev_I_stdev = e_rev_I_stdev
        self.v_thresh = v_thresh
        self.v_thresh_stdev = v_thresh_stdev
        self.v_reset = v_reset
        self.v_reset_stdev = v_reset_stdev
        self.i_offset = i_offset
        self.i_offset_stdev = i_offset_stdev

        self.io_prob = io_prob
        self.outputs = outputs
        self.inputs = inputs
        self.ex_prob = ex_prob
        self.pop_size = pop_size

        self.neuron_params = {}
        self.neuron_params['v_rest'] = self.v_rest
        self.neuron_params['cm'] = self.cm
        self.neuron_params['tau_m'] = self.tau_m
        self.neuron_params['tau_refrac'] = self.tau_refrac
        self.neuron_params['tau_syn_E'] = self.tau_syn_E
        self.neuron_params['tau_syn_I'] = self.tau_syn_I
        self.neuron_params['v_thresh'] = self.v_thresh
        self.neuron_params['v_reset'] = self.v_reset
        self.neuron_params['i_offset'] = self.i_offset

        self.neuron_param_stdevs = {}
        self.neuron_param_stdevs['v_rest'] = self.v_rest_stdev
        self.neuron_param_stdevs['cm'] = self.cm_stdev
        self.neuron_param_stdevs['tau_m'] = self.tau_m_stdev
        self.neuron_param_stdevs['tau_refrac'] = self.tau_refrac_stdev
        self.neuron_param_stdevs['tau_syn_E'] = self.tau_syn_E_stdev
        self.neuron_param_stdevs['tau_syn_I'] = self.tau_syn_I_stdev
        self.neuron_param_stdevs['v_thresh'] = self.v_thresh_stdev
        self.neuron_param_stdevs['v_reset'] = self.v_reset_stdev
        self.neuron_param_stdevs['i_offset'] = self.i_offset_stdev
        default_check = 0
        for param in self.neuron_param_stdevs:
            default_check += self.neuron_param_stdevs[param]
        if not default_check:
            default = True
        if default:
            for param in self.neuron_param_stdevs:
                self.neuron_param_stdevs[param] = 0
            pop_size = self.inputs + self.outputs + 1

        self.neuron_configs = {}
        self.neurons_generated = -1  # counting backwards to avoid any confusion with motifs
        self.total_weight = 0

        if read_population:
            print "reading the population"
        else:
            for i in range(self.inputs + self.outputs):
                neuron = {}
                if np.random.random() < io_prob:
                    io_choice = np.random.randint(self.inputs + self.outputs)
                    if io_choice - self.inputs < 0:
                        neuron['type'] = 'input{}'.format(io_choice)
                    else:
                        neuron['type'] = 'output{}'.format(io_choice - self.inputs)
                else:
                    if np.random.random() < self.ex_prob:
                        neuron['type'] = 'excitatory'
                    else:
                        neuron['type'] = 'inhibitory'
                neuron['weight'] = 1
                neuron['params'] = {}
                for param in self.neuron_params:
                    neuron['params'][param] = np.random.normal(self.neuron_params[param], self.neuron_param_stdevs[param])
            for i in range(self.inputs + self.outputs, self.pop_size):
                not_new = True
                while not not_new:
                    neuron = {}
                    if np.random.random() < io_prob:
                        io_choice = np.random.randint(self.inputs + self.outputs)
                        if io_choice - self.inputs < 0:
                            neuron['type'] = 'input{}'.format(io_choice)
                        else:
                            neuron['type'] = 'output{}'.format(io_choice - self.inputs)
                    else:
                        if np.random.random() < self.ex_prob:
                            neuron['type'] = 'excitatory'
                        else:
                            neuron['type'] = 'inhibitory'
                    if default:
                        neuron['weight'] = ((self.inputs + self.outputs) / self.io_prob) - (self.inputs + self.outputs)
                    else:
                        neuron['weight'] = 1
                    neuron['params'] = {}
                    for param in self.neuron_params:
                        neuron['params'][param] = np.random.normal(self.neuron_params[param], self.neuron_param_stdevs[param])
                    not_new = self.check_neuron(neuron)
                self.insert_neuron(neuron, check=False)

    def generate_neuron(self):
        found_new = False
        while not found_new:
            neuron = {}
            if np.random.random() < self.io_prob:
                io_choice = np.random.randint(self.inputs + self.outputs)
                if io_choice - self.inputs < 0:
                    neuron['type'] = 'input{}'.format(io_choice)
                else:
                    neuron['type'] = 'output{}'.format(io_choice - self.inputs)
            else:
                if np.random.random() < self.ex_prob:
                    neuron['type'] = 'excitatory'
                else:
                    neuron['type'] = 'inhibitory'
            neuron['weight'] = 1
            neuron['params'] = {}
            for param in self.neuron_params:
                neuron['params'][param] = np.random.normal(self.neuron_params[param], self.neuron_param_stdevs[param])
            neuron['id'] = self.neurons_generated
            if not self.check_neuron(neuron):
                neuron_id = self.insert_neuron(neuron, check=False)
                found_new = True
        return neuron_id

    def insert_neuron(self, neuron, check=True):
        if check:
            repeat_check = self.check_neuron(neuron)
            if repeat_check:
                return repeat_check
            else:
                self.total_weight += neuron['weight']
                self.neuron_configs['{}'.format(self.neurons_generated)] = neuron
                self.neurons_generated -= 1
        else:
            self.total_weight += neuron['weight']
            self.neuron_configs['{}'.format(self.neurons_generated)] = neuron
            self.neurons_generated -= 1
        return '{}'.format(self.neurons_generated + 1)

    def check_neuron(self, new_neuron):
        for neuron in self.neuron_configs:
            the_same = False
            for param in neuron:
                if neuron[param] == new_neuron[param] or param == 'id' or param == 'weight':
                    the_same = True
                else:
                    the_same = False
                    break
            if the_same:
                return neuron['id']
        return False

    def choose_neuron(self):
        if not self.total_weight:
            for neuron in self.neuron_configs:
                self.total_weight += self.neuron_configs[neuron]['weight']
        choice = np.random.random() * self.total_weight
        for neuron in self.neuron_configs:
            choice -= self.neuron_configs[neuron]['weight']
            if choice < 0:
                break
        return neuron

    def return_neuron(self, neuron_id):
        return self.neuron_configs[neuron_id]



