from copy import deepcopy
import numpy as np
from network import Network
import pickle

class Optimizer:
    def __init__(self, network, loss_function):
        self.network = network
        self.loss_function = loss_function

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network):
        if getattr(self, '_network', None) is not network:
            self._network = network
            self.reset()

    def step(self, training_input, expected_output):
        """Perform a forward pass through the network, compute the loss and gradients, and accumulate them"""

        predicted = self.network.forward(training_input)
        self.loss_sum += self.loss_function.loss(predicted=predicted, expected=expected_output)
        loss_func_gradient = self.loss_function.gradient(self.network.last_output, expected_output)
        gradients = self.network.gradients(loss_func_gradient)
        
        if self.gradient_sum is not None:
            # Accumulate gradients if this is not the first step
            for j, grad in enumerate(gradients):
                self.gradient_sum[j] += grad
        else:
            # Initialize the gradient sum if this is the first step
            self.gradient_sum = gradients

        self.num_steps += 1

    def optim(self, learning_rate, regularization_parameter):
        """Perform the optimization step, updating the filters and output weights in the network"""

        if self.num_steps == 0:
            return

        gradient_sum_multiplier = learning_rate / self.num_steps
        regularization_term = np.sum(self.network.output_weights * self.network.output_weights) * regularization_parameter / 2

        # Perform gradient descent on all layers except the output layer
        for j, layer in enumerate(self.network.layers):
            layer.gradient_descent(gradient_sum_multiplier * self.gradient_sum[j])
        
        # Update the output weights using L2 regularization
        self.network.output_weights *= 1 - learning_rate * regularization_parameter
        self.network.output_weights -= gradient_sum_multiplier * self.gradient_sum[-1] 

        # Compute the total loss and reset the optimizer for the next iteration
        loss = self.loss_sum / self.num_steps + regularization_term
        self.reset()

        return loss

    def reset(self):
        """Reset the optimizer for the next iteration"""

        self.loss_sum = 0
        self.gradient_sum = None
        self.num_steps = 0

    def save_to_file(self, file):
        if isinstance(file, str):
            with open(file, "wb") as f:
                return self.save_to_file(f)
        
        self.network.save_to_file(file)
        pickle.dump(
            (
                self.loss_function,
                self.loss_sum,
                self.gradient_sum,
                self.num_steps
            ), 
            file
        )

    @staticmethod
    def load_from_file(file):
        if isinstance(file, str):
            with open(file, "rb") as f:
                return Optimizer.load_from_file(f)
        
        network = Network.load_from_file(file)
        (
            loss_function,
            loss_sum,
            gradient_sum,
            num_steps
        ) = pickle.load(file)

        optimizer = Optimizer(network, loss_function)
        optimizer.loss_sum = loss_sum
        optimizer.gradient_sum = gradient_sum
        optimizer.num_steps = num_steps
        return optimizer