import tensorflow as tf

# Encoder Decoder network

class Encoder(tf.keras.Model):
  def __init__(self, lstm_units, embedding_size, vocab_size):
    """
      Parameters: 
          lstm_size - number of lstm units
          embedding_size - size of embedding layer
          vocab_size - size of vocabulary for input language
    """

    super(Encoder, self).__init__()

    self.units = lstm_units
    self.embeding_layer = tf.keras.layers.Embedding(vocab_size, embedding_size, mask_zero=True, trainable=True)
    self.lstm_layer = tf.keras.layers.LSTM(units, dropout=0.2, return_sequences=True, return_state=True)
  
  def call(self, sequences, lstm_states, training_mode):
    """
      Parameters:
        sequences - tokenized input sequence of shape [batch_size, seq_max_len]
        lstm_states - hidden states of encoder lstm layer of shape 2*[batch_size, lstm_size].
                        Can be get from init_states method of encoder
        training_mode - are we in training or prediction mode. It`s important for dropouts present in lstm_layer
      
      Returns:
        encoder_out - encoder output states for all timesteps of shape [batch_size, seq_max_len, lstm_size]
        state_h, state_c - hidden states of lstm_layer of shape 2*[batch_size, lstm_size]
    """

    # sequences shape = [batch_size, seq_max_len]
    # lstm_states = [batch_size, lstm_size] x 2
    # encoder_embedded shape = [batch_size, seq_max_len, embedding_size]
    # encoder_out shape = [batch_size, seq_max_len, lstm_size]
    # state_h, state_c shape = [batch_size, lstm_size] x 2

    encoder_embedded = self.embeding_layer(sequences, training=training_mode)
    #print("encoder_embedded = ", encoder_embedded.shape)
    encoder_out, state_h, state_c = self.lstm_layer(encoder_embedded, initial_state=lstm_states, training=training_mode)

    return encoder_out, state_h, state_c

  def init_states(self, batch_size):
        return (tf.zeros([batch_size, self.units]),
                tf.zeros([batch_size, self.units]))

class Decoder(tf.keras.Model):
  def __init__(self, lstm_size, embedding_size, vocab_size):
    """
      Parameters: 
          lstm_size - number of lstm units
          embedding_size - size of embedding layer
          vocab_size - size of vocabulary for output language
    """

    super(Decoder, self).__init__()

    self.embedding_layer = tf.keras.layers.Embedding(vocab_size, embedding_size)
    self.lstm_layer = tf.keras.layers.LSTM(units, dropout=0.2, return_sequences=True,
                                           return_state=True)
    self.dense_layer = tf.keras.layers.Dense(vocab_size)
  
  def call(self, sequences, lstm_states, training_mode):
    """
      Parameters:
        sequences - tokenized input sequence of shape [batch_size, seq_max_len]
        lstm_states - hidden states of encoder lstm layer of shape 2*[batch_size, lstm_size].
                        Can be get from init_states method of encoder
        training_mode - are we in training or prediction mode. It`s important for dropouts present in lstm_layer
      
      Returns:
        output_vector - output for given timestep of shape [batch_size, vocab_size]
        state_h, state_c - hidden states of lstm_layer of shape 2*[batch_size, lstm_size]
    """

    # sequences shape = [batch_size, seq_max_len]
    # embedding shape = [batch_size, seq_max_len, embedding_size]
    # output shape = [batch_szie, seq_max_len, lstm_size]
    # state_h, state_c = [batch_size, lstm_size] x2
    # dense shape = [batch_size, seq_max_len, vocab_size]
    
    decoder_embedded = self.embedding_layer(sequences, training=training_mode)
    lstm_output, state_h, state_c = self.lstm_layer(decoder_embedded, lstm_states, training=training_mode)
    return self.dense_layer(lstm_output), state_h, state_c

def test_encoder_decoder_shapes():
    # checks for encoder state
    vocab_size = len(en_tokenizer.word_index)+1
    fr_vocab_size = len(fr_tokenizer.word_index)+1
    batch_size = 1
    encoder = Encoder(vocab_size, EMBEDDING_SIZE, LSTM_SIZE)

    source_input = tf.constant([[1, 7, 59, 43, 55, 6, 10, 10]])
    initial_state = encoder.init_states(batch_size)
    encoder_output, en_state_h, en_state_c = encoder(source_input, initial_state)
    
    decoder = Decoder(fr_vocab_size, EMBEDDING_SIZE, LSTM_SIZE)
    decoder_input = tf.constant([[1,2,3,4,5]])
    decoder_output, de_state_h, de_state_c = decoder(decoder_input, [en_state_h, en_state_c])

    assert(decoder_output.shape == (*decoder_input.shape, fr_vocab_size))
    assert(de_state_h.shape == (batch_size, LSTM_SIZE))
    assert(de_state_c.shape == (batch_size, LSTM_SIZE))

    assert(encoder_output.shape == (*source_input.shape, LSTM_SIZE))
    assert(en_state_h.shape == (batch_size, LSTM_SIZE))
    assert(en_state_c.shape == (batch_size, LSTM_SIZE))