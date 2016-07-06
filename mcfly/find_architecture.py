import numpy as np
from matplotlib import pyplot as plt
from . import modelgen
# Summary:
# Function generate_models from modelgen.py generates and compiles models
# Function train_models_on_samples trains those models
# Function plotTrainingProcess plots the training process
# Function find_best_architecture is wrapper function that combines
# these steps
# Example function calls in 'EvaluateDifferentModels.ipynb'
def train_models_on_samples(X_train, y_train, X_val, y_val, models,
                            nr_epochs=5, subsize_set=100, verbose=True):
    #<= subsize_set maybe needs to be a percentage or at least a check that
    # value is feasible
    '''
    Given a list of compiled models, this function trains
    them all on a subset of the train data
    Parameters
    ----------
    X_train : numpy array of shape (num_samples, num_timesteps, num_channels)
        The input dataset for training
    y_train : numpy array of shape (num_samples, num_classes)
        The output classes for the train data, in binary format
    X_val : numpy array of shape (num_samples_val, num_timesteps, num_channels)
        The input dataset for validation
    y_val : numpy array of shape (num_samples_val, num_classes)
        The output classes for the validation data, in binary format
    models : list of model, params, modeltypes
        List of keras models to train
    nr_epochs : int, optional
        nr of epochs to use for training one model
    subsize_set : int, optional
        number of samples to use from the training set for training these models
    verbose : bool, optional
        flag for displaying verbose output

    Returns
    ----------
    histories : list of Keras History objects
        train histories for all models
    val_accuracies : list of floats
        validation accuraracies of the models
    val_losses : list of floats
        validation losses of the models
    '''
    nr_epochs = 5 #<= this line should be omitted as it overwrites args!
    X_train_sub = X_train[:subsize_set, :, :]
    y_train_sub = y_train[:subsize_set, :]

    histories = []
    val_accuracies = []
    val_losses = []
    for model, params, model_types in models:
        history = model.fit(X_train_sub, y_train_sub,
                            nb_epoch=nr_epochs, batch_size=20, #<= see comment on subsize_set
                            validation_data=(X_val, y_val),
                            verbose=verbose)
        histories.append(history)
        val_accuracies.append(history.history['val_acc'][-1])
        val_losses.append(history.history['val_loss'][-1])

    return histories, val_accuracies, val_losses


def plotTrainingProcess(history, name='Model', ax=None):
    # text made specific to one model
    '''
    This function plots the loss and accuracy on the train and validation set,
    for each epoch in the history of one model.

    Parameters
    ----------
    history : keras History object for one model
        The history object of the training process corresponding to one model
    Returns
    ----------

    '''
    if ax is None:
        fig, ax = plt.subplots()
    ax2 = ax.twinx()
    LN = len(history.history['val_loss'])
    val_loss, = ax.plot(range(LN), history.history['val_loss'], 'g--',
                        label='validation loss')
    train_loss, = ax.plot(range(LN), history.history['loss'], 'g-',
                          label='train loss')
    val_acc, = ax2.plot(range(LN), history.history['val_acc'], 'b--',
                        label='validation accuracy')
    train_acc, = ax2.plot(range(LN), history.history['acc'], 'b-',
                          label='train accuracy')
    ax.set_xlabel('epoch')
    ax.set_ylabel('loss', color='g')
    ax2.set_ylabel('accuracy', color='b')
    plt.legend(handles=[val_loss, train_loss, val_acc, train_acc],
               loc=2, bbox_to_anchor=(1.1, 1))
    plt.title(name)


def find_best_architecture(X_train, y_train, X_val, y_val, verbose=True,
                           number_of_models=5, **kwargs):
    '''
    Tries out a number of models on a subsample of the data,
    and outputs the best found architecture and hyperparameters.

    Parameters
    ----------
    X_train : numpy array of shape (num_samples, num_timesteps, num_channels)
        The input dataset for training
    y_train : numpy array of shape (num_samples, num_classes)
        The output classes for the train data, in binary format
    X_val : numpy array of shape (num_samples_val, num_timesteps, num_channels)
        The input dataset for validation
    y_val : numpy array of shape (num_samples_val, num_classes)
        The output classes for the validation data, in binary format
    verbose : bool, optional
        flag for displaying verbose output
    **kwargs: key-value parameters
        parameters for generating the models

    Returns
    ----------
    best_model : Keras model
        Best performing model, already trained on a small sample data set.
    best_params : dict
        Dictionary containing the hyperparameters for the best model
    best_model_type : str
        Type of the best model
    '''
    models = modelgen.generate_models(X_train.shape, y_train.shape[1],
                                      number_of_models=number_of_models,
                                      **kwargs)
    histories, val_accuracies, val_losses = train_models_on_samples(X_train,
                                                                    y_train,
                                                                    X_val,
                                                                    y_val,
                                                                    models,
                                                                    verbose=verbose)
    best_model_index = np.argmax(val_accuracies)
    best_model, best_params, best_model_type = models[best_model_index]
    if verbose:
        for i in range(len(models)): #<= now one plot per model, ultimately we
            # may want all models in one plot to allow for direct comparison
            name = str(models[i][1])
            plotTrainingProcess(histories[i], name)
        print('Best model: model ', best_model_index)
        print('Model type: ', best_model_type)
        print('Hyperparameters: ', best_params)
        print('Accuracy on train set: ', val_accuracies[best_model_index])
    return best_model, best_params, best_model_type