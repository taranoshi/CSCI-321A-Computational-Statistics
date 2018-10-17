#! Christopher Ottesen
from projectq.ops import All, CNOT, H, Measure, X, Z
from projectq import MainEngine
import numpy as np


def create_bell_pair(quantum_engine):
    # Qubit one is 'Alices' qubit, and will be used to create a message state
    qubit_one = quantum_engine.allocate_qubit()
    # Qubit two is 'Bobs' qubit, and will be used to re-create the message state
    qubit_two = quantum_engine.allocate_qubit()
    H | qubit_one
    CNOT | (qubit_one, qubit_two)

    return qubit_one, qubit_two

def create_message(quantum_engine='', qubit_one='', message_value=0):
    qubit_to_send = quantum_engine.allocate_qubit()
    if message_value == 1:
        X | qubit_to_send

    # entangle the original qubit with the message qubit
    CNOT | (qubit_to_send, qubit_one)
    H | qubit_to_send
    Measure | qubit_to_send
    Measure | qubit_one

    # The qubits are now turned into normal bits we can send through classical channels
    classical_encoded_message = [int(qubit_to_send), int(qubit_one)]

    return classical_encoded_message

def message_reciever(quantum_engine, message, qubit_two):
    if message[1] == 1:
        X | qubit_two
    if message[0] == 1:
        Z | qubit_two
    
    Measure | qubit_two

    quantum_engine.flush()

    received_bit = int(qubit_two)
    return received_bit


def send_receive(bit=0,quantum_engine=''):
    # Create bell pair
    qubit_one, qubit_two = create_bell_pair(quantum_engine)
    # entangle the bit with the first qubit
    classical_encoded_message = create_message(quantum_engine=quantum_engine, qubit_one=qubit_one, message_value=bit)
    # Teleport the bit and return it back
    return message_reciever(quantum_engine, classical_encoded_message, qubit_two)


def send_full_message(message='DataEspresso.com',quantum_engine=''):
    # Convert the string into binary values
    binary_encoded_message = [bin(ord(x))[2:].zfill(8) for x in message]
    #print('Message to send: ', message)
    #print('Binary message to send: ', binary_encoded_message)

    received_bytes_list = []
    for letter in binary_encoded_message:
        received_bits = ''
        for bit in letter:
            received_bits = received_bits + str(send_receive(int(bit),quantum_engine))
        received_bytes_list.append(received_bits)

    binary_to_string = ''.join([chr(int(x, 2)) for x in received_bytes_list])
    #print('Received Binary message: ', received_bytes_list)
    #print('Received message: ', binary_to_string)
    return binary_to_string

# Using the simulator as quantum engine
quantum_engine=MainEngine()
wp = [
    "Hey,Babe", 
    "Hello,Honey", 
    "Read,SciFi", 
    "Watch,Romance", 
    "I,Love",
    "Hey,Sweety",
    "Read,Scifi",
    "Read,Manga",
    "I,Want",
    "I,Need",
    "I,Love",
    "How,Are"
    ]
rx = []
print("Sending data...")
i = 0
for xi in wp:
    print("{0}%".format((i / len(wp)*100)))
    rx.append(send_full_message(message=xi,quantum_engine=quantum_engine))
    i += 1
learn = {}
X = []
y = []
# learn = {"Hey" : [1 0 0 0]}
# where the list is the probs of second-coming words
# value will contain the words.
for w in rx:
    ws = w.split(",")
    X.append(ws[0])

for w in rx:
    ws = w.split(",")
    y.append(ws[1])

for x in X:
    if not (x in learn.keys()):
        learn[x] = [0.0 for i in range(len(X))]

# something is wrong with this algorithm. It needs to count the duplicates as higher probs

for i in range(len(X)):
    if X[i] in learn.keys():
        t = learn[X[i]]
        t[i] += 1.0
        learn[X[i]] = t
    
keys = learn.keys()
for k in keys:
    t = learn[k]
    learn[k] = [ts / sum(t) for ts in t]
print(learn)

# Alice sends a word to Bob, and Bob predicts:
rw = send_full_message(message="Hey",quantum_engine=quantum_engine)
print(learn[rw])
print("Recieved: {0} Predicted next word: {1} With the probabilities: {2}".format(rw, np.random.choice(value, 1, p=learn[rw]), learn[rw]))
