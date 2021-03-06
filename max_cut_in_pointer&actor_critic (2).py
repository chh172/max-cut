# -*- coding: utf-8 -*-
"""max-cut-in-Pointer&Actor-Critic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1y5GfJISsZZ--RhSN0z3B48cs5NwfldwO
"""

import numpy as np
from networkx import *
import random
import tensorflow as tf
import matplotlib.pyplot as plt
import keras
import keras.backend as K
# from keras.engine import InputSpec
from tensorflow.keras.layers import InputSpec
from keras.activations import tanh, softmax
from keras.layers import LSTM

# copyright to https://github.com/keon/pointer-networks
class Attention(keras.layers.Layer):
    """
        Attention layer
    """

    def __init__(self, hidden_dimensions, name='attention'):
        super(Attention, self).__init__(name=name, trainable=True)
        self.W1 = keras.layers.Dense(hidden_dimensions, use_bias=False)
        self.W2 = keras.layers.Dense(hidden_dimensions, use_bias=False)
        self.V = keras.layers.Dense(1, use_bias=False)

    def call(self, encoder_outputs, dec_output, mask=None):

        w1_e = self.W1(encoder_outputs)
        w2_d = self.W2(dec_output)
        tanh_output = tanh(w1_e + w2_d)
        v_dot_tanh = self.V(tanh_output)
        #print(v_dot_tanh.shape)
        if mask is not None:
            v_dot_tanh += (mask * -1e9)
        attention_weights = softmax(v_dot_tanh, axis=1)
        att_shape = K.shape(attention_weights)
        return K.reshape(attention_weights, (att_shape[0], att_shape[1]))


class Decoder(keras.layers.Layer):
    """
        Decoder class for PointerLayer
    """

    def __init__(self, hidden_dimensions):
        super(Decoder, self).__init__()
        self.lstm = keras.layers.LSTM(
            hidden_dimensions, return_sequences=False, return_state=True)

    def call(self, x, hidden_states):
        dec_output, state_h, state_c = self.lstm(
            x, initial_state=hidden_states)
        return dec_output, [state_h, state_c]

    def get_initial_state(self, inputs):
        return self.lstm.get_initial_state(inputs)

    def process_inputs(self, x_input, initial_states, constants):
        return self.lstm._process_inputs(x_input, initial_states, constants)


class PointerLSTM(keras.layers.Layer):
    """
        PointerLSTM
    """

    def __init__(self, hidden_dimensions, name='pointer', **kwargs):
        super(PointerLSTM, self).__init__(**kwargs)
        self.hidden_dimensions = hidden_dimensions
        self.attention = Attention(hidden_dimensions)
        self.decoder = Decoder(hidden_dimensions)

    def build(self, input_shape):
        super(PointerLSTM, self).build(input_shape)
        self.input_spec = [InputSpec(shape=input_shape)]

    def call(self, x, training=None, mask=None, states=None):
        """
        :param Tensor x: Should be the output of the decoder
        :param Tensor states: last state of the decoder
        :param Tensor mask: The mask to apply
        :return: Pointers probabilities
        """

        input_shape = self.input_spec[0].shape
        en_seq = x
        x_input = x[:, input_shape[1] - 1, :]
        x_input = K.repeat(x_input, input_shape[1])
        if states:
            initial_states = states
        else:
            initial_states = self.decoder.get_initial_state(x_input)

        constants = []
        preprocessed_input, _, constants = self.decoder.process_inputs(
            x_input, initial_states, constants)
        constants.append(en_seq)
        last_output, outputs, states = K.rnn(self.step, preprocessed_input,
                                             initial_states,
                                             go_backwards=self.decoder.lstm.go_backwards,
                                             constants=constants,
                                             input_length=input_shape[1])

        return outputs

    def step(self, x_input, states):
        x_input = K.expand_dims(x_input,1)
        input_shape = self.input_spec[0].shape
        en_seq = states[-1]
        _, [h, c] = self.decoder(x_input, states[:-1])
        dec_seq = K.repeat(h, input_shape[1])
        probs = self.attention(dec_seq, en_seq)
        return probs, [h, c]

    def get_output_shape_for(self, input_shape):
        # output shape is not affected by the attention component
        return (input_shape[0], input_shape[1], input_shape[1])

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], input_shape[1])

import random 
from networkx import *
n = 6
p = 0.5
g = erdos_renyi_graph(n, p)
print(g. nodes)
# [0, 1, 2, 3, 4, 5] 
print(g. edges)
# [(0, 1), (0, 2), (0, 4), (1, 2), (1, 5), (3, 4), (4, 5)]
vertices = 5
A = adjacency_matrix(erdos_renyi_graph(vertices, 0.5)).todense()
print(A)
B = tf.concat([A,tf.zeros([1,5])],0)
print(B)
C = tf.concat([B,tf.zeros([6,1])],1)
print(C)

# Description: this function randomly generate a sequence of graphs G(V,E)
# where graphs are represented by their adjacency matrix A
# and the distribution of V and E are all uniform.
# It takes in 'number' of graphs, 'infimum' and 'supremum' of |V|. 
import numpy as np
from networkx import *
import random
def graph_seq_generator(num, inf, sup):
  atlas = []
  for i in range(num):
    A = adjacency_matrix(erdos_renyi_graph(np.random.randint(inf,sup), 0.5))
    #print(A.todense())
    atlas.append(A.todense())
  return atlas

import numpy as np
# Description: this function tensor-ize the atlas, preparing for LSTM
def input_generator(atlas):
  return tf.cast(np.array(random.sample(atlas,1)),tf.float32)

# Description: this function randomly generate a random graph G(V,E)
# where graph is represented by their adjacency matrix A, plus 'Split'

def graph_generator(vertices):
  A = adjacency_matrix(erdos_renyi_graph(vertices, 0.5)).todense()
  B = tf.concat([A,tf.zeros([1,vertices])],0)
  C = tf.concat([B,tf.zeros([vertices+1,1])],1)
  return tf.cast(np.array([C]),tf.float32)

print(graph_generator(5))

# Unit testing
# atlas = graph_seq_generator(4,1,5)
#print(atlas[1])
#inp = Input(atlas[1])
#print(inp)
#for i in range(3):
  #print(g[i].nodes)
  #
  #print(g[i].edges)
  #
  #print(len(g[i].nodes))
#g = random.sample(atlas,2)
#print(g[1])
#input = input_generator(atlas)
#input_2 = tf.cast(np.array([atlas[1]]),tf.float32)
#print(input)
#print(input_2)
#print(input.shape[0])
#print(input.shape[1])
#print(input.shape[2])
#print(input.shape)
#print(input.shape)
# x = Input(shape=(32,))
#x_1 = Input(input)
# print(x)
# print(graph_generator(5))
# print(tf.keras.Input(shape=(10,None,5),tensor=graph_generator(5)))
def increment(x):
  x = x +1
  return
x = 1
increment(x)
print(x)

# actor-critic training
# starting state: (0,0,...,0)
# action space = {action: flip a single bit in state} U {ternimate}
def actor_critic_algo(actor,critic,graph):
  # randomly init 'phi', 'theta'
  # do until theta converges (loop for every graph)
    # init starting state
    # \lambda = 1
    # do until reach terminal state
      # In state 's', select action 'a' given by actor
      # perform 'a' and collect reward r and new state (terminal state)
      # update delta
      # update value function parameter 'phi'
      # update policy parameter 'theta'
      # update discount 
      # update state
  return

def delta_update(critic,reward):
  return 

def value_f_update(critic, delta ,phi, beta):
  return phi+ beta*delta*value_grad(critic,phi)

def policy_update(actor,alpha,lamb,delta,theta):
  return theta + alpha*lamb*delta*policy_grad(actor,theta)
#  
def policy_grad(actor,theta):
  with tf.GradientTape() as tape:
    tape.watch(theta)
    y = tf.math.log(actor(theta))
  return tape.gradient(y,theta) 
def value_grad(critic,phi):
  with tf.GradientTape() as tape:
    tape.watch(phi)
    y = critic(phi)
  return tape.gradient(y, phi)

# training main in way 2

hidden_size = 128
vertices_size = 5

# input is a [A], where A is the adjacency matrix, which is a square matrix
# sequence length shall match the number of rows and feature_dim is number of cols
# note the feature for each node is its adjacency relation (row vector in adjacency matrix)
seq_len = vertices_size+1
feature_dim = vertices_size+1

encoder = LSTM(hidden_size,return_sequences = True, name="encoder",return_state=True)
actor_decoder = PointerLSTM( hidden_size, name="actor_decoder")
critic_decoder = LSTM(hidden_size,name="critic_decoder")

inputs = keras.layers.Input(shape=(seq_len, feature_dim)) 
encoder_o, state_h, state_c = encoder(inputs)
policy = actor_decoder(encoder_o,states=[state_h, state_c])
scores = critic_decoder(encoder_o)



#actor = tf.keras.Model(inputs=inputs, outputs=policy)

#critic = tf.keras.Model(inputs=inputs, outputs=scores)
model = tf.keras.Model(inputs=inputs, outputs=[policy,scores])
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
              loss=tf.keras.losses.Huber(),
              metrics=['accuracy'])
graph = graph_generator(5)
with tf.GradientTape() as tape:
  tape.watch(graph)
  y_p, y_c= model(graph)

grad = tape.gradient(y_p,graph)
print(grad)
# for i in range(5):
graph = graph_generator(vertices_size)
print(graph)
encoder_outputs, state_h, state_c = encoder(graph)
#print(encoder_outputs)
print("hello world")
policy = actor_decoder(encoder_outputs)
print(policy)
scores = critic_decoder(encoder_outputs)
print("hello world")
#print(scores)

import keras
keras.__version__

# training main in way 2

hidden_size = 4
vertices_size = 2

# input is a [A], where A is the adjacency matrix, which is a square matrix
# sequence length shall match the number of rows and feature_dim is number of cols
# note the feature for each node is its adjacency relation (row vector in adjacency matrix)
seq_len = vertices_size+1
feature_dim = vertices_size+1

encoder = LSTM(hidden_size,return_sequences = True, name="encoder",return_state=True)
actor_decoder = PointerLSTM( hidden_size, name="actor_decoder")
critic_decoder = LSTM(hidden_size,name="critic_decoder")

inputs = keras.layers.Input(shape=(seq_len, feature_dim)) 
encoder_o, state_h, state_c = encoder(inputs)
policy = actor_decoder(encoder_o,states=[state_h, state_c])
scores = critic_decoder(encoder_o)



#actor = tf.keras.Model(inputs=inputs, outputs=policy)

#critic = tf.keras.Model(inputs=inputs, outputs=scores)
model = tf.keras.Model(inputs=inputs, outputs=[policy,scores])
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
              loss=tf.keras.losses.Huber(),
              metrics=['accuracy'])

graph = graph_generator(vertices_size)
print(graph)
encoder_outputs, state_h, state_c = encoder(graph)
print(encoder_outputs)
print("hello world")
policy = actor_decoder(encoder_outputs)
print(policy)
scores = critic_decoder(encoder_outputs)
print("hello world")
#print(scores)
model.summary()