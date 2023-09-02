
import librosa.display
from td_utils import *
from keras.callbacks import ModelCheckpoint
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Activation, Dropout, Input, Masking, TimeDistributed, LSTM, Conv1D
from keras.layers import GRU, Bidirectional, BatchNormalization, Reshape
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import os 
import pandas as pd
import numpy as np
from keras.utils import Sequence

# get_ipython().run_line_magic('matplotlib', 'inline')



class DataGenerator(Sequence):
    def __init__(self, df, batch_size, shuffle = True):
        self.X = list(df.x)
        self.y = list(df.y)
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()
        
    def on_epoch_end(self):
        self.indexes = np.arange(len(self.X))
        if self.shuffle:
            np.random.shuffle(self.indexes)
            
    def __len__(self):
        return int(np.floor(len(self.X) / self.batch_size))
    
    def __data_generation(self, X_list, y_list):
        X = []
        y = []
        for i, (img, label) in enumerate(zip(X_list, y_list)):
            X.append(np.load(img))
            y.append(np.load(label))
        
        X = np.stack(X, axis=0)
        y = np.stack(y, axis=0)

        return X, y
        
    def __getitem__(self, index):
        indexes = self.indexes[index * self.batch_size : (index + 1) * self.batch_size]
        X_list = [self.X[k] for k in indexes]
        y_list = [self.y[k] for k in indexes]
        X, y = self.__data_generation(X_list, y_list)
        return X, y




# # Train
def make_model(input_shape):
    
    X_input = Input(shape = input_shape)
    X = Conv1D(196, kernel_size=15, strides=4)(X_input)         # CONV1D
    X = BatchNormalization()(X)                                 # Batch normalization
    X = Activation('relu')(X)                                   # ReLu activation
    X = Dropout(0.8)(X)                                         # dropout (use 0.8)

    X = GRU(units = 128, return_sequences = True)(X)            # GRU (use 128 units and return the sequences)
    X = Dropout(0.8)(X)                                         # dropout (use 0.8)
    X = BatchNormalization()(X)                                 # Batch normalization

    X = GRU(units = 128, return_sequences = True)(X)            # GRU (use 128 units and return the sequences)
    X = Dropout(0.8)(X)                                         # dropout (use 0.8)
    X = BatchNormalization()(X)                                 # Batch normalization
    X = Dropout(0.8)(X)                                         # dropout (use 0.8)

    X = TimeDistributed(Dense(1, activation = "sigmoid"))(X)    # time distributed  (sigmoid)

    model = Model(inputs = X_input, outputs = X)
    return model  





# # Test
def postprocessing(outputs, th):
    for output in outputs:
        output[output<th] = 0
        output[output>=th] = 1
    return outputs



if __name__=="__main__":
    # data check
    audio_dir = os.path.join('.','data','train_audios')
    wav_file = 'mix_0.wav'
    fullname = os.path.join(audio_dir, wav_file)

    x = graph_spectrogram(fullname)
    _, data = get_wav_info(fullname)
    print("Time steps in audio recording before spectrogram", data.shape)
    print("Time steps in input after spectrogram", x.shape)

    librosa.display.specshow(x, sr=44100, x_axis='time', y_axis='mel')

    n_freq = 128 # 스펙토그램 높이
    
    
    # data loader
    data_dir = os.path.join('.','data', 'XY_train')
    x_s = []
    y_s = []
    for file in os.listdir(data_dir):
        if file.startswith('x_'):
            x_s.append(os.path.join(data_dir,file))
        elif file.startswith('y_'):
            y_s.append(os.path.join(data_dir,file))
        x_s = sorted(x_s)
        y_s = sorted(y_s)
    df = pd.DataFrame({'x':x_s, 'y':y_s})
    df.head()

    train_ratio = 0.8
    idxs = list(range(len(df)))
    np.random.shuffle(idxs)
    train_idx = idxs[:int(len(df)*train_ratio)]
    valid_idx = idxs[int(len(df)*train_ratio):]

    train_df = df.loc[train_idx]
    valid_df = df.loc[valid_idx]

    print(train_df.shape, valid_df.shape)

    data_dir = os.path.join('.','data', 'XY_test')
    x_s = []
    y_s = []
    for file in os.listdir(data_dir):
        if file.startswith('x_'):
            x_s.append(os.path.join(data_dir,file))
        elif file.startswith('y_'):
            y_s.append(os.path.join(data_dir,file))
        x_s = sorted(x_s)
        y_s = sorted(y_s)
    test_df = pd.DataFrame({'x':x_s, 'y':y_s})
    test_df.head()
    
    train_generator = DataGenerator(train_df, 5)
    valid_generator = DataGenerator(valid_df, 5)
    test_generator = DataGenerator(test_df, 3)
    
    
    # train
    model = make_model(input_shape = (None, n_freq))
    model.summary()
    opt = Adam(lr=0.00001, beta_1=0.9, beta_2=0.999, decay=0.01)
    model.compile(loss='binary_crossentropy', optimizer=opt, metrics=["accuracy"])
    model.fit_generator(generator=train_generator,
                        validation_data=valid_generator,
                        epochs = 10)
    
    # test
    for batch in test_generator:
        x, y = batch
        output = model.predict(x)
        output = postprocessing(output,0.6)
        for i in range(len(y)):
            plt.plot(y[i], label='true')
            plt.plot(output[i], label='predict')
            plt.legend()
            plt.show()